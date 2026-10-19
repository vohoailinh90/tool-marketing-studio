# Continuing the System Design slide decks on Moda (handoff for Claude Code or Codex)

Read this when you are asked to build, resume or finish the Moda decks of `system-design-101/vi/` lessons. It is the order of work
for one session; the rules it leans on stay where they are: `docs/sd101-slides.md` (claims, the style, exports, the watermark) and
`CLAUDE.md` (*System Design slides: claim before you build*). Where this page and those differ, they win.

## What you need before you start

- **Moda access.** A deck is a canvas on Moda, exported to PPTX by Moda. If your session has no Moda tools (Claude Code: the
  connector whose tools are named `mcp__Moda_-_Slides_and_Designs__*`), stop and say so: do not draw slides with python-pptx or
  with images, and do not claim a lesson you cannot build. Moda's free plan is enough; it puts a `moda.app` badge on exported files
  that you must never remove (`docs/sd101-slides.md`, *Exports and the Moda watermark*).
- **The repository current.** `git fetch origin && git merge origin/main`: a lesson is claimable only when its `lesson.md` is in your
  checkout. Then `pip install -r requirements-dev.txt` so `scripts/sd101_check.py` runs.
- **The assignment board.** `docs/sd101-assignments.md` reserves whole ranges for sessions that claim five lessons at a time;
  `claim --next` skips those ranges, and you claim inside one by id only when it is reserved for you.
- **Nothing to publish.** Building a deck is not posting it. You never upload to Facebook; the owner does.

## The loop for one lesson

```bash
python3 scripts/sd101_slides.py status                      # what is done / doing / free, and the next free lessons
python3 scripts/sd101_slides.py claim --next 3 --publish    # claim before building; claim only what you will build now
python3 scripts/sd101_slide_brief.py sd-01-027              # the lesson cut into slide roles (add --json for a tool)
```

1. **Read the brief.** It copies the lesson's own lines onto the slide roles of the style (six fixed ones and two to four concept slides), names the canvas, fixes the slide
   count (8 to 10), gives each concept its colour (the same on every slide of the deck; the rotation of `docs/sd101-slides.md`, *Accent
   rotation*, which starts from the lesson number), names the signature layout of the first concept's slide (slide 3) and flags everything still over
   10 words: lines, concept labels, terms and source names. Paragraphs and bullets keep the order the lesson writes them. The other slides'
   layout kinds are yours to choose from the twelve of the layout table, and the backdrop of the slides between the dark cover and the dark closing
   slide follows the content (*Variety between decks*).
   Its `Concepts are taken from` line says where the lesson keeps its concepts: bullets or bold-label paragraphs under
   `## Đọc hình`, bullets before the first section, or the text cards of the figure (`diagrams/<id>-main.svg`) for lessons that keep
   them only there (the rows of a table in the figure are folded into the card of their heading). For those, the figure's line breaks are lost in the brief: open the SVG to read the sentences, and the prose
   under `Đọc hình` (left off slide 2 because it explains those same cards, a WARNING says how long it is) is in `lesson.md`.
   A typed address in the lesson shows as `[address]`: draw such an example as its parts (scheme, host, path ...), never as one address.
   The brief leaves out what is not slide text and says so in a WARNING: a code block or table, and the sections of the lesson's body
   (a catalogue, an experiment) that are not its limits or choice sections; read them in `lesson.md`. The figure description in the
   header is for planning the diagrams, not copy.
2. **Start Moda.** `moda_bootstrap`, then `load_skill("moda-core")` once, then `load_skill("moda-deck")` and the skills it names (`markup`,
   `deck-design`, `design-quality` and the one for working without a brand kit). Moda asks you to ask which brand kit a new design
   uses; for these decks the answer is already fixed (*no kit*, `docs/sd101-slides.md`) and `brand_list` returned no kit on
   2026-10-18, so do not ask the owner again. The tool schemas are authoritative for parameter names.
3. **Look at a finished deck first.** `canvas_search` for `System Design 101` lists them; `canvas_read` (with `summary=true`, then
   one `page`) and `canvas_screenshot` show the real markup. Do not copy a slide, copy the system: colours, fonts, footer, spacing; the
   layouts are not part of it, each deck gets its own (*Variety between decks*).
4. **Create the canvas** with the name from the brief, 1920x1080, category `slides`, no brand kit, one page per slide
   (`canvas_create`; further pages are added inside a `canvas_edit` program). Send the editor link as soon as it exists.
5. **Write the copy, then draw one slide per `canvas_apply_markup`.** Condense each brief line to at most 10 words, at most 3
   bullets per card, nothing the lesson does not say. Vietnamese with diacritics, no em dash, no address typed on a slide.
6. **Look at every slide** with `canvas_screenshot` (text cut off, text shrunk by auto-fit, arrows off centre, anything under 22 px,
   the bottom right corner not clear) and fix it before the next one.
7. **Finish.**

```bash
python3 scripts/sd101_slides.py touch --publish             # while you work; a heartbeat older than 72 h is stale
python3 scripts/sd101_slides.py finish sd-01-027 --canvas cvs_... --url https://moda.app/canvas/... --slides 10 \
    --layouts KIND,KIND,... --first-concept 3 --publish     # the layout table: one kind per slide, in order
python3 scripts/sd101_check.py                              # CI runs it on the folder
```

   `--layouts` lists the layout kind of every slide in order and `--first-concept` is the slide of the lesson's first concept (slide 3 in
   a brief); add `--cannot KIND=REASON` only when the signature layout fell back. `docs/sd101-slides.md` (*Layout table*) has the rules
   `finish` checks and the twelve kind names.

   A deck is finished with `exports: pending`. **Its PPTX file then goes into the repository** (owner decision 2026-10-18, a reference
   copy that is never posted): `export` the whole deck as PPTX (`export(canvas_ref, format="pptx")` returns a short-lived download
   link; fetch it with `curl`, the host `assets-cdn.moda.app` must be in the environment's allowed domains), save it as
   `system-design-101/vi/lessons/<id>/slides/<id>.pptx`. The PNG files are optional, all of them or none: `export` each page as PNG
   (`pixel_ratio` 1) and save them as `01.png` to `NN.png` next to it. Then
   `python3 scripts/sd101_slides.py exported <id> --badged --publish`, which opens the files and records `exports: badged`. The badge
   stays on every slide. The PPTX is never a file for Facebook; the PNG files of a badged export carry the badge the owner accepts on
   them, and the owner uploads them. `exports: done` (plain `exported <id> --publish`) waits until the owner's plan exports without
   the badge (`docs/sd101-slides.md`, *Exports and the Moda watermark*).

## What was seen on 2026-10-18 (re-check, do not rely)

- Canvas names follow `System Design 101 · Bài NN · <lesson title> (sd-XX-NNN)`, where `NN` is the lesson's position in its group
  (sd-14-009 is Bài 09). A few older decks (sd-01-001, sd-01-011, sd-01-012) lack the `(id)` suffix.
- The cover of sd-14-001 (read with `canvas_read`): page 1920x1080 filled `#14161C`; a 24 px label `SYSTEM DESIGN 101 · BÀI 01` in
  `#FF6A4D` with letter-spacing 4; the title in Bricolage Grotesque 800 at 108 px `#F3EEE3`; the hook question in Be Vietnam Pro 40 px
  `#E4E1D8`; a 28 px sub-line and a 22 px footer line in `#9AA0B5`; one rounded card per concept (420x76, radius 38, fill `#1E212B`,
  3 px stroke and 28 px bold text in that concept's colour) joined to a round hub by curved 5 px lines. The brief's `question_candidate`
  is the lesson's check question; sd-14-001 uses it as the hook question.
- The canvas recorded for sd-03-001 in its `deck.yaml` (`cvs_56W3...`) answered `canvas_not_found` for the account that was logged in
  to Moda in that session, while the decks of sd-14 were listed and readable. Before resuming or exporting a deck, `canvas_read` its id; if it is
  not found, tell the owner rather than building a second canvas under the same lesson.
- Other sessions build decks at the same time. `status` prints `names another owner` warnings for decks inherited by merging; they are
  not claims and not a problem.

## If a session died mid-deck

A claim stays `doing` until `finish`, and the canvas id is recorded only by `finish`. Look for a canvas of that lesson first
(`canvas_search` on the id, e.g. `sd-01-027`): continue on it instead of creating a second one. Take over a stale claim with
`claim <id> --take-stale`. A lesson you will not build is given back: `release <id> --publish`.

## Starter prompts

Claude Code:

> Continue the System Design slide decks. Read `docs/sd101-slides-handoff.md` and follow it. Claim the next 3 free lessons with
> `sd101_slides.py`, build each deck on Moda from `sd101_slide_brief.py`, look at every slide, finish them, export each deck as PPTX
> into its lesson folder with `exported <id> --badged`, and tell me the editor links. Do not publish anything and do not remove the
> Moda badge.

Codex:

> Read `AGENTS.md`, `CLAUDE.md` and `docs/sd101-slides-handoff.md`. If this session has no Moda tools, say so and stop. Otherwise claim
> the next 3 free lessons with `scripts/sd101_slides.py`, build each deck on Moda from the output of `scripts/sd101_slide_brief.py`,
> check every slide with a screenshot, record them with `finish`, add each deck's PPTX with `exported <id> --badged`, and report the
> editor links and any lesson you could not finish.

## Where things are

| What | Where |
|---|---|
| Claims, style, exports, watermark | `docs/sd101-slides.md` |
| Claim and export commands | `scripts/sd101_slides.py` |
| Brief for one lesson (read-only, writes no file) | `scripts/sd101_slide_brief.py`, tested by `tests/test_sd101_slide_brief.py` |
| A lesson's record | `system-design-101/vi/lessons/<id>/slides/deck.yaml` |
| The lessons and their figures | `system-design-101/vi/lessons/<id>/lesson.md`, `diagrams/<id>-main.svg` |
