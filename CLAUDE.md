# Tool Marketing Studio

## Purpose

This repository markets the owner's software tools and measures demand for them before
they are commercialised. It holds:

- **Content**: per tool, a fact brief and a positioning per language; per campaign, posts
  written **separately and completely** in Vietnamese, Japanese and English (never a
  sentence-by-sentence translation), rendered into explanatory images.
- **The engine** (`mkt/`, CLI `studio.py`): checks, rendering, approvals, publishing,
  posting history, feedback, metrics and AI drafting/insights.
- **The app** (`app.py` + `web/`): a local web UI built from the Automation UI Kit on a
  FastAPI server bound to 127.0.0.1.
- **The agent office** (`office/` + `scripts/office/`): a read-only page that shows which
  agent is doing what, from the hook log, the agent budget ledger and the VPS team's
  `state.json`; see `docs/office-dashboard.md`.

Development of the engine and the app follows the routing and agent-team rules below,
inherited from `vohoailinh90/claude-agent-routing-template`. The three lanes that can do
the work — Claude subagents, Codex, and the free-model team on the VPS — and how CI picks
its runner are in `docs/agent-team.md`. Writing marketing content is
not a routed software requirement: follow `.claude/skills/tool-campaign/SKILL.md`.

Your primary job is to select the lowest-cost profile that safely handles a requirement,
not to maximise the number of agents.

## Routing source of truth

- Routing policy: `agent-routing/policy.yaml`
- Scoring rubric: `agent-routing/complexity-rubric.md`
- Requirement classifier: `.claude/skills/classify-requirement/SKILL.md`

Do not invent a different tier model unless the user explicitly asks to change the policy.

## Mandatory routing flow

For non-trivial feature/change requests:

1. Understand the requirement and inspect relevant repository context when available.
2. Score the six dimensions defined by the rubric.
3. Extract domain/risk signals as **actions the change performs**, never as nouns the requirement mentions. A read-only signal from `signal_taxonomy.read_only_exempt` never feeds an override.
4. Run `scripts/route.py` on the scores and signals. It applies the overrides, selects the profile, fires the conditional agents and adds up the budget from `agent-routing/policy.yaml`; do not apply those rules by hand.
5. When the session will execute the requirement, run it again with `--record` so the agent budget is enforced (below).
6. Execute only the roles required by that profile, staying inside `budget.max_agent_invocations`.
7. Verify independently before declaring success.
8. If the work ships as a pull request, run it through *Pull request lifecycle* (below): Codex review until clean, merge, then the next task.

The semantic analysis may be probabilistic; policy enforcement must not be — which is why steps 4–5 are a script and a hook, not instructions to the model. See `docs/agent-budget.md`.

## Execution profiles

### T0 — trivial

Use the main session only. Do not spawn subagents unless the requirement unexpectedly reveals additional risk or scope.

Good examples: copy changes, typo fixes, obvious local validation, tiny isolated refactors.

Agent budget: **0**.

### T1 — standard

The main session implements. One subagent verifies:

- `code-reviewer`

Do not spawn a separate `implementer` — the main session already holds the requirement and the code, and handing it to a subagent buys nothing except a second context that must rebuild both. The reviewer must inspect the resulting diff independently; the session that wrote the code cannot be its own only verification.

Agent budget: **1**.

### T2 — complex

The main session analyzes, designs and implements, recording its plan as an artifact. Then:

- `code-reviewer` — reviews the diff **and** independently verifies behavior (this is the combined review/test role)
- `architect` — **only** when the architecture dimension scored 2, or a signal in the profile's `when_any_signal` list fires (`changes-service-contract`, `changes-event-contract`, `changes-storage-ownership`, `changes-canonical-model`). These are two independently-sufficient conditions (OR, never AND) — either alone fires the architect — and both are machine-checkable on purpose: a condition the classifier cannot evaluate is prose, not policy.

An architect agent that would restate a design the main session can already state is not worth a context. Spawn it when the design genuinely needs authoring by someone not already committed to an implementation path.

Agent budget: **2** by default, plus a reserved invocation for verification escalation described below.

### T3 — critical

The main session analyzes, designs and implements. Two subagents supply what it cannot supply for itself:

- `architecture-critic` — challenges the main session's design before implementation
- `code-reviewer-t3` — the T3 variant of `code-reviewer` (16 turns, high effort instead of 12/medium): it reviews the diff and independently verifies behavior, and the combined remit does not fit the standard budget on payment/auth/migration-scale work without review crowding out verification

Critique is **one round** by default. A second round is allowed only when round 1 left unresolved critical or high findings, and it must **resume the round-1 critic**, never spawn a new one. A fresh critic re-reads the requirement, the design and the diff from zero, so a spawned round 2 costs more than round 1 did; a resumed one costs the delta.

`requirement-analyst` fires **conditionally**, not by default: when the requirement scores ambiguity `2`, invoke it before architecture begins. The critic reviews a design the main session already authored; the analyst is what keeps an open product decision from silently becoming a technical assumption before that design is written, and the critic cannot structurally substitute for it. `architect`, `implementer`, `test-engineer` and `code-reviewer-verify` remain available for escalation only.

Before implementation, resolve high-severity architecture objections. Escalate to the user only for a genuine blocker (the task cannot proceed without a decision only a human can make) or a change to the original requirement — including for irreversible or destructive changes. See `docs/claude-to-codex.md` §20 for the standing autonomous-completion-and-merge policy.

Agent budget: **3** by default (critic, reviewer, and one slot for a resumed critique round), **4** when ambiguity `2` fires the conditional `requirement-analyst`, plus a reserved invocation described below that either case may additionally earn.

A T3 worst case spends all three base slots on critique alone — critic, resumed critic, reviewer. A T2 worst case spends both base slots the same way, on the conditional architect plus the reviewer. In either case, if that reviewer then escalates because verification needs its own design work, that escalation would be a forbidden extra invocation and the requirement could never reach its own definition of done. `budget.escalation_reserve` grants exactly one additional invocation for that path at T2 and T3, available only to `test-engineer` and only after the reviewer has formally reported that verification needs designing. It may not be spent on another critique round, and it does not exist at T0-T1 — T0 does no independent verification, and T1's risk domains are already forced to T2+ by the policy overrides, so no T1 case can produce the finding this reserve exists to unblock. `budget.analyst_reserve` is the T3-only equivalent for the ambiguity-2 path — it fires before review even starts, so the two reserves are independent and a T3 requirement that is both ambiguous and later found to need designed verification can spend both (3 base + 1 analyst + 1 escalation = 5). Report base and reserve consumption separately rather than as one number.

### Codex lane (T1–T3)

The profiles above are the **claude lane**, the default. The **codex lane**
(`lanes.codex` in `agent-routing/policy.yaml`, `docs/codex-lane.md`) executes
the same tier with Codex Cloud: Codex designs and writes the code, a separate
`@codex review` run critiques it, and the main session orchestrates through
`docs/claude-to-codex.md` and validates every result per its §14. A Codex step
that `replaces` a Claude agent runs exactly when the claude lane would require
that agent, so the roster shrinks without restating any condition: T1 and T2
spawn no Claude subagent (budget **0**); T3 keeps `code-reviewer-t3` for the
verification a diff review cannot run (budget **1**, plus the same reserves).

The lane is the operator's choice — `scripts/route.py ... --lane codex` — never
the classifier's, and it never changes the tier, an override or a reserve. T0
has no codex lane. Run it with `.claude/skills/codex-lane/SKILL.md`; every task
comment it posts is rendered by `scripts/codex_task.py`, which refuses a
duplicate, a skipped round, a round past its cap, a second request of one mode
at one SHA, or a thread with a request still unanswered. When Codex is blocked, re-record the requirement in the
claude lane under the same label; that moves who does the work and never waives the PR's Codex review (*Pull request lifecycle*).

## Agent budget

`budget.max_agent_invocations` in `agent-routing/policy.yaml` is a ceiling, not a target. It counts every subagent invocation for the requirement — resumed agents included, and anything a subagent itself spawns.

It is enforced, not advised: `scripts/route.py --record` writes the requirement's ledger to `artifacts/handoff/agent-budget.json`, and `scripts/hooks/agent_budget.py` (a `PreToolUse` hook matching `Agent|Task`, the spawn tool's name across Claude Code releases, wired in `.claude/settings.example.json`) charges every spawn to the base or to a reserve granted for that agent and refuses the one past the ceiling. A resumed agent is a message rather than a spawn, so charge it by hand with `agent_budget.py charge`; a reviewer's formal escalation is granted with `agent_budget.py grant escalation_reserve --agent test-engineer`. Details in `docs/agent-budget.md`.

Reaching the ceiling with work outstanding is an escalation signal. Report the partial result and the remaining risk; do not spawn past the cap because the work felt unfinished. The one exception is `budget.escalation_reserve` at T2 and T3, under the condition stated there. Parallelism changes when agents run, never how many: independent tracks do not raise the budget.

## Session budget

The agent budget caps how many contexts a requirement builds. It says nothing
about the one context that always exists: the session itself. A run that dies
mid-requirement — auto-compaction, or a rate limit — and is restarted from
scratch costs several times what finishing it would have, and the reasons are
structural rather than incidental:

- **The prompt cache goes cold.** A live session re-reads its history at roughly
  0.1x input price; a cold restart pays full price *plus* a cache write. That is
  the single largest multiplier, and a rate-limit wait guarantees it.
- **Turn cost is quadratic.** Every turn resends the whole conversation, so
  reaching the same depth twice costs the integral twice.
- **Re-derivation is the expensive part.** The reading, grepping and test runs
  that produced the session's conclusions are gone; the conclusions go with them.
- **Subagent contexts do not survive at all.** A T3 requirement that dies after
  three invocations rebuilds all three. Only what reached disk survives.

So treat the session like the roster: bounded, and instrumented.

`scripts/hooks/session_budget.py` and `scripts/hooks/statusline.py` are wired in
`.claude/settings.example.json`. Copy it to `.claude/settings.json` to enable
them; `docs/session-budget.md` documents the thresholds and the payload fields
they read.

### Handoff protocol

`artifacts/handoff/SESSION-HANDOFF.md` is the session's equivalent of the
artifact protocol: the stable output a restart reads instead of rebuilding. It
holds two blocks, and the split is the point.

- **`auto-state`** is regenerated on every capture from git and the transcript —
  branch, HEAD, uncommitted paths, diffstat, recent commits, context occupancy,
  the last request. All of it computable, none of it judgement, per
  *Deterministic work is not agent work* below.
- **`model-notes`** is authored by the session and preserved verbatim across
  every capture. Goal, what is done, what remains, the next command, decisions
  not worth re-litigating. A script cannot write this block, which is exactly
  why the session must.

Keep `model-notes` current whenever the work reaches a state worth resuming
from, and always when the hook asks for it (~70% of the context window) or tells
you to wrap up (~85%). Being cut off having written nothing is the failure this
protocol exists to prevent. Commit working code before that point too — a
handoff that points at an uncommitted working tree is a weaker checkpoint than
one that points at a commit.

On `SessionStart`, an existing handoff is replayed into the new session. Read it
before re-deriving anything.

## Deterministic work is not agent work

If the correct answer to a check is computable, compute it. Do not route it to a model.

This covers counting (records, rows, files, diff lines), hash/checksum/fingerprint comparison, schema and contract conformance a validator can assert, presence/expiry/referential-integrity checks over known data, and lint/format/type/test runs whose output is already a verdict.

Write a script or a CI check and commit it to the repository. A model comparing two SHA-256 values can be wrong; a script cannot. The reliability argument here is stronger than the cost argument, and the cost argument is already strong: prefer adding a check to the repository over adding a role to the roster.

**Mutation checking is the worked example.** A passing test proves nothing on its own; a test that would still pass with the behavior removed reports safety that is not there. The only thing that settles it is to break the behavior and require the test to notice — and that loop is computable: edit a file, run a test, read an exit code. It costs a reviewer three tool calls per behavior and scales with the number of behaviors, so no subagent turn ceiling can hold it, which is precisely why it is not a reason to enlarge one.

`scripts/mutation_check.py` owns that loop, driven by manifests in `tests/mutations/`. Each entry names a behavior, the edit that breaks it, and the test that must fail as a result; an entry whose `find` no longer matches exactly one site fails as drift rather than silently proving nothing. When you ship a fix with a test, add the mutation that would have caught it.

## Artifact protocol

For T2/T3, use artifacts so roles communicate through stable outputs rather than free-form debate:

- architecture proposal → `artifacts/architecture/<requirement-id>.md`
- critique → `artifacts/critiques/<requirement-id>.md`
- implementation plan → `artifacts/plans/<requirement-id>.md`
- final review → `artifacts/reviews/<requirement-id>.md`

Artifacts must record unresolved issues explicitly.

Artifacts are a compression channel, not a record of everything considered. Every downstream agent reads them, so length multiplies across the roster. `budget.max_artifact_lines` caps them: architecture 200 lines, critique 80, plan 120, review 120. An artifact over its cap must be **cut down**, not split across more files. A critique lists critical and high findings; low-severity observations belong in a closing sentence, not their own section.

## Escalation rules

Escalate to a higher tier when implementation discovers:

- hidden cross-service coupling
- auth/security implications
- schema/data migration
- irreversible operations
- distributed consistency requirements
- external dependency uncertainty
- materially harder verification than originally scored

Never downgrade below a policy override.

## Stop conditions

Do not keep agents debating until they "agree". Stop the architecture loop when:

- all critical/high objections are either accepted and addressed, or explicitly rejected with evidence;
- remaining disagreements are low severity; and
- the implementation plan has a verifiable acceptance criterion.

Maximum default architecture critique rounds: **1**. A second round requires unresolved critical/high findings and must resume the round-1 critic rather than spawning a new one. Escalate to the user instead of looping indefinitely when a critical product decision remains unresolved.

## Verification rule

Implementation is not complete because code was written. Completion requires evidence appropriate to the tier:

- T0: local sanity check, in the main session
- T1: relevant tests/lint, plus an independent diff review by `code-reviewer`
- T2: targeted tests and integration considerations, plus independent review and verification by `code-reviewer`
- T3: integration/e2e or migration/security verification as applicable, rollback consideration, plus independent review and verification by `code-reviewer-t3`

At T2 and T3 the reviewer both reads the diff and runs verification. Splitting those into two agents doubles the context cost to check one change; keep them in one role and escalate to `test-engineer` only when verification genuinely needs its own design work (failure injection, migration rehearsal, concurrency harnesses).

When a review's remit is known up front to be probe-heavy — probes that must be designed and run rather than an existing suite re-run — the reviewer slot may instead be filled by `code-reviewer-verify` (24 turns, high effort). It is a **substitution**, not an addition: it replaces `code-reviewer`/`code-reviewer-t3` in the one slot the profile already requires, so the budget is unchanged. No tier spawns it automatically, and that is deliberate: the two reviews that exhausted their ceiling here did so on mutation checking (now a script, above) and on diff size, which nothing can know at classification time. A `verification 2` trigger would have moved a third of the eval corpus onto the most expensive reviewer without evidence, which is the cost this repository exists to avoid. Registered in `escalation_only_agents` in `agent-routing/policy.yaml`.

Whatever the tier, a check whose answer is computable belongs in a script — see *Deterministic work is not agent work*.

## Delegating to Codex Cloud

`docs/claude-to-codex.md` is the only approved protocol for delegating work to Codex Cloud (the `@codex` GitHub mention). Claude must read that file in full before posting any GitHub comment that mentions `@codex`, and must follow it exactly — task contract, comment tracking marker, GitHub location rules, duplicate-call and loop prevention (how rounds are counted against the caps included), and response-validation steps included. Codex's automatic review when a PR is opened is turned off (the owner's setting, 2026-10-10): Codex never reviews a PR on its own, so request every review yourself, the first one as soon as the PR is open — never wait for an opening run. This is mandatory for every PR you create; the full loop from review to merge to the next task is *Pull request lifecycle*, below. Before every review request, `python3 scripts/codex_round_count.py` counts the review rounds and proves the PR's three lists complete (reviews have no cap since 2026-10-12, §16); request only when it exits 0. Every task comment (BRAINSTORM, IMPLEMENT, FIX) is rendered by `python3 scripts/codex_task.py render` and posted only when it exits 0. Do not invent a different Codex invocation path (API, GitHub Action, CLI, SDK, or browser automation) — the file explicitly forbids all of those.

## Pull request lifecycle

Every pull request you create or drive for a requirement goes through the loop below — at any tier, in any lane, a T0 typo fix included. It is a standing rule, not a judgement call, and a requirement never has to ask for it. The rule starts when a PR exists; it does not authorize opening one, so a PR is still opened only when the user asks for it or the flow calls for it.

1. **Open, then Codex review — immediately.** The first action after the PR exists is the Codex review. The review request of `docs/claude-to-codex.md` §11, posted only when `python3 scripts/codex_round_count.py` exits 0. Codex never reviews a PR on its own here, so nothing arrives unless you ask. A PR with no Codex review is not done and is never merged.
2. **Validate every finding before acting.** Per §14 and §13: check it against the code. A confirmed finding is fixed; a wrong one is answered on its thread with the evidence, never silently skipped, and never "fixed" speculatively.
3. **Fix, then have the new head reviewed.** Fix each confirmed finding with a regression test, run the repository's checks, push, and request the next review on the new head SHA — each review command once per head, with no request still unanswered (§11, §16).
4. **Stop when the review is clean.** Clean means every review command the work requires — the standard review, and a security review where the protocol or the route calls for one (§12) — has a review of the *current* head that carries no finding (the bot's 👍 on that command's request counts as such a review where §14, §17 and §20 accept it) (other than a P2/P3 whose recorded rejection stands, see the last bullet below), every earlier finding was fixed or rejected with evidence, CI and the required checks are green, and there is no merge conflict. A fix pushed after the last review is unreviewed, so it is not clean — review it with every command the work requires.
5. **Merge it yourself.** A clean PR is merged under `docs/claude-to-codex.md` §20 (branch-protection precondition, merge scoped to the validated head SHA, base unchanged) without waiting for or asking the user for approval. Record the merge commit SHA and a one-line summary on the PR.
6. **Then continue.** Do not stop after the merge to ask what is next. Update the handoff `model-notes`, then start the next outstanding task from the latest default branch (a merged branch is finished; never stack new commits on it), through the full routing flow again under a new requirement id. An outstanding task is one the user explicitly asked for and that is not done yet, as recorded in this session, the session task list or the handoff `model-notes`; never invent work or pick up an item the user did not ask for. A task that needs the code of a PR that is not merged (blocked, or waiting on the owner) waits: skip it rather than stack on that branch. When none remains, report what merged and stop.

The loop adds to the tier's verification and replaces none of it: in the claude lane `code-reviewer` still runs as the profile says. A Codex review is not a Claude subagent and spends no agent budget, so T0 stays main-session. The PR description never mentions Codex (§16), and no comment or commit message carries the literal trigger string except the intentional trigger comments the protocol authorizes — each review request of steps 1 and 3, a security review, an authorized retry, each task-contract request (BRAINSTORM, INVESTIGATE, AUDIT, IMPLEMENT, FIX) or a delegated merge command (§3, §7–§13, §20).

What the loop does not change:

- **No review cap.** The owner removed the limit of three on 2026-10-12, so the loop runs until every review command the work requires is clean on the current head. A review is still bounded by §16's other rules: each review command (standard, security) once per head SHA — a required security review may follow the standard one on the same head, never while a request is unanswered, never before the previous response was validated. Two exits remain: a finding you reject with evidence — a P2/P3 stands at once and blocks nothing, even if Codex raises it again; a P0/P1 is a disagreement unless a review drops it: when other fixes make a new head, push it and let the next review decide (raised again, unchanged or reworded or moved when it is substantially the same issue, means escalate; not raised again means closed), and when no code change is pending escalate at once — report it to the repository owner and do not merge until they decide — and a genuine blocker (§20). Those brakes are rules, not script gates: the count script sees neither the PR head nor Codex's reaction. The BRAINSTORM and FIX round caps are unchanged.
- **Codex unreachable.** A trigger failure past its one retry, a stalled or failed task, or a wrong account (§17, §18) makes the PR BLOCKED, not merged unreviewed and not worked around with the API, an Action, the SDK or browser automation. Report it once, leave the PR open and continue with the next task that does not depend on it (step 6). Re-recording the requirement in the claude lane, as the lane section above says for a blocked design or implement step, moves who does the work and never waives the PR's Codex review: the PR stays BLOCKED until Codex has reviewed its head. Choosing the lane is the operator's choice, never a fallback you take.
- **The merge preconditions.** Branches required to be up to date, and a merging identity that cannot bypass the rule (§20; read the base branch's protection to confirm both). Where they are missing, merging is a genuine blocker: escalate, do not merge.
- **Who may stop the loop.** A human is needed only for §20's two cases — a genuine blocker, or a change to the original requirement.

## Marketing content rules

- **Facts come from the brief.** `tools/<tool>/brief.yaml` is the only source of claims.
  A claim with `verified: false` is written as an estimate. Never invent numbers,
  testimonials, customers, prices or dates; the AI path enforces this with
  `unsourced_numbers`, and a human reviews every post.
- **One complete post per language.** `campaigns/<c>/posts/<lang>/<id>.yaml`. Same slot id
  across languages so metrics compare; content, examples and slide count are free per
  audience. `studio.py check` warns when the numbers a slot states differ between languages.
- **Links only through `{link}`.** No URL is ever written into a post; the campaign's
  `links:` decide where a post points, tracked per post, language and platform.
- **Publishing is the owner's act.** Never publish, approve, or mark a post posted on your
  own initiative. Approval (`studio.py approve`) is pinned to a content hash; publishing
  needs that approval, a smoke-checked Page and the Page name typed. Facebook allows API
  posts to Pages only — profiles and groups get a manual pack.
- **People's words stay out of git.** Scanned or pasted comments live in gitignored
  `campaigns/*/feedback/`; raw survey exports in gitignored `research/raw/`. Commit
  aggregates and insight reports only.
- **Secrets only in `.env`.** Never in YAML, code, logs or commits.

## Languages (Vietnamese / Japanese / English)

- Content: three complete versions, as above.
- App UI: every string in `web/src/locales/{vi,ja,en}.json`; `python3 scripts/i18n_check.py`
  is the verdict on key parity, empty strings and placeholder parity, and CI runs it.
  The agent office keeps its catalogs, nested, in `office/src/locales/{vi,ja,en}.json`; the
  same script checks them.
- Rendered images: the engine's fixed words live in `mkt/text.py` (`UI`), one entry per language.
- This repository's harness (`scripts/`, hooks, agent and skill files, CLI output) stays English.

## UI implementation source

`web/` is built from `vohoailinh90/Automation-UI-Kit` (React 19 + Tailwind CSS v4 + Radix).
Its copied components live in `web/src/components/ui/`, `components/layout/`,
`components/dashboard/`, with the kit's theme tokens in `web/src/index.css` and
`web/THIRD_PARTY_NOTICES.md`. Before building a new UI piece, check the kit with
`.claude/skills/ui-kit/SKILL.md`; a component the kit lacks follows its conventions
(`cva`, `cn()`, the same tokens), as `components/ui/textarea.tsx` does. The built
`web/dist` is committed so users need no Node: rebuild it (`cd web && npm run build`) in
the same commit as any `web/src` change.

The agent office (`office/`, React 19 + Tailwind CSS v4 from the same kit) follows the same
rule: its built `office/dist` is committed, so rebuild it (`cd office && npm run build`) in the
same commit as any `office/src` change, and keep `@source not "../dist";` in
`office/src/index.css` so a build never scans the committed one.

## Verification commands

```bash
python3 -m pytest -q                      # engine, server guards, publisher fakes, AI guards
python3 studio.py check                   # every campaign: 0 errors
python3 scripts/layout_check.py           # repository layout
python3 scripts/i18n_check.py             # app catalogs in vi/ja/en
python3 scripts/mutation_check.py --all   # the safety-rail tests catch their own removal
(cd web && npm run build)                 # typecheck + build the UI (a subshell: the block runs top to bottom from the root)
python3 scripts/office/snapshot.py --check            # the agent office's data contract
(cd office && npm run typecheck && npm run lint && npm run build)   # the agent office page
```

## Repository layout

The root holds only what a user needs: README, the agent instruction files, dependency
files, `studio.py` (CLI), `app.py` (the app), `start-app.bat`, `studio.yaml`. The engine is
`mkt/`, the UI `web/`, the agent office `office/` (with its server in `scripts/office/`),
tests `tests/`, developer tooling `scripts/`. When a requirement adds
a Python file, use `.claude/skills/repo-layout/SKILL.md`; `python3 scripts/layout_check.py`
is the verdict and CI runs it.

