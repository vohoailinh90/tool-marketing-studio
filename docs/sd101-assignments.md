# System Design 101: who is assigned which lessons and decks

Two Claude accounts (and Codex) work on `system-design-101/vi/` at the same time. The claim tools
(`scripts/sd101_claims.py` for lessons, `scripts/sd101_slides.py` for decks) only see what a session has already claimed, and the
sessions below claim five lessons at a time. This page reserves whole ranges ahead of those claims, so that no one starts a lesson
or a deck another session will reach in its next batch.

**Before you claim a lesson or a deck, read the tables below.** A range listed here is reserved for the session it names: do not
write, build or claim inside it. Pick a range that is not listed, or ask the owner of the repository. The claim tools enforce it:
`claim --next`, `next` and the *Next free* line of `status` skip every reserved id (`scripts/sd101_claims.py` for lessons, in rows
whose Work names a lesson; `scripts/sd101_slides.py` for decks, in rows whose Work names a deck or a PPTX), and a row whose Status is
`done` reserves nothing. The session a range is reserved for claims it by id (`claim <id>... --publish`). The claim tools stay the
authority on what is being worked on right now; this page only reserves what comes next.

- **Who updates it.** The coordinator session that dispatched the work (`claude/dazzling-curie-9vyfbo`) adds a row when it
  assigns a range and marks it done when the range is merged. Another account that takes a range adds its own row in the same way,
  through a pull request, before it starts.
- **Expiry.** A reservation lapses when nothing in its range has been claimed, touched or merged for 72 hours since the date of its
  row (the same lease the claim tools use). The tools keep skipping it until its row changes, so a session that takes a lapsed range
  claims it by id and, in the same pull request, rewrites the row with its own branch.
- **Snapshot.** Counted on 2026-10-20 at 01:05 UTC from `main`, against source commit `b28380a` of
  ByteByteGoHq/system-design-101 (which has not moved): 404 lessons, 403 of them written and on `main`. 384 have a finished
  deck; the 19 without one are sd-04-013..024 and sd-06-023..029. sd-02-030 is not written (its source is a picture alone).

## Assigned (dispatched 2026-10-19)

| Range | Work | Session branch prefix | Status |
|---|---|---|---|
| sd-15-001..012 | PPTX of the finished decks (exports pending) | `claude/sd101-decks-w1-` | done |
| sd-05-001..005, sd-06-001..015 | deck and PPTX | `claude/sd101-decks-w1-` | done |
| sd-01-022..049 | deck and PPTX | `claude/sd101-decks-w2-` | done |
| sd-04-025..047 | deck and PPTX | `claude/sd101-decks-w3-` | done |
| sd-09-001..020 | deck and PPTX | `claude/sd101-decks-w4-` | done |
| sd-13-004..027 | deck and PPTX | `claude/sd101-decks-w5-` | done |
| sd-01-050, sd-02-004..029, sd-02-031..032 | lesson, figure, deck and PPTX | `claude/sd101-lessons-w6-` | done |
| sd-07-001..020 | lesson, figure, deck and PPTX | `claude/sd101-lessons-w7-` | done |
| sd-08-001..024 | lesson, figure, deck and PPTX | `claude/sd101-lessons-w8-` | done |
| sd-10-001..028 | lesson, figure, deck and PPTX | `claude/sd101-sd10-lot` | done |
| sd-14-016..035 | lesson, figure, deck and PPTX | `claude/sd101-sd14-lo` | done |
| sd-11-001..049, sd-12-001..018 | lesson, figure, deck and PPTX | `claude/sd101-lessons-w16-` .. `w19-` | done |
| sd-14-001..015 | deck and PPTX | `claude/trusting-gauss-foyunq` | done |
| sd-04-001..012, sd-06-016..022 | deck and PPTX | `claude/sd101-decks-w21-` | done |

## Still to do

| Range | Work | Branch or pull request | Status |
|---|---|---|---|
| sd-04-013..024 | lessons | `claude/sd101-l3-sd04` (#228) | done |
| sd-06-023..029 | lessons | `claude/sd101-l6-sd06-b` (#227) | done |
| sd-06-001..003, sd-06-009..011, sd-13-009..011, sd-13-017..020 | decks | #194, #197 | done |
| sd-04-013..024, sd-06-023..029 | deck and PPTX | the VPS team (a Claude session with Moda; owner request 2026-10-20) | assigned |
| sd-02-030 | lesson | held for the owner's decision: its source is a picture with no text | held |

403 of the 404 lessons are on `main`. The two rows above reserve what is left: the decks of the 19 lessons that have none, for
the VPS team, and sd-02-030, until the owner decides whether it gets a lesson.
