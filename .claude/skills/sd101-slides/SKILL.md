---
name: sd101-slides
description: Build, resume or finish the Moda slide deck (and its PPTX) of a System Design lesson in system-design-101/vi. Use whenever a session is asked to make slides, a deck, a PowerPoint or "file ppt" for a lesson, "làm slide cho bài", "tạo file ppt trên Moda", "スライドを作る", or to continue the lesson decks another session started.
---

Build the Moda deck for: $ARGUMENTS

The order of work for one session is `docs/sd101-slides-handoff.md`; the claims, the style, the exports and the Moda watermark rule are
`docs/sd101-slides.md`. Read both before the first Moda call, and `CLAUDE.md` (*System Design slides: claim before you build*).

1. Check that the Moda connector is there (tools named `mcp__Moda_-_Slides_and_Designs__*`). If not, stop and say so; never draw the
   deck with another tool.
2. Claim first: `python3 scripts/sd101_slides.py claim <id> --publish` (or `--next N`). Never build a lesson the registry shows as
   `doing` or `done`.
3. `python3 scripts/sd101_slide_brief.py <id>` cuts the lesson into slide roles, names the canvas, fixes the slide count and the colour of
   each concept. It copies the lesson's lines; condensing them to 10 words and drawing the slide is your job. Add nothing the lesson
   does not say.
4. Build one slide per `canvas_apply_markup`, look at every slide with `canvas_screenshot`, then `sd101_slides.py finish ... --publish`,
   then export the deck as PPTX into the lesson's `slides/` folder and record it with `sd101_slides.py exported <id> --badged --publish`.
5. Never remove the `moda.app` badge from an export, never publish or upload anything to Facebook.
