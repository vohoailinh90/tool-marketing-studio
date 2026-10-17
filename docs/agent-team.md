# The agent team for this repository

Three lanes can develop the engine and the app. The tier is decided the same way in all
of them — classify, then `scripts/route.py` (see `CLAUDE.md`). The lane is the owner's choice.

## 1. Claude subagents (default)

`.claude/agents/`: `architect`, `architecture-critic`, `requirement-analyst`, `implementer`,
`code-reviewer`, `code-reviewer-t3`, `code-reviewer-verify`, `test-engineer`. The main session
analyses, designs and implements; subagents supply independent judgement, inside the budget
`scripts/route.py --record` writes and `scripts/hooks/agent_budget.py` enforces (hooks are
enabled in `.claude/settings.json`).

```bash
python3 scripts/route.py --dimensions 1,1,1,1,0,1 --record --requirement REQ-001
```

## 2. Codex lane

Codex Cloud designs and writes, a separate `@codex review` critiques, the main session
orchestrates and validates. Protocol: `docs/claude-to-codex.md` (read it in full before any
`@codex` comment), `docs/codex-lane.md`, `.claude/skills/codex-lane/SKILL.md`,
`scripts/codex_task.py`, `scripts/codex_round_count.py`.

```bash
python3 scripts/route.py --dimensions 1,2,1,1,1,1 --lane codex --record --requirement REQ-002
```

## 3. Free-model team on the VPS

Installed once on the VPS from `claude-agent-routing-template` (`docs/vps-team.md` there):
Claude writes the spec and audits; free models write tests, code and a pre-review in
containers; `team.py` runs the gates. It targets any repository, so for this one:

1. Add a deploy key for the VPS `team` user (Settings → Deploy keys, write access), and keep
   branch protection on `main`.
2. In `/srv/team/team.env` on the VPS, gates for this repository need its Python packages:

   ```
   TEAM_GATES_SETUP="python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt && .venv/bin/python -m playwright install chromium"
   ```
3. Start a feature: `team new F1 --repo git@github.com:vohoailinh90/tool-marketing-studio.git`,
   write `request.md`, let Claude write `spec.md` / `tasks.md` / `acceptance.md`. Acceptance
   for this repository is at least:

   ```
   .venv/bin/python -m pytest -q
   .venv/bin/python studio.py check
   .venv/bin/python scripts/i18n_check.py
   .venv/bin/python scripts/layout_check.py
   .venv/bin/python scripts/mutation_check.py --all
   ```
   A change under `web/src` also needs `cd web && npm ci && npm run build` and the rebuilt
   `web/dist` committed.

Never give the VPS workers the app's `.env` (Page token, Anthropic key): the gates need none.

## CI runner

`.github/workflows/ci.yml` and `radar-preview.yml` run on `${{ vars.CI_RUNNER || 'ubuntu-latest' }}`: a
GitHub-hosted runner by default. The repository is public, so those minutes are free; a private repository would
be billed, and without minutes a job on `ubuntu-latest` fails at once with no log.

Until 2026-10-17 the default was `self-hosted`: two runners on the owner's VPS
(`tool-marketing-studio-runner` and `tool-marketing-studio-runner-2`), added because one runner left the queue
hours long. Both were removed when the repository went public and `CI_RUNNER=ubuntu-latest` was set, so nothing
serves the `self-hosted` label now. Once this default is merged, that variable is redundant: delete it (Settings →
Secrets and variables → Actions → Variables) or leave it, the result is the same.

- Move every job to another runner: set the repository variable `CI_RUNNER` to its label (Settings →
  Secrets and variables → Actions → Variables). Delete it to come back to `ubuntu-latest`.
- The `engine` job is `pytest -q` (about 17 minutes on `ubuntu-latest`) plus `mutation_check.py --all`, which is most of
  the job (about 35 minutes with two workers): it runs every entry of `tests/mutations/` (over a thousand), so its
  time grows with each fix that ships a mutation. The step starts `MUTATION_JOBS` workers (repository variable, a whole
  number from 1; default 2), each mutating its own copy of the tree under `$RUNNER_TEMP`; raise it only after timing the
  step in a run's log before and after, and set it to 1 for the old single-tree run. A pull request that changes only
  the System Design store skips the check: `scripts/ci_changes.py` decides, and every push to `main` still runs it.
- A GitHub-hosted runner is a fresh machine for every job, so Chromium's system libraries are installed by the job
  itself (`playwright install --with-deps`, only when `runner.environment == 'github-hosted'`).
- Going back to a self-hosted runner (for example a VPS again) is a choice with a cost on a public repository: a
  persistent runner keeps its files between jobs, so it must run only code from people who can push here. Every job
  already skips a pull request whose branch lives in a fork for that reason (`tests/test_codex_review.py` checks it);
  keep that guard, and read GitHub's advice on self-hosted runners for public repositories before registering one.
  To register one: as the user that will own it, download and unpack the runner from this repository → Settings →
  Actions → Runners → New self-hosted runner (the token expires in about an hour, never write it in a file), run
  `./config.sh --url https://github.com/vohoailinh90/tool-marketing-studio --token <token> --name <name> --unattended`,
  then, as root in that folder, `./svc.sh install <user> && ./svc.sh start`; set `CI_RUNNER` to a label the runner has
  (`self-hosted` matches any). To remove one: `./svc.sh stop`, `./svc.sh uninstall`, then
  `./config.sh remove --token <removal token>`.
- A personal account's self-hosted runner belongs to one repository: a runner registered for another repository does
  not serve this one.
- On a VPS, install Chromium's system libraries once so the render test runs instead of skipping:
  `sudo python3 -m playwright install-deps chromium`.

## Radar preview

github-radar opens a **draft pull request** on branch `radar/<campaign>` for each scan (it adds
`campaigns/radar-<date>[-n]/` and `tools/github-radar/`). `.github/workflows/radar-preview.yml` looks at it for you:

- it runs `studio.py check` and then `studio.py render` on that campaign with this repository's engine; the drawing runs only
  when the check passed, because `render` revalidates the posts and not the tool brief (a `brand.accent` that is CSS would
  reach the page, which may load local images into the uploaded screenshots);
- it attaches the PNGs, the platform texts and the manifests to the run (artifact `radar-preview-pr-<number>`, kept
  14 days) and keeps **one comment** on the pull request with the slide count, the slides that overflow, the
  Facebook caption and a link to the artifact (edited in place on every push). The comment is budgeted to stay under the
  size GitHub accepts: captions past the budget and table rows past theirs are left out with a note, and the files stay in the artifact;
- it never approves, publishes, commits or pushes: reading the images, `studio.py approve` and publishing stay the owner's.

The engine of a pull request is code that would run on the shared runner, so `scripts/radar_preview.py` first lists the
files the pull request changed (against the base as it is now, the first parent of GitHub's merge commit) and draws it only
when every one is under `campaigns/radar-*/` or `tools/github-radar/` and none is, or sits under, a symbolic link; otherwise
the comment says which files are the problem and nothing runs. The planner and the comment writer run from the **base commit** (read with `git show` into the runner's
temp folder, not checked out into the workspace, where a symbolic link of the pull request could steer the checkout), so a
pull request that edits or deletes them is judged by the version on the base branch. That is still not a boundary against
someone who can already push a branch here: GitHub runs the workflow file of the pull request's merge, so that person can
edit the workflow itself, which runs on the same runner, exactly as with `ci.yml`.
Only branches of this repository named `radar/...` are drawn (never a fork), the token can write pull-request comments
and nothing else (and is not kept in `.git/config`), and no pull-request value is written into a script. The job is a
few minutes and waits in the same runner queue as `ci.yml` (`CI_RUNNER` moves both). Tests: `tests/test_radar_preview.py`; mutations: `tests/mutations/radar_preview*.yaml`.
