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

`.github/workflows/ci.yml` runs on `${{ vars.CI_RUNNER || 'self-hosted' }}`: the VPS runner
registered for this repository (`tool-marketing-studio-runner`, labels `self-hosted`, `Linux`,
`X64`). This repository is private, so GitHub-hosted minutes are billed; without minutes a job
on `ubuntu-latest` fails at once with no log.

- Move every job to GitHub-hosted runners: set the repository variable `CI_RUNNER=ubuntu-latest`
  (Settings → Secrets and variables → Actions → Variables). Delete it to come back.
- A personal account's self-hosted runner belongs to one repository: the runner that serves
  `claude-agent-routing-template` does not serve this one, which is why it has its own.
- On the VPS, install Chromium's system libraries once so the render test runs instead of
  skipping: `sudo python3 -m playwright install-deps chromium`.
