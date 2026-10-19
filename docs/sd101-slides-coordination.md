# System Design slide decks: who does what (coordination board)

Several Claude sessions, from **two Claude accounts**, build the Moda decks of `system-design-101/vi/` at the same time. The
per-lesson claim (`scripts/sd101_slides.py`, `docs/sd101-slides.md`) stays the only lock: never build a lesson `status` shows as
`doing` or `done`. This board adds what the claims cannot say: which session owns which **range of work**, including the PPTX
exports of finished decks, which have no claim of their own. Read it before you start; take work outside the ranges below, or a
range whose session is marked ended.

Coordinator: `claude/system-design-ppt-coordination-o93528` (session `session_01EEyBDZ6v19PCc7JPGubEEn`). Board written
2026-10-19 00:45 UTC, updated 06:45 UTC. The same board is posted as a GitHub issue titled *SD101 slides: coordination board*; comment there to
take or give back a range.

## Process every session follows (owner decision 2026-10-19)

- One PPTX per lesson, moda.app badge and all, saved as `system-design-101/vi/lessons/<id>/slides/<id>.pptx`, recorded with
  `sd101_slides.py exported <id> --badged --publish`. **No PNG files** for now.
- The session does all the work itself: no subagent reviews of slides; it checks each slide with `canvas_screenshot` and the
  repository's scripts.

## Live state

This board does not keep counts: they change with every push. `python3 scripts/sd101_slides.py status --all` (after
`git fetch origin && git merge origin/main`) gives the live numbers per group and every `doing` claim with its branch.

A deck counts as exported when its record says `exports: badged` (or `done`) on **any** branch, `main` first: a builder's
branch can still carry an older `pending` record of a deck whose PPTX is already on `main`. Never export a deck again
that has one.

## Ranges

The owner allows **at most two account-A sessions working at once** (decision 2026-10-19). The coordinator resumes the
sessions below one after another. Each finishes the claims it holds; a session is given a new lesson only through this
board.

| Holds (`doing`) at 06:45 UTC | Session | Order |
|---|---|---|
| sd-13-020, then sd-06-010..011 (free, released by the sd-06 session) | `session_01EhxTYrCJpuk4mcqCLwPdds` (`claude/sd13-slides-0219`) | next |
| sd-01-038..040 | `session_01ARzV9v8j9Ux8mYa9UcKRzC` (`claude/sd101-slides-sd01-0210`) | then |
| sd-04-041..043 | `session_013D8efqJ38789pjA4WvcwwT` (`claude/sd101-slides-sd04`) | then |
| sd-14-009..015 | `claude/trusting-gauss-foyunq` (heartbeat 2026-10-18 07:11 UTC; stale after 72 h, then `claim --take-stale`) | not ours |

The sd-06 and sd-09 sessions have finished building and only drive their pull requests to merge.

### PPTX exports still missing

| Decks | Who |
|---|---|
| sd-15-001..012 | exported by `session_015U1QMJBxBFrqQh6qyz6yMm`, PR #162 |
| sd-14-001..008 | **the other account**: their canvases answer `canvas_not_found` for account A's Moda. Free for the account that owns them |

A canvas this account cannot read (`canvas_not_found`) belongs to the other account's Moda: list it in the issue for that
account instead of building a second canvas.

## Not covered yet

The lessons not written yet (`progress.json` lists the written ones). Writing them follows `docs/sd101-claims.md` and is not part of this board until the owner asks.
