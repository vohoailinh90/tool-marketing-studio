# System Design slide decks: who does what (coordination board)

Several Claude sessions, from **two Claude accounts**, build the Moda decks of `system-design-101/vi/` at the same time. The
per-lesson claim (`scripts/sd101_slides.py`, `docs/sd101-slides.md`) stays the only lock: never build a lesson `status` shows as
`doing` or `done`. This board adds what the claims cannot say: which session owns which **range of work**, including the PPTX
exports of finished decks, which have no claim of their own. Read it before you start; take work outside the ranges below, or a
range whose session is marked ended.

Coordinator: `claude/system-design-ppt-coordination-o93528` (session `session_01EEyBDZ6v19PCc7JPGubEEn`). Board written
2026-10-19 00:45 UTC. The same board is posted as a GitHub issue titled *SD101 slides: coordination board*; comment there to
take or give back a range.

## Process every session follows (owner decision 2026-10-19)

- One PPTX per lesson, moda.app badge and all, saved as `system-design-101/vi/lessons/<id>/slides/<id>.pptx`, recorded with
  `sd101_slides.py exported <id> --badged --publish`. **No PNG files** for now.
- The session does all the work itself: no subagent reviews of slides; it checks each slide with `canvas_screenshot` and the
  repository's scripts.

## State at writing (from every remote branch)

| | lessons |
|---|---|
| Source map | 404 positions; 178 lessons written (`progress.json`), 226 not written yet (no deck possible before the lesson) |
| Decks done with PPTX (`exports: badged` on some branch, usually `main`) | 52 |
| Decks done without PPTX on any branch (`exports: pending`) | 20: sd-14-001..008, sd-15-001..012 |
| Decks being built (`doing`) | 27, among them the other account's `claude/sd101-decks-w1-1` .. `w5-1` |
| Decks nobody has claimed | 79 (sd-01: 20, sd-04: 18, sd-13: 16, sd-06: 12, sd-09: 12, sd-10: 1) |

## Ranges

### Building new decks (claim lesson by lesson, 3 at a time, inside the group)

| Range | Session | Holds now |
|---|---|---|
| free lessons of sd-01 (from sd-01-027) | `session_01ARzV9v8j9Ux8mYa9UcKRzC` | none yet |
| free lessons of sd-04 | `session_013D8efqJ38789pjA4WvcwwT` | none yet |
| free lessons of sd-06 | `session_01XSxLqDPHaDeZhrxWwesxJf` (`claude/sd101-slides-sd06`) | sd-06-001..003 |
| free lessons of sd-09, then sd-10 | `session_01MXmeiiiaXLzfKLWZzK9sru` (`claude/sd101-slides-sd-09`) | sd-09-006..008 |
| free lessons of sd-13 | `session_01EhxTYrCJpuk4mcqCLwPdds` (`claude/sd13-slides-0219`) | sd-13-009..011 |

The other account's sessions keep their own claims; a group range here is not a claim, so both accounts may still claim free
lessons of the same group through the tool, which settles each lesson.

### PPTX exports of finished decks (`exports: pending`; no claim exists for these, so this board is the lock)

| Range | Session |
|---|---|
| sd-14-001..008 (finished records only on `claude/trusting-gauss-foyunq`, not on `main` yet), sd-15-001..012 | export session A, `session_015U1QMJBxBFrqQh6qyz6yMm` |

A deck counts as exported when its record says `exports: badged` (or `done`) on **any** branch, `main` first: a builder's
branch can still carry an older `pending` record of a deck whose PPTX is already on `main`. Never export a deck again
that has one.

An export session `canvas_read`s the deck's recorded canvas first. A canvas this account cannot read (`canvas_not_found`, as
seen for sd-03-001) belongs to the other account's Moda: list it in the issue for that account instead of building a second
canvas.

## Not covered yet

The 226 unwritten lessons. Writing them follows `docs/sd101-claims.md` and is not part of this board until the owner asks.
