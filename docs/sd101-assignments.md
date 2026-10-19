# System Design 101: who is assigned which lessons and decks

Two Claude accounts (and Codex) work on `system-design-101/vi/` at the same time. The claim tools
(`scripts/sd101_claims.py` for lessons, `scripts/sd101_slides.py` for decks) only see what a session has already claimed, and the
sessions below claim five lessons at a time. This page reserves whole ranges ahead of those claims, so that no one starts a lesson
or a deck another session will reach in its next batch.

**Before you claim a lesson or a deck, read the tables below.** A range listed here is reserved even when `claim` or `status` shows
it free: do not write, build or claim inside it. Pick a range that is not listed, or ask the owner of the repository. The claim tools
stay the authority on what is being worked on right now; this page only reserves what comes next.

- **Who updates it.** The coordinator session that dispatched the work (`claude/dazzling-curie-9vyfbo`) adds a row when it
  assigns a range and marks it done when the range is merged. Another account that takes a range adds its own row in the same way,
  through a pull request, before it starts.
- **Expiry.** A reservation lapses when nothing in its range has been claimed, touched or merged for 72 hours since the date of its
  row (the same lease the claim tools use). Then the range is free again; say so in the pull request that takes it.
- **Snapshot.** Counted on 2026-10-19 from `main` and every remote branch, against source commit `b28380a` of
  ByteByteGoHq/system-design-101 (which has not moved): 404 lessons; 31 with a deck and its PPTX on `main`; 127 on `main` without a
  deck; 139 only on unmerged branches; 87 not written anywhere.

## Assigned (dispatched 2026-10-19)

| Range | Work | Session branch prefix | Status |
|---|---|---|---|
| sd-15-001..012 | PPTX of the finished decks (exports pending) | `claude/sd101-decks-w1-` | assigned |
| sd-05-001..005, sd-06-001..015 | deck and PPTX | `claude/sd101-decks-w1-` | assigned |
| sd-01-022..049 | deck and PPTX | `claude/sd101-decks-w2-` | assigned |
| sd-04-025..047 | deck and PPTX | `claude/sd101-decks-w3-` | assigned |
| sd-09-001..020 | deck and PPTX | `claude/sd101-decks-w4-` | assigned |
| sd-13-004..027 | deck and PPTX | `claude/sd101-decks-w5-` | assigned |
| sd-01-050, sd-02-004..032 | lesson, figure, deck and PPTX | `claude/sd101-lessons-w6-` | assigned |

## Queued for the same coordinator (reserved, not started)

| Range | Work | Status |
|---|---|---|
| sd-07-001..020 | lesson, figure, deck and PPTX | queued |
| sd-08-001..024 | lesson, figure, deck and PPTX | queued |

## Held by other sessions (already claimed or in an open pull request)

| Range | Work | Branch or pull request |
|---|---|---|
| sd-10-001..028 | lessons and decks | `claude/sd101-sd10-lot23` .. `lot27` (#149) |
| sd-14-016..035 | lessons and decks | `claude/sd101-sd14-lo19` .. `lo22` (#146) |
| sd-14-001..015 | decks | `claude/trusting-gauss-foyunq` |
| sd-11-001..049, sd-12-001..018 | lessons | waits on #151; old drafts #47, #51 |
| sd-04-001..024 | lessons | #144, `claude/sd101-l3-sd04` |
| sd-06-016..029 | lessons | #142, `claude/sd101-l6-sd06-b` |
| sd-01-018..021 | decks | `claude/sd101-slides-batch-gaouoy` (claim lapses 2026-10-21 13:55 UTC) |

The decks of the lessons in this last table are not reserved by anyone yet: once a lesson is on `main` and its owner is no longer
building its deck, it can be assigned here.
