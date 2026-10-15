# System Design lessons: claiming a lesson before writing it

Several sessions write lessons of `system-design-101/vi/` at once, each in its own container and on its
own branch. `progress.json` names a single `next_id`, so two sessions that start together both take it
and write the same lesson. `system-design-101/vi/claims.jsonl` is the registry that prevents that, and
`scripts/sd101_claims.py` is the only way to change it.

## The rule for a session

Before you write a lesson, claim it. When you are done, mark it written. Never pick an id from
`progress.json`'s `next_id`, and never start a lesson the registry shows as taken.

```bash
python3 scripts/sd101_claims.py status                        # who holds what, what is free
python3 scripts/sd101_claims.py claim --next 3 --publish      # or: claim sd-14-016 sd-14-017 --publish
python3 scripts/sd101_claims.py verify                        # exit 0 = every claim of mine is still mine
# ... write the lessons, then every few hours and before each push:
python3 scripts/sd101_claims.py touch --publish
python3 scripts/sd101_claims.py finish sd-14-016 sd-14-017 --pr <number>   # commit it with the lesson files
python3 scripts/sd101_claims.py release sd-14-018 --publish   # give a lesson back you will not write
```

`--publish` commits only `claims.jsonl` and pushes your own work branch, never the remote's default branch
(whatever it is called; `main`/`master` are refused even on a remote that renamed its default) (any other commit of yours that was not
pushed yet goes with it), which is what makes the claim visible to the others. A claim that is not pushed protects nothing. `verify`, `touch` and `finish` therefore fail (exit 1) while a claim exists only in your working tree,
and `verify` or `touch` with named ids fail unless every id is one of your claims. The copy on your branch must also have a live heartbeat: a renewal made only in your working
tree does not keep a published claim from going stale, so `touch --publish` (which pushes first) is the way to renew. If `claim` or `verify` says you lost, stop
work on that lesson, release it and take another; do not push the draft.

A claim refused because the remote could not be read (exit 2) is not a refusal to argue with: fix the
network or ask the owner. `--offline` exists for a machine with no remote and accepts the risk. The same
exit 2 comes when the registry on some branch cannot be read as a whole registry (conflict markers committed
by mistake, an invalid record, a header of another schema or source pin, a truncated file that lost source-map lessons), because a claim in it could be missed: fix or delete that branch, or pass `--ignore-unreadable` to decide
without it. `status` only reports such a branch.

## What the file holds

JSON Lines. Line 1 is the header (`schema_version`, `lease_hours`, the source repository and the pinned
commit `b28380a4710c5ec9638ec037d4168e288f334cba`). Every other record is one of the 404 source-map
positions, in source-map order, with a blank line between every two records. Git reports two changes on
adjacent lines as one conflict, and sessions that claim the next free lessons change neighbouring records,
so the blank line is what lets two sessions that claim different lessons merge without a conflict; two that
claim the same one always conflict. `sd101_claims.py fmt` writes this layout and the checker requires it. `sd101_claims.py sync` also follows a repinned or retitled source map: it refreshes the header's pin and every title, keeps all statuses and claims, and drops records of lessons the
source map no longer lists (naming any that were not `todo`; git history keeps them).

| status | meaning | extra fields |
|---|---|---|
| `todo` | nobody has it | none |
| `doing` | a session is writing it | `owner` (its branch), `claimed_at`, `heartbeat_at`, optional `session`, `taken_from` (a list) |
| `written` | the lesson, its figure and its metadata are committed | optional `owner`, `done_at`, `pr`, `session` |

`written` is not metadata's `content_status: done`. It says the lesson was handed over; whether it was
reviewed, and whether its figure passed the phone check, stays in `metadata/<id>.json`. The 68 lessons
that were on disk when the registry was created are `written` without an owner or a date: nobody
recorded them and the registry does not invent them.

`finish` writes the terminal `written` record only when the lesson is complete: the four files exist as regular files and the
store checker (`scripts/sd101_check.py`) finds nothing wrong with the lesson's text, metadata and figure. What it says about the store
as a whole (README links, progress) is fixed afterwards, before the pull request.

## How a claim is seen by other sessions

Sessions share only the remote. Every command that decides something first fetches all branches of the
remote and reads the registry on each:

- `origin/main`: every entry counts.
- Any other branch `B`: only entries whose `owner` is `B`. A branch that was cut from a branch carrying
  someone's claim holds a stale copy of it; that copy is not a claim.
- Your working tree: the entries you own, and every written lesson.

The default branch must carry the registry: if it has none, every deciding command stops (exit 2), because a feature
branch's own copy cannot stand in for the claims already merged. `--ignore-unreadable` does not cover this case, nor a default-branch registry that cannot be read or parsed. Only `status` still reports, with a warning.

So a claim becomes visible the moment it is pushed to a branch, with no pull request needed, and it stops
counting when its branch is deleted or the lesson is released or merged as `written`.

## Dead sessions: the lease

A `doing` claim whose `heartbeat_at` is older than `lease_hours` (72) is stale. The lease is the same 72 hours in every registry (a header with another value is refused, locally and on every branch), so no two branches disagree about who is stale. It no longer blocks
anyone, but it is taken over on purpose: `claim <id> --take-stale`. The new entry records `taken_from`,
every owner whose stale claim it superseded, chain included, which makes it win against each of them even
if one wakes up and touches its heartbeat. A session that takes back a lesson it once held (because the session that took it from it let its
published heartbeat expire) starts a new claim, so the later takeover is the one that stands. Run
`touch --publish` while you work so a slow session is not mistaken for a dead one. A heartbeat dated more than an hour ahead of the observing clock
(a session whose clock is wrong) is not proof of life: it counts as expired, so it cannot block a lesson for days.

A claim that has itself expired loses to any live claim on the same lesson, whichever is older. A session
that took a lesson over cannot always record whom it took it from (the dead owner's branch may have been
deleted first), and a container that wakes up after days must not push its old claim over the new one.

## Lessons that share a source

Four pairs of positions share one source file (`same_source_as` in the source map): `sd-01-045`/`sd-10-023`,
`sd-02-019`/`sd-13-012`, `sd-07-012`/`sd-12-010`, `sd-08-020`/`sd-10-026`. Each keeps its own id, but two
sessions writing both halves would write the same lesson twice, so `claim` refuses one half while another
session holds the other. Claim both in one session, or pass `--allow-same-source` when the lessons are
meant to differ. A half that is already written by another session (or before the registry existed) blocks the other half the same way. A half taken with `--allow-same-source` keeps `shared_source` on its `written` record, so it never orders the other half to give way. The check is repeated by `verify`, `touch` and `finish`, so two sessions that took the two halves before either
push was visible are decided like two claims on one lesson (the earlier claim wins). A half taken with
`--allow-same-source` is recorded as `shared_source` and is never asked to give way. Claiming a half you already hold again with that flag records it too, which is how you keep it
on purpose after `verify` says it lost to the other half. A claim that has no live published copy (expired in public, or never pushed) gives way to a live claim on the other
half, whoever claimed first, because a takeover across a pair leaves no record of whom it replaced; Every `--publish` judges all of your claims in the
registry before it pushes (it is pushed whole), not only the ones you named, and refuses with the list to release. It also refuses to push a lesson that turned `written` since the last commit while its files (`lessons/<id>/`,
`metadata/<id>.json`, `diagrams/<id>-main.svg`) are not all committed as they are now (the lesson, its `lesson.yaml`, metadata and figure must each be in the last commit): commit the lesson and its registry
record together (`git add -A && git commit`) first, so the remote never advertises a finished lesson that its branch lacks
(or holds only an older draft of). A lesson already pushed may be reworked, but a commit that deletes one of its files, or leaves its text, metadata or figure
rejected by the store checker (judged on the committed tree, which is what the push carries, not on uncommitted edits), is refused the same way. Lessons your branch inherited from the default branch are not judged again, so the first publication stays quick. Nor is a registry pushed ahead of the source-map edit it was synchronized with: commit both together. Every `--publish` runs the store checker once on the committed tree (a copy of `HEAD`) and refuses when it reports anything about a written lesson, or about a lesson id the registry no longer lists (files left behind by a dropped record): whatever changed, a lesson's own files, a link target elsewhere, the source map. The whole committed checkout is exported for that judgement, so a lesson may link to a file outside the store. A repin or a new lesson is published from one branch while the others still have the old pin and roster: every branch's registry is judged against the source map that branch itself holds (when the map is part of the checkout), so claims on branches that have not caught up stay visible; your own registry follows your own map. `sync` refuses to drop a record while the lesson's files are still in the store. It also refuses to import a lesson that is on disk as `written` while its four files are not all there or the store checker rejects it. The same import covers a row that still says `todo` while its lesson is on disk: after merging the default branch into a work branch, run `sync` to record the lessons other sessions finished meanwhile as written (owned by your branch, with today's date). `sync` also adopts the written lessons your branch merged from another unmerged work branch (the record moves to your branch), because a record on a non-default branch counts only for its own owner and would vanish when the other branch is deleted. It refuses when the adoption would hide a shared-source conflict with a half you hold (release that half, or claim it again with `--allow-same-source`). Every `--publish` also refuses when the store checker rejects the source map itself. A branch cut before the default branch dropped a lesson from the source map cannot claim it (nor is it offered by `next`): merge the default branch first. A released lesson is not pushed while the draft you committed for it is still in git: delete the files, commit
the deletion (`git add -A && git commit`), then push.
`touch --publish`
judges this before it pushes a renewal. Every command except `sync` and `fmt` refuses a local registry that lags the source map (lessons missing, another
pin), so a truncated file is never written back or pushed; `sync` repairs it. `verify` also compares the published record with your
own claim (same `claimed_at`, takeover history and `shared_source`), not just the lesson id.

## What the registry does not guarantee

There is no compare-and-swap on a git remote. Two sessions that both read the registry before either
pushed can each write a claim for the same lesson. The protocol narrows and then catches that:

1. `claim --publish` fetches, writes, commits, pushes and verifies in one command.
2. The earlier `claimed_at` wins, then the smaller owner; the loser's `verify`, `touch` and `finish` fail.
3. `sd101_check.py` (CI) fails a branch whose registry disagrees with its lessons, and two branches that
   wrote the same lesson conflict at merge.

What is lost in that race is the loser's work, never a duplicate lesson on `main`.

The `owner` of a claim is the branch name. That is deliberate: a session that continues another
session's branch inherits its claims, and cloud sessions get distinct branch names. The cost is that two
containers working on the same branch name are one owner to the registry, and renaming a branch that
holds claims orphans them (release them first). `--owner` overrides the name for tests and detached checkouts; `--publish` refuses an owner that is not the
branch it would push, because a claim counts only on the branch its owner names.

## Checks

`python3 scripts/sd101_check.py` requires the file to list every source-map id once, in order, with the
source map's title; `written` only for a lesson that exists and `todo` only for one that does not;
well-formed fields per status; and the canonical text `sd101_claims.py fmt` writes. The claim logic is
covered by `tests/test_sd101_claims.py`, which runs real git repositories as sessions, and by
`tests/mutations/sd101_claims.yaml`.
