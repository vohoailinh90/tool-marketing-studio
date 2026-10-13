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

`.github/workflows/ci.yml` runs on `${{ vars.CI_RUNNER || 'self-hosted' }}`: the two VPS runners
registered for this repository (`tool-marketing-studio-runner` and
`tool-marketing-studio-runner-2`, both with labels `self-hosted`, `Linux`, `X64`). This
repository is private, so GitHub-hosted minutes are billed; without minutes a job on
`ubuntu-latest` fails at once with no log.

- Move every job to GitHub-hosted runners: set the repository variable `CI_RUNNER=ubuntu-latest`
  (Settings → Secrets and variables → Actions → Variables). Delete it to come back.
- A personal account's self-hosted runner belongs to one repository: the runner that serves
  `claude-agent-routing-template` does not serve this one, which is why it has its own.
- On the VPS, install Chromium's system libraries once so the render test runs instead of
  skipping: `sudo python3 -m playwright install-deps chromium`.
- Each runner takes one job at a time, so two jobs run at once. `engine` takes about 30 minutes,
  27 of them in `mutation_check.py --all`. A pull request that changes only the System Design
  store skips that check: `scripts/ci_changes.py` decides, and every push to `main` still runs it.
- The second runner was added on 2026-10-13 because one runner left the queue hours long. Both
  live on the same VPS, under the `ci-runner` user, one folder each:
  `/home/ci-runner/actions-runner-tool-marketing-studio` and `...-2`, each its own systemd
  service (`actions.runner.vohoailinh90-tool-marketing-studio.<runner name>.service`). That VPS
  has 4 CPU cores and about 7.6 GiB of RAM and also serves the runners of the owner's other
  repositories, so do not add a third without watching memory and swap (`free -h`) while two
  `engine` jobs run.
- To add a runner: as `ci-runner`, copy a working runner folder, delete `_work`, `_diag`,
  `.runner`, `.runner_migrated`, `.credentials*`, `.service` and the downloaded `.tar.gz` from the
  copy, register it with a fresh token (this repository → Settings → Actions → Runners → New
  self-hosted runner; the token expires in about an hour, never write it in a file) using
  `./config.sh --url https://github.com/vohoailinh90/tool-marketing-studio --token <token>
  --name <new name> --unattended`, then, as root in that folder,
  `./svc.sh install ci-runner && ./svc.sh start`. To remove one: `./svc.sh stop`,
  `./svc.sh uninstall`, then `./config.sh remove --token <removal token>` as `ci-runner`.
- The VPS keeps its files between jobs, so it runs only code from people who can push to this
  repository: every job skips a pull request whose branch lives in a fork. Keep the repository
  private, or keep that guard, while CI runs on the VPS (`tests/test_codex_review.py` checks it).

## Radar preview

github-radar opens a **draft pull request** on branch `radar/<campaign>` for each scan (it adds
`campaigns/radar-<date>[-n]/` and `tools/github-radar/`). `.github/workflows/radar-preview.yml` looks at it for you:

- it runs `studio.py check` and `studio.py render` on that campaign with this repository's engine;
- it attaches the PNGs, the platform texts and the manifests to the run (artifact `radar-preview-pr-<number>`, kept
  14 days) and keeps **one comment** on the pull request with the slide count, the slides that overflow, the
  Facebook caption and a link to the artifact (edited in place on every push);
- it never approves, publishes, commits or pushes: reading the images, `studio.py approve` and publishing stay the owner's.

The engine of a pull request is code that would run on the shared runner, so `scripts/radar_preview.py` first lists the
files the pull request changed (against the base as it is now, the first parent of GitHub's merge commit) and draws it only
when every one is under `campaigns/radar-*/` or `tools/github-radar/` and none is, or sits under, a symbolic link; otherwise
the comment says which files are the problem and nothing runs. That is a safety net for a bot branch that carries code by
accident, not a boundary against someone who can already push a branch here: that person can edit the workflow itself, which
runs on the same runner, exactly as with `ci.yml`. Only branches of this repository named `radar/...` are drawn (never a
fork), the token can write pull-request comments and nothing else (and is not kept in `.git/config`), and no
pull-request value is written into a script. The job is a few minutes and waits in the same runner queue as `ci.yml`
(`CI_RUNNER` moves both). Tests: `tests/test_radar_preview.py`; mutations: `tests/mutations/radar_preview*.yaml`.
