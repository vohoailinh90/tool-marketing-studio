# Figures for the System Design lessons

`scripts/figures/` draws a lesson's figure from a small spec, so a session chooses the words and the pictograms and a script
chooses everything else. It exists so the lessons of `system-design-101/vi/` can be redone with figures that carry icons,
numbered steps, arrows and message sequences instead of plain boxes. It is a port of the drawing code of
`vohoailinh90/github-radar` (`radar/boards.py`, `svg.py`, `excalidraw.py`, `moda.py`, `drawio.py`, `icons/`), narrowed from a
1200 px digest to the 320 px column a lesson is read in on a phone.

The owner asked for it on 2026-10-17 and thereby lifted "chưa xây framework renderer" from
`brainstorm/system-design-101-vi/DECISIONS.md` (the row is updated). A hand-drawn figure is still valid; this is the way to get a
consistent one without writing coordinates.

## The spec

One JSON file per figure, `system-design-101/figures/vi/<lesson id>.json` (next to the store, not in it: `vi/` accepts only what
`scripts/sd101_check.py` knows). Keys outside this vocabulary are refused.

```json
{"id": "sd-01-001", "lang": "vi", "title": "...", "subtitle": "...", "desc": "alt text of the whole picture",
 "sections": [
   {"kind": "parts", "heading": "...", "items": [{"name": "...", "role": "...", "icon": "server"}], "flow": [[0, 1], [1, 2]]},
   {"kind": "steps", "heading": "...", "items": [{"title": "...", "text": "..."}]},
   {"kind": "notes", "heading": "...", "items": ["..."]},
   {"kind": "sequence", "heading": "...", "actors": [{"name": "...", "icon": "monitor"}, {"name": "..."}],
    "messages": [{"from": 0, "to": 1, "text": "..."}, {"from": 1, "to": 0, "text": "...", "reply": true}]}]}
```

- `parts`: 2-6 cards in a column. A link to the next card is a straight arrow; any other link runs in a lane beside the cards (at
  most 4 lanes; the spec check says when a flow needs more). Name an icon for every card or for none.
- `steps`: 2-8 numbered cards joined by short arrows. `notes`: 2-8 cards with a tick.
- `sequence`: 2-3 actors, 2-10 messages; `reply` draws the arrow dashed.
- Limits on lengths and counts are in `scripts/figures/spec.py`. No address is accepted in any text (the studio's own rule for posts, `mkt.check.has_url`: `https://`, `www.`, a bare
  domain, a spaced scheme; it also reads a file name that ends in a country code, such as `server.py` or `README.md`, as a domain, so
  write the name as a word), no control or invisible character (any Unicode control, format, surrogate or line-separator character: zero-width spaces and joiners, direction marks, a byte-order mark), and no icon outside the set
  (`python3 -m scripts.figures icons` lists the 81 names and what each means).

Every word on the figure is a field of the spec: no caption, arrow label or icon is invented by the drawing code.

## Commands

```bash
python3 -m scripts.figures icons                      # the names a spec may use, with their meaning
python3 -m scripts.figures preview SPEC               # a PNG in build/figures/ (Chromium) to look at
python3 -m scripts.figures build [SPEC ...]           # write system-design-101/vi/diagrams/<id>-main.svg (the lesson must exist)
python3 -m scripts.figures check [SPEC ...]           # specs valid, stored figures are exactly what the specs draw, store and phone rules, icons intact
python3 -m scripts.figures check --browser            # ... and measure every line of text in Chromium
python3 -m scripts.figures render SPEC --format drawio|excalidraw|moda|svg [--out FILE] [--scale 2]     # scale from 0.25 to 8
python3 -m scripts.figures facebook SPEC [--format portrait|square|landscape] [--out DIR]   # Facebook slides, see below
```

`check` without a spec checks every spec in `system-design-101/figures/vi/` and runs in the test suite, so a figure that no longer
matches its spec fails CI. An editor file kept next to a spec (`<id>.drawio`, `<id>.excalidraw`, `<id>-moda.xml`) must match too;
the editor files are not committed by default.

## Redoing a lesson

1. Claim the lesson (`docs/sd101-claims.md`): the figure belongs to the lesson body.
2. Write the spec; `preview` it; read the picture, not the JSON.
3. `build`, then show it in `lesson.md` (alt text, `diagrams/<id>-main.svg`). Every abbreviation of two capitals or more in the
   figure's text goes in the lesson's `## Từ viết tắt`; `python3 scripts/sd101_check.py` says which.
4. `check --browser`, `python3 scripts/sd101_check.py`, then look at it on a phone or on GitHub: the phone rule is checked as
   arithmetic (`scripts/figures/mobile.py`: 14 px at a 375 px screen, 12 px at 320 px, nothing past the edge), not as a promise that
   it reads well. Whether the figure explains the lesson is the reviewer's call.

## Images for Facebook: the standard

A lesson figure is a 320 px column for a phone page. For Facebook it is exported as slides, and this is the one way a lesson image
is made for upload: `python3 -m scripts.figures facebook SPEC` writes `build/figures/facebook/<id>/01.png ...` and `alt.txt`
(`build/` is gitignored; the images are regenerated, never committed or edited). The standard is the studio's own
(`mkt/page.py`, `mkt/theme.css`) so a lesson's slides sit beside the campaign slides, and `scripts/figures/facebook.py` enforces it:

| Rule | Value |
|---|---|
| File | PNG, opaque, exactly the canvas size, at most 4 MB (checked after writing) |
| Canvas | `portrait` 1080x1350 (4:5, the default for the feed), `square` 1080x1080, `landscape` 1200x630 (a link preview: figures rarely fit it). The sizes are read from `mkt/page.py`, never copied |
| Slides | one section of the figure per slide, under the figure's title (the subtitle on the first slide only); at most 10 slides per post (`MAX_SLIDES` of `mkt/check.py`) |
| Text | the smallest body text on a slide is at least 30 px on the canvas (the studio's body text runs 28-34 px; on a 375 px phone that is about 10 px; the 22 px footer is the studio's own and is not body text). A section that cannot be scaled that far is refused: split it in the spec or shorten its words, never lower the limit |
| Footer | `author.handle` of `studio.yaml` bottom left when set, `n/N` bottom right, 22 px muted: the studio's footer |
| Words | no address on any slide (the spec check refuses one); a link goes only through `{link}` in the first comment of a campaign post |
| Alt text | `alt.txt` holds the figure's `desc` and one line per slide from the spec's own headings: paste it into Facebook's alt-text field when uploading |

`check` also runs the portrait plan on every spec, so a figure that could not be exported to the standard fails CI instead of
failing when someone wants to post it. That is a limit on every spec in the store, not only on the ones to be posted: **a section must
fit one portrait slide.** Measured with the portrait canvas: about 4 cards of a `parts` section when the roles are short (3 when they
run to two or three lines), 4 steps, 5 notes, and a `sequence` of up to 10 short messages. The spec limits (6 cards, 8 steps, 8 notes)
are looser than that on purpose; the Facebook plan names the slide that is too tall, and the author splits the section in the spec. A
figure of 4 cards fits a portrait slide and not a square one. The two layout fixtures that stress the drawing (`tests/fixtures/figures/stress.json`)
are not specs of the store and are not meant to export.

What a session does and does not do:
- It regenerates the slides after any change to a spec, and looks at them (read the PNGs) before saying they are ready.
- It never edits a PNG, never uploads a picture exported from Moda, Canva, Figma, draw.io or Excalidraw as a standard image (those
  are for polishing, and their files do not carry the footer, the sizes or the checks above), and never posts, approves or marks
  anything posted: publishing is the owner's act (CLAUDE.md, *Marketing content rules*).
- Lesson slides are uploaded by hand. They are not attached to a campaign post through the `image` layout: that layout adds the
  studio's header and footer around a screenshot, on top of the footer these slides already carry.

## The four outputs

| Output | For | Notes |
|---|---|---|
| SVG (`svg.py`) | the lesson | Plain elements only (what `sd101_check.SVG_ELEMENTS` allows), 320 px wide, DejaVu Sans, the look of the stored figures. Icons are drawn from the shapes of the icon files, never as `<image>`. |
| draw.io (`drawio.py`) | editing by hand | One shape per card holding its words, number or icon; connectors attached to the cards. Icons are embedded as data URIs. Open at app.diagrams.net. |
| Excalidraw (`excalidraw.py`) | sketching | Hand-drawn style, no icons. Open at excalidraw.com. |
| Moda markup (`moda.py`) | a designed copy | Applied by a Claude session through the Moda connector (`canvas_create`, then `canvas_apply_markup`). No icons. |

The text is broken into lines once (`text.py`, a width table of DejaVu Sans measured in Chromium, the widest of the fonts used) and
every writer reuses those lines. `tests/test_figures.py` measures every line again in Chromium and compares the table with the
browser for every ASCII character.

## What was and was not checked

- The Facebook slides were exported from the demo figure and looked at on 2026-10-17 (portrait); the sizes, the text limit and the footer are tested. They were not uploaded to Facebook: that is the owner's act.
- Checked in tests: spec limits and hostile text, the icon files (hash, listing, allowlist), arrows that never cross a card or share a
  line (hundreds of random flows), text inside its card, the SVG against the store's own rule, the phone rule, the same bytes from the
  same spec, draw.io connectors attached with ports on the card edges, text staying text in all four formats.
- Checked by hand on 2026-10-17 with the demo figure: the Moda markup applied to a canvas through the Moda connector with no
  warning (the dashed lines use Moda's `dash` attribute); the draw.io file drawn by a local copy of the editor, version 14.6.12
  (npm `drawio-offline`, not JGraph's), in Chromium with no network: icons, connectors, lanes and ticks as expected. That is not the
  current app.diagrams.net, which was not seen.
- Not re-checked here: the Excalidraw board in the editor (its writer is the one github-radar drew with `@excalidraw/excalidraw`
  0.18.1; the structure is tested, the picture of this version was not looked at). The Japanese font of the Moda markup is named
  (`Noto Sans JP`) and not checked against Moda's font list.

## The connectors

Excalidraw, draw.io, Moda, Figma, Canva and Google Drive are connectors of the owner's claude.ai account, not files of a repository,
so there is nothing to move: they are available in any session of the account that has them on. `.claude/skills/visual-lessons/SKILL.md`
says what each is good for. No `.mcp.json` is added: `npx -y @drawio/mcp` would run an unpinned package from the network at each
session start for a server the hosted draw.io connector already covers.

## Adding an icon

Copy the file from the `lucide-static` package into `scripts/figures/icons/`, add `{"gloss": ..., "sha256": ...}` to `index.json`,
run `python3 -m scripts.figures icons --verify`. A file with an element or attribute outside the allowlist in `icons/__init__.py` is
refused. Licence and notice: `docs/third-party/lucide/`.
