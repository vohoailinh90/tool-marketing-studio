---
name: steward
description: Drive an open pull request from creation to merge in a repository created from this template — fill the PR from its template, subscribe to its events, request the first review, arm the one check-in that §17 needs, read each PR event for what it is, push validated fixes and merge under §20. Use right after opening a PR, whenever a PR-activity event wakes the session, or when the user says "theo dõi PR", "watch/babysit this PR", "PR を見ていて". Never use it to classify, and never to open a PR nobody asked for.
---

# Steward: one PR, open to merge

CLAUDE.md's *Pull request lifecycle* says what the loop is: review, validate,
fix, review the new head, merge, next task. This is the runbook for what lies
between those steps — what to do while waiting, and what each event means. It
adds no rule to the lifecycle and takes none away; where they differ, CLAUDE.md
and `docs/claude-to-codex.md` win.

The harness reads this file by path (`.claude/skills/steward/SKILL.md` on the
PR's head branch) before it acts on CI or review events of a PR the session
opened, so keep the name and the location. There is no `babysit` file: the
harness prefers this one when both exist.

It sets conventions and how proactive to be. It grants no merge authority (that
is lifecycle step 5 and §20) and relaxes no harness "never": no empty commit or
close-and-reopen to kick CI, no rebase, amend or force-push of a branch someone
else owns, no skipped or quarantined test.

## 1. Opening the PR

- Fill every section of `.github/pull_request_template.md` from the routing
  record (requirement id, tier, overrides, budget, artifacts) and the checks you
  actually ran. `n/a` with a reason beats a deleted section.
- The description never mentions Codex and never reports review state — what a
  reviewer found, or whether the head is clean (§16): the round count does not
  read it, a mention there can start a run it cannot see, and the state is stale
  at the next push. Review state lives on the PR's threads, not in its body.
- Title in the imperative, under 70 characters. Base: the default branch. Head:
  the session's designated branch.

## 2. Immediately after it opens

1. **Request the first review** (lifecycle step 1), before anything else: the
   lifecycle makes it the first action once the PR exists. Claude and codex lanes:
   `python3 scripts/codex_round_count.py` must exit 0, then post the §11 command.
   Codex-cli lane (only a repository that ships `scripts/codex_cli.py` has it):
   section 8 replaces this step and step 3, and its report is validated after
   step 2.
2. **Subscribe** with `subscribe_pr_activity`, right after the request. The
   lifecycle is the user's standing instruction to drive every PR to merge, so
   subscribing is part of it: do not stop to ask. The check-in in step 3 re-fetches
   every list and the request's reactions, so nothing that happened before the
   subscription is lost.
3. **Arm one check-in** with `send_later`, at the request's `created_at` + 11
   minutes, rounded up to the next whole minute. Take `created_at` from the API
   response, not the session clock. 11 is §17's silent window plus one minute for
   the scheduler's whole-minute truncation; this one check-in is what turns "Codex
   never answered" from an endless wait into a decision.
4. Record the PR number, head SHA and what is pending in the handoff
   `model-notes`: in the cloud lanes the pending request with the check-in's time
   and trigger id, in the codex-cli lane the SHA the review ran on and what is left
   to do. Then end the turn once nothing in this section is left to do. Never wait
   with `sleep` or polling.

## 3. What each event means

| Event | It is | Do |
|---|---|---|
| Subscription confirmation: the first event after `subscribe_pr_activity`, with no review, CI or comment content | An acknowledgement, not feedback | Nothing. Do not re-deliberate and do not arm another check-in; step 2.3 already did |
| Your own request or reply coming back | An echo | Nothing |
| A reaction or linked task on the request | Trigger evidence (§17); the review is still pending | Wait. Replace the pending check-in with one at the evidence's time + 31 minutes (§17's stall window plus one) and post nothing. If it fires with no result, section 4's last step |
| The bot's review-status summary comment | Neither a review nor trigger evidence (§16, §17) | Nothing |
| A bare 👍, no review | An unsuccessful completion, never a clean review (§17) | Handle it as the reaction-or-linked-task row: the review stays pending and the stall check-in is armed |
| The linked task posts a failure, error or cancellation | A terminal failure (§17) | Post nothing; section 4's last step |
| A usage-limit or error post in place of a review | An immediate trigger failure (§17) | The single authorized retry now, only if `scripts/codex_round_count.py` exits 0 and none was posted for this SHA; otherwise section 4's last step. Delete the pending check-in (`delete_trigger`) and arm a new one from the retry's `created_at` (section 2, step 3): the old one would fire inside the retry's own window |
| A review with findings | A result (§14) | Validate each finding against the code (§13); fix the real ones with a regression test; answer a wrong one on its thread with the evidence; resolve the threads you addressed. Fixed anything: section 5, then section 6. Rejected a P2 or P3: it stands at once and blocks nothing, and with nothing fixed the review counts as clean for its command. Rejected a P0 or P1: the next review of the new head decides it when other fixes make one; with no code change pending it is an unresolved disagreement (§16), so report it to the repository owner and do not merge |
| A review of the current head with no finding | A clean review for that command | Check every other review command the work requires, then CI and mergeability, then section 7 |
| CI red | Work now | Reproduce it, fix it, section 5, then section 6 |
| A merge conflict, or the base branch advanced (the harness's "base recovered" notice is one such event) | Work now | Merge the base into the PR branch (never rebase or force-push), section 5, then section 6 |
| A human comment | A request | A small, local ask: do it. A larger or ambiguous one: ask the user, with enough context to answer cold |

After the first check-in, the harness's own safety-net check-ins cover the gaps
(commit-status CI, a lost delivery): about 50 minutes after the last activity, then
about 4 hours apart, silent when nothing changed, stopping after three empty ones.

## 4. When a check-in fires

Re-fetch the PR, its reviews and its comments first, and read the `reactions` counts
on the request comment: a reaction is trigger evidence (§17), no event announces it,
and an acknowledged request must not be classified as silent and retried. A count
carries no time: take the evidence's time from the reaction record where the toolset
can list it, and otherwise from this check-in, which is never earlier than the truth,
so a stall is never declared early. Nothing remembered is current.

Every window is measured from the newest request, retry or evidence. A check-in
that fires before its window has run out is re-armed from that newest time and does
nothing else. A check-in that a later event supersedes is deleted (`delete_trigger`)
when its replacement is armed, so at most one is pending per PR.

- A result of the requested kind for the current head: validate it (§14) and
  continue the loop.
- Evidence of Codex but no result: not a trigger failure, so no retry. If §17's
  stall window has not yet run out since the last update, post nothing and arm the
  stall check-in unless one is already pending. If it has, the review is stalled:
  the last step below.
- No evidence at all: a trigger failure (§17). Post the one authorized retry only
  when `scripts/codex_round_count.py` exits 0 and none was posted for this SHA,
  then arm the same check-in again.
- A second trigger failure, no retry left, a stalled review or a task that failed
  or was cancelled: post nothing more and delete the pending check-in
  (`delete_trigger`), so it cannot wake the session to re-arm or report again. The
  PR is BLOCKED — report it once to the user, leave it open, and take the next task
  that does not depend on it (lifecycle step 6). It is never merged unreviewed, and no API,
  Action, SDK, browser or other lane stands in for the review.

## 5. Before every push

Run what CI runs for what you changed; the workflows under `.github/workflows/`
are the list. Reproduce a CI failure before fixing it and show the same check passing
after. Re-read the diff as a reviewer would. A fix ships with the test that would
have caught it, and its entry in `tests/mutations/` where one applies. No commit
message carries the literal trigger string.

## 6. After every push

The pushed head is unreviewed. For each review command the work requires, request
it on the new head once `scripts/codex_round_count.py` exits 0: once per command
per head, none while a request is unanswered, and only after the previous response
was validated (§16). Arm section 2's check-in for each request. In the codex-cli
lane, section 8.

## 7. Merge, then move on

Lifecycle step 5, under §20. Its precondition is a repository setting that the
operator applies, since it needs an admin token a session does not hold, and that
`scripts/protect_branches.py` reports where the repository ships that script (the
operator confirms it by hand where it does not). Record what you learn in
`model-notes`. Missing or unconfirmed means a genuine blocker: escalate, do not
merge. Re-fetch head and base immediately before merging and scope the merge to
`validated_head_sha`. If either moved, do not merge (§20, STALE): a moved head is
unvalidated and goes back through the review rows, and a moved base is merged into
the PR branch and the checks re-run before fresh SHAs are recorded. Then record the merge commit SHA and a one-line summary on
the PR, call `unsubscribe_pr_activity`, delete this PR's pending check-in
(`delete_trigger` on the id `send_later` returned), update `model-notes`, and take
the next outstanding task through the full routing flow.

## 8. The codex-cli lane

Only a repository that ships `scripts/codex_cli.py` has this lane
(`docs/codex-cli-lane.md`). The review runs on this machine and returns its report
before the command exits, so there is no request to post, nothing to wait for, no
check-in to arm and no reaction to read: skip step 3 of section 2 and the check-in
rules of section 4. Wherever this file says to request a review, do this instead,
then validate the report at once (§14) and work it through section 3's review rows:

- Compare the PR head with the SHA a review already ran on. A review run before the
  push is the PR's review only while the pushed head is exactly that SHA
  (CLAUDE.md, lifecycle step 1), so when they are equal reuse that report: the
  ledger refuses a second run of the same review command on one head.
- Otherwise run `python3 scripts/codex_cli.py review --branch <branch>` on the head
  the PR carries, with `--security` as well where the work requires a security
  review.

## Never

- A second review request to test the integration or to chase a slow one (§16).
- A Claude subagent because an event arrived. Events spend no agent budget; the
  budget is the requirement's, set by routing.
- Merging a head that lacks a clean review from every command the work requires.
