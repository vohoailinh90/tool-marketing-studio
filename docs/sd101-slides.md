# System Design lessons: slide decks for Facebook

Every written lesson of `system-design-101/vi/` becomes a deck of 8 to 10 slides (the checker enforces it), built on Moda in one fixed style and
exported as PNG files (to post on Facebook) and one PPTX. Several sessions build decks at once, so a lesson is
**claimed before its deck is built**, with `scripts/sd101_slides.py`. `sd101_claims.py` only stops two sessions
*writing* one lesson; it knows nothing about decks.

## The rule for a session

```bash
python3 scripts/sd101_slides.py status                       # done / doing / stale / free per group
python3 scripts/sd101_slides.py claim --next 3 --publish     # or: claim sd-01-002 sd-01-003 --publish
python3 scripts/sd101_slides.py verify                       # exit 0 = every claim of mine is still mine and pushed
# ... build the decks on Moda; every few hours and before each push:
python3 scripts/sd101_slides.py touch --publish
python3 scripts/sd101_slides.py finish sd-01-002 --canvas cvs_... --url https://moda.app/canvas/... --slides 10 --publish
python3 scripts/sd101_slides.py exported sd-01-002 --publish # its PPTX and PNG files are now in slides/
python3 scripts/sd101_slides.py exported sd-01-002 --badged --publish  # only its PPTX, moda.app badge and all
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
lessons/<id>/slides/deck.yaml      status doing: the claim. status done: moda_canvas, moda_url, slide_count, size, exports
lessons/<id>/slides/<id>.pptx      only when exports: badged (with the moda.app badge) or done (without it)
lessons/<id>/slides/01.png ..      only when exports: done, one 1920x1080 PNG per slide
```

`exports: pending` means the deck exists on Moda and is editable there, but its files are not in the repository yet.
`exports: badged` means its PPTX is there as Moda's free plan exports it, badge and all: a reference copy to open and
present, never a file for Facebook.

### Exports and the Moda watermark

Moda's free plan puts a `moda.app` badge on every PNG and PPTX it exports. Moda's own answer is that this is a plan
limit with no setting or export option to switch off. **Do not remove it** (not from the PPTX, not by cropping or painting
over the PNG): that is getting around the plan's limit. The deck on Moda carries no badge, so building decks is not blocked;
a deck is finished with `exports: pending`. Once the owner's plan exports without the badge, any session can export a
finished deck: `export` each page as PNG (`pixel_ratio` 1) and the whole deck as PPTX, download the links with `curl`
(the host `assets-cdn.moda.app` must be in the environment's allowed domains), save them as above
(`<id>.pptx`, `01.png` to `NN.png`) and run `exported <id> --publish`, which checks the files and records `exports: done`.
The check opens every file: a PNG must be whole (every chunk's checksum, an image stream that inflates to its end, an
`IEND` chunk and nothing after it) and exactly 1920x1080; a PPTX must be a ZIP archive that reads through and holds
`[Content_Types].xml` and `ppt/presentation.xml`.
Re-exporting does not change the slides, so it needs no claim.

The owner decided on 2026-10-18 that a deck's PPTX may also go into the repository while the plan is free, badge and all:
`export` the deck as PPTX, save it as `<id>.pptx` and run `exported <id> --badged --publish`, which records
`exports: badged` (the PPTX alone, no PNG files). The badge is not removed here either, and a badged file never goes to
Facebook. The check refuses to record a PPTX that still carries the badge as `done`, and one without it as `badged` (it looks for
the picture Moda names `moda-export-watermark` on its slides); once the plan exports without the badge, replace the file,
add the PNG files and run `exported <id> --publish`.

## The style (the approved sample is sd-01-001)

The sample is `sd-01-001`; read its canvas (`canvas_read` on the id in its `deck.yaml`) for the exact markup. The rules:

- Canvas `1920x1080`, category `slides`, **no brand kit** (the workspace has none; `skip_brand_kit=true`), vector only (no
  generated images). Name it `System Design 101 · Bài NN · <short title>` and send the editor link when it exists.
- Fonts: **Bricolage Grotesque** 800 for titles and big numbers, **Be Vietnam Pro** for everything else. Sizes: cover title
  108, slide title 92 to 112, body 34 to 40, labels 22 to 28; nothing below 22.
- Colours: cream `#F3EEE3`, ink `#14161C`, card `#E8E0CF`, diagram card `#FBF8F2` (stroke `#DDD5C1`), muted `#6B6A66`;
  blue `#1F3FD1`, amber `#B45309`, teal `#0F766E`, red `#E8472B` (tints `#DDE3FA` `#F3DFB8` `#CFE8E2` `#F8D9D0`); on dark
  `#14161C` (cards `#1E212B`) with `#7C93FF` `#FFB454` `#3DD6A0` `#FF6A4D`. One colour per concept of the lesson, the same
  on every slide of the deck.
- Footer on every slide but the cover: one progress dot per slide (the current one red) and `System Design 101 · Bài NN ·
  03/10` (slide number and slide count), at the bottom left. Keep the bottom right clear.
- Slides: 1 cover (dark, the lesson title, its hook question, one line per main concept), 2 situation and goal, 3 to 7 one
  slide per concept with a diagram, then the choice or summary, a check question with its answer, the deep dive, and a last
  dark slide with the terms (the lesson's `## Từ viết tắt`) and its sources. Vary layouts (sequence diagram, flow, cards,
  numbered rows, steps); alternate cream and dark.
- Content comes from the lesson and nothing else: no new number, claim or example. Vietnamese, with diacritics; no em
  dash; at most 10 words per bullet and 3 bullets per card. A slide is read in five seconds.
- Build one slide per `canvas_apply_markup`, then `canvas_screenshot` every slide and look at it (text cut off, text
  shrunk by the auto-fit, arrows off centre) before `finish`.

Binary exports add about 1.5 MB per lesson; the repository grows by that much for each finished export set.
