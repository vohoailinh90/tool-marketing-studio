# System Design lessons: slide decks for Facebook

Every written lesson of `system-design-101/vi/` becomes a deck of 8 to 10 slides (the checker enforces it), built on Moda in one fixed style and
exported as PNG files (to post on Facebook) and one PPTX. Several sessions build decks at once, so a lesson is
**claimed before its deck is built**, with `scripts/sd101_slides.py`. `sd101_claims.py` only stops two sessions
*writing* one lesson; it knows nothing about decks.

For the order of work of a whole session (Moda setup, the brief of a lesson, resuming a half-built deck, prompts to start Claude Code
or Codex with) read `docs/sd101-slides-handoff.md`.

## The rule for a session

```bash
python3 scripts/sd101_slides.py status                       # done / doing / stale / free per group
python3 scripts/sd101_slides.py claim --next 3 --publish     # or: claim sd-01-002 sd-01-003 --publish
python3 scripts/sd101_slides.py verify                       # exit 0 = every claim of mine is still mine and pushed
# ... build the decks on Moda; every few hours and before each push:
python3 scripts/sd101_slides.py touch --publish
python3 scripts/sd101_slides.py finish sd-01-002 --canvas cvs_... --url https://moda.app/canvas/... --slides 10 \
    --layouts one-highlighted-sentence,flow,... --first-concept 3 --publish   # the layout table, see below
python3 scripts/sd101_slides.py exported sd-01-002 --publish # its PPTX and PNG files are now in slides/
python3 scripts/sd101_slides.py exported sd-01-002 --badged --publish  # its PPTX (and PNG files), moda.app badge and all
python3 scripts/sd101_slides.py release sd-01-003 --publish  # give back a lesson you will not build
```

Never start a lesson's deck without a claim that `verify` accepts, and never touch a lesson the registry shows as
`doing` or `done`. Merge the default branch first: a lesson is claimable only when its `lesson.md` is in your checkout.
A claim is the file `lessons/<id>/slides/deck.yaml`; it protects nothing until it is pushed (`--publish`), the same rule as
`docs/sd101-claims.md`, and a heartbeat older than 72 hours is stale and taken over with `claim <id> --take-stale`.
If `claim` or `verify` says you lost, stop on that lesson, `release` it and take another. Claim a few lessons at a time
and finish them; claiming more than you will build in the next hours keeps them from the other sessions.
`finish` and the publishing of a finished deck need a lease that has not expired (`touch --publish` first) and a claim the
remote still holds, so a deck is never finished over a claim another session has taken; `exported --publish` asks the
remote the same before it pushes a finished record that only exists in your checkout. The tool refuses a symbolic link
anywhere between `lessons/` and `deck.yaml`: a write through one would land outside the lesson's folder.
`verify` also checks a finished deck of yours (its record must be on the remote and no earlier claim may beat it), which
is the check to run after pushing a finished folder by hand.
`python3 scripts/sd101_check.py` judges the folder (CI runs it).

## What a lesson folder holds

```
lessons/<id>/slides/deck.yaml      status doing: the claim. status done: moda_canvas, moda_url, slide_count, size, exports, layouts
lessons/<id>/slides/<id>.pptx      only when exports: badged (with the moda.app badge) or done (without it)
lessons/<id>/slides/01.png ..      when exports: done, or badged with all of them: one 1920x1080 PNG per slide
```

`exports: pending` means the deck exists on Moda and is editable there, but its files are not in the repository yet.
`exports: badged` means its PPTX is there as Moda's free plan exports it, badge and all, and so are its PNG files when
they were added (all of them or none): the PPTX is a reference copy to open and present, never a file for Facebook; the
PNG files carry the badge the owner accepts on them, and the owner uploads them like any other deck's.

### Exports and the Moda watermark

Moda's free plan puts a `moda.app` badge on every PNG and PPTX it exports. Moda's own answer is that this is a plan
limit with no setting or export option to switch off. **Do not remove it** (not from the PPTX, not by cropping or painting
over the PNG): that is getting around the plan's limit. The deck on Moda carries no badge, so building decks is not blocked;
a deck is finished with `exports: pending`. Once the owner's plan exports without the badge, any session can export a
finished deck: `export` each page as PNG (`pixel_ratio` 1) and the whole deck as PPTX, download the links with `curl`
(the host `assets-cdn.moda.app` must be in the environment's allowed domains), save them as above
(`<id>.pptx`, `01.png` to `NN.png`) and run `exported <id> --publish`, which checks the files and records `exports: done`.
The check opens every file: a PNG must be whole (every chunk's checksum, an image stream that inflates to its end, an
`IEND` chunk and nothing after it) and exactly 1920x1080; a PPTX must be a ZIP archive that reads through, holds
`[Content_Types].xml` and `ppt/presentation.xml`, and has as many slides as `slide_count` (badged or not).
Re-exporting does not change the slides, so it needs no claim.

The owner decided on 2026-10-18 that a deck's files may also go into the repository while the plan is free, badge and
all: `export` the deck as PPTX (and each page as PNG, `pixel_ratio` 1, for the files the owner uploads), save them as
above and run `exported <id> --badged --publish`, which records `exports: badged` (the PPTX, with all its PNG files or
none). The badge is not removed here either, and a badged PPTX never goes to Facebook. The check refuses to record a PPTX
that still carries the badge on any slide as `done`, and one that lacks it on any slide as `badged` (it looks for the
picture Moda names `moda-export-watermark` on every slide); the badge cannot be told on a PNG, so the PNG files of a
badged export are only checked as whole 1920x1080 images. Once the plan exports without the badge, replace the files,
add the PNG files and run `exported <id> --publish`.

## The style (the approved sample is sd-01-001)

The sample is `sd-01-001`; read its canvas (`canvas_read` on the id in its `deck.yaml`) for the tokens (colours, fonts, sizes,
footer), not for its layouts: a deck that repeats the sample's layouts slide for slide is not finished (see *Variety between
decks* below). The rules:

- Canvas `1920x1080`, category `slides`, **no brand kit** (the workspace has none; `skip_brand_kit=true`), vector only (no
  generated images). Name it `System Design 101 · Bài NN · <short title>` and send the editor link when it exists.
- Fonts: **Bricolage Grotesque** 800 for titles and big numbers, **Be Vietnam Pro** for everything else. Sizes: cover title
  108, slide title 92 to 112, body 34 to 40, labels 22 to 28; nothing below 22.
- Colours: cream `#F3EEE3`, ink `#14161C`, card `#E8E0CF`, diagram card `#FBF8F2` (stroke `#DDD5C1`), muted `#6B6A66`;
  blue `#1F3FD1`, amber `#B45309`, teal `#0F766E`, red `#E8472B` (tints `#DDE3FA` `#F3DFB8` `#CFE8E2` `#F8D9D0`); on dark
  `#14161C` (cards `#1E212B`) with `#7C93FF` `#FFB454` `#3DD6A0` `#FF6A4D`. One colour per concept of the lesson, the same
  on every slide of the deck; which colour a concept gets follows the rotation under *Variety between decks*.
- Footer on every slide but the cover: one progress dot per slide (the current one red) and `System Design 101 · Bài NN ·
  03/10` (slide number and slide count), at the bottom left. Keep the bottom right clear.
- Slides: the cover first (dark: the lesson title, its hook question, one line per main concept) and the terms and sources
  last (dark: the lesson's `## Từ viết tắt` and its `## Nguồn đối chiếu`; a lesson with no `## Từ viết tắt` gets the terms it
  explains itself). Between them the lesson's own logic sets the order: the situation and goal, one slide per concept with a
  diagram, the choice or summary, a check question with its answer, the deep dive. The check question is the lesson's own,
  from its `## Nhìn hình thử trả lời` or its `## Nhìn hình trả lời` section, whichever it has (both names exist); a lesson with
  neither gets a recap in its own sentences instead. The layouts and the light and dark rhythm are set under *Variety
  between decks*.
- Content comes from the lesson and nothing else: no new number, claim or example. Vietnamese, with diacritics; no em
  dash; at most 10 words per bullet and 3 bullets per card. A slide is read in five seconds.
- Build one slide per `canvas_apply_markup`, then `canvas_screenshot` every slide and look at it (text cut off, text
  shrunk by the auto-fit, arrows off centre) before `finish`.

### Variety between decks

The decks of one series are recognisable as one brand and still do not look alike. The brand is fixed: the fonts, the neutrals
(cream, ink, card), the footer, the size floor, the `1920x1080` canvas, 8 to 10 slides, the dark cover first and the dark terms
and sources slide last. Everything else differs from deck to deck; `sd-01-001` is one example of it, not the template.

- **Visual idea.** Each deck gets one idea taken from its lesson's own subject (a deck about NAT built around an address table,
  one about HTTP/2 around a single pipe that carries several streams). Say it in one line in the first message about the deck;
  there is no need to wait for an answer unless the owner replies.
- **Layout kinds.** A slide is exactly one of these twelve: sequence diagram, flow, two-column comparison, 2x2 matrix, lookup
  table, card grid, numbered rows, connection diagram, layers, timeline, one big number, one highlighted sentence. A deck
  uses at least five different kinds and never the same kind on two adjacent slides. The lesson's `kind` (in
  `system-design-101/vi/metadata/<id>.json`) says where to lean, in these names: `flow` toward sequence diagram and flow,
  `comparison` toward two-column comparison and 2x2 matrix, `reference` toward lookup table and card grid, `topology` toward
  layers and connection diagram, `timeline` toward timeline, `howto` toward numbered rows.
- **Signature layout.** The slide for the lesson's first concept takes the kind at position (n mod 12) in the list above,
  counted from 0 in the order the list gives them (n as under *Accent rotation*), or, when the content cannot be shown that
  way (a one big number slide needs a number the lesson states), the next kind in the list, wrapping round, that it can; each
  kind passed over is named with its reason in `finish --cannot` (below). Two
  decks whose n differ mod 12 and that both use their own position start their concepts differently; a fallback can land on
  the kind another position holds, and nothing here claims otherwise. What the rule guarantees is that a session picks the
  layout from its own lesson id and never looks at another deck to choose.
- **Accent rotation.** The four accents are, counted from 0: blue, amber, teal, red. With n the number at the end of the
  lesson id (`sd-01-004` gives 4), the k-th concept of the lesson (k counted from 0) takes the accent numbered (n + k) mod 4.
  A concept keeps its colour on every slide of the deck. Lessons with consecutive ids in one group therefore open with
  different colours; across a group boundary (`sd-05-005` and `sd-13-001`, say) they can coincide, and nothing here claims
  otherwise. A session never needs to look at another deck to choose.
- **Light and dark.** Follow the content, not a strict alternation: never more than three slides in a row on the same
  background.
- **Moda's own help** (`load_skill`, `template_search`) may suggest layouts; the tokens above stay.
- **Layout table.** `finish` takes it and checks it: `--layouts` is the kind of every slide, in order, one per slide, spelled
  as in the list above with hyphens (`sequence-diagram`, `flow`, `two-column-comparison`, `2x2-matrix`, `lookup-table`,
  `card-grid`, `numbered-rows`, `connection-diagram`, `layers`, `timeline`, `one-big-number`, `one-highlighted-sentence`;
  spaces and capitals are read the same); `--first-concept N` is the number of the slide of the lesson's first concept, from 2 to
  one before the last; `--cannot KIND=REASON`, once for each kind, only when the signature layout fell back, names every kind
  passed over and why the content cannot be shown that way (`--cannot "one big number=the lesson states no number"`). `finish`
  refuses a table with a kind outside the list, a number of kinds that is not the slide count, fewer than five different
  kinds, the same kind on two adjacent slides, or a first concept that is not on its signature kind (or on a later one with
  exactly the passed-over kinds named), and says which rule. A table that passes is kept as `layouts` in `deck.yaml`
  (`slides`, `first_concept`, and `cannot` after a fallback), and every later read of the record checks it again. The light and
  dark rhythm, the accent rotation and the visual idea are not in the table and no tool checks them. Put the table in the
  report to the owner as well. A deck finished before 2026-10-20 has no table and stays valid; from that day on a record with
  no `layouts` fails the folder check (`verify`, `sd101_check.py`, CI), so a checkout that predates the table cannot finish a
  deck without one. Such a record is mended by adding the key to its `deck.yaml` by hand, in this shape, which the same check
  then validates:

  ```yaml
  layouts:
    slides: [one-highlighted-sentence, flow, lookup-table, ...]   # one kind per slide, in order
    first_concept: 3
    cannot: {one-big-number: the lesson states no number}        # only after a fallback
  ```

Binary exports add about 1.5 MB per lesson; the repository grows by that much for each finished export set.
