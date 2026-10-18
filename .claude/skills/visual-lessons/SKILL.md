---
name: visual-lessons
description: Make a System Design lesson's figure richer (icons, numbered steps, arrows, message sequences) with the figure toolkit, and choose between the image connectors available to the account (Excalidraw, draw.io, Moda, Canva, Figma). Use whenever a session redoes, adds or reviews a figure in system-design-101/vi, or is asked for a "more visual" lesson, an infographic, a diagram for a lesson, "hình trực quan hơn", "vẽ lại hình".
---

Make or redo a lesson figure: $ARGUMENTS

The figure of a lesson is `system-design-101/vi/diagrams/<id>-main.svg`. The toolkit in `scripts/figures/` draws it from a JSON
spec; read `docs/figures.md` for the spec, the commands and what was checked. This skill is the order of work and the choice of tool.

## Order of work

1. **Claim the lesson first** (`docs/sd101-claims.md`): a figure is part of the lesson body. Do not touch a lesson shown as `doing`.
2. **Decide what the figure must teach** in one sentence. One idea per figure; the lesson's text carries the rest. A figure that
   needs more than about 6 cards in one section or more than 4 cross links should be two sections or two lessons' worth of idea.
3. **Pick the section kinds**: `sequence` for who says what to whom in what order (handshakes, polling vs push, auth flows);
   `parts` for components and how data moves between them; `steps` for a procedure; `notes` for what to remember. Several sections
   may be stacked in one figure (the stored lessons often compare four things in four frames).
4. **Pick icons by meaning** from `python3 -m scripts.figures icons` (81 names). Name one for every card or actor, or for none.
   If nothing fits, use `box`; do not ask for a new icon unless the same concept is missing from several lessons.
5. **Write the spec** in Vietnamese for `vi` (written for the lesson, not translated from the source; no source image, no mention
   of the source's image host, no address in any text). Keep text short: the limits are in `spec.py`.
6. **`preview`** and look at the PNG. Fix the words, not the coordinates: there are none.
7. **`build`**, show the figure in `lesson.md` with alt text, add every abbreviation of two capitals or more to `## Từ viết tắt`,
   then `python3 -m scripts.figures check --browser` and `python3 scripts/sd101_check.py`.
8. **Facebook**: when the lesson is to be posted, run `python3 -m scripts.figures facebook system-design-101/figures/vi/<id>.json`
   and read the PNGs in `build/figures/facebook/<id>/`; `alt.txt` is the alt text. A slide refused for small text means the section is
   too big: split it in the spec. Never upload, approve or mark a post posted; the owner does.
9. The phone check is arithmetic, not a look: say in the lesson's metadata only what was really done (`verification.mobile` is
   `checked` only after a person or a browser really looked at widths 375 and 320). Do not mark a lesson `done`: review is not yours.

## Which tool for which job

| Need | Use | Notes |
|---|---|---|
| The figure that ships in a lesson | `scripts/figures` (SVG) | The only output that passes `sd101_check` as a figure. Deterministic, reviewable in git. |
| Tuning a figure by hand, an editable source | `render --format drawio` → app.diagrams.net, or the draw.io connector `create_diagram` | The connector returns a link that opens the editor with the XML; it does not give back a picture. |
| A hand-drawn sketch to think with | `render --format excalidraw`, or the Excalidraw connector `create_view` | Sketch style does not belong in the store's figures. |
| A designed infographic or social image | `render --format moda`, applied with Moda `canvas_create` + `canvas_apply_markup` | Free calls; image generation inside Moda is metered and not needed. Ask the owner about a brand kit before a new design. |
| A lesson's image for Facebook | `scripts.figures facebook` | The standard slides: `docs/figures.md`, *Images for Facebook*. |
| A lesson's slide deck for Facebook | Moda, claimed with `scripts/sd101_slides.py` | Its own product, not a figure: `docs/sd101-slides.md`. |
| Campaign posts for Facebook | the studio's own renderer (`studio.py render`) | Not a figure of a lesson; see `tool-campaign`. |
| Figma, Canva | only when the owner asks | They produce raster or proprietary files; the store accepts neither as a figure. |

Connectors belong to the owner's claude.ai account, not to this repository: they are there in a session only when the account has
them on. If one is missing, say so and use the SVG; do not add an `.mcp.json` entry to get it.

## Rules

- A session never writes SVG, coordinates or paths for a figure made with the toolkit; it writes the spec. Never edit a generated
  `-main.svg` by hand: change the spec and `build` again (`check` fails on a figure that differs from its spec).
- No icon, caption or arrow label that is not in the spec. No source image is traced or embedded (`DECISIONS.md`, "Ảnh nguồn").
- The toolkit refuses a figure whose text is too small for a phone; do not loosen `mobile.py` to make one pass: shorten the text.
- Images for Facebook follow the standard in `docs/figures.md` (sizes, text 30 px or more, footer, no address, alt text); `check` fails a
  figure that cannot be exported to it. A picture exported from Moda, Canva, Figma, draw.io or Excalidraw is not a standard image of
  a figure; a lesson's Moda slide deck is the one separate Facebook product (`docs/sd101-slides.md`).
- A new Moda canvas made to try a figure is a test canvas: tell the owner so they can delete it.
