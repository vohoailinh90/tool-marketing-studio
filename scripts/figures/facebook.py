"""A figure as Facebook-ready slides: one PNG per section, at the studio's own sizes, ready to upload by hand or to attach to a post.

The lesson figure is a 320 px column for a phone page; Facebook shows a picture at the width of the screen, cropped to 4:5 in the feed.
The standard here is the studio's own (mkt/page.py, mkt/theme.css), so a lesson's slides sit beside the campaign slides:
- the canvas is `FORMATS[format]`: portrait 1080x1350 (the default), square 1080x1080, landscape 1200x630; at most `MAX_SLIDES` slides;
- one section of the figure per slide, under the figure's title (and its subtitle on the first), scaled up as far as the canvas allows;
- the smallest text on a slide is at least `MIN_TEXT_PX` canvas px (the studio's body text runs 28-34 px); a section that cannot be
  scaled that far is refused, and the author splits it in the spec;
- the footer is the studio's: `author.handle` of studio.yaml bottom left when set, `n/N` bottom right;
- PNG, exactly the canvas size, opaque, under `MAX_BYTES`; no address on any slide (the spec check refuses one).
Nothing here posts anything: publishing stays the owner's act (CLAUDE.md, "Publishing is the owner's act").
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

from mkt.check import MAX_SLIDES
from mkt.page import FORMATS

from . import scene as scenes, svg
from .text import esc

MIN_TEXT_PX = 30                    # smallest text on a slide, in canvas px
PAD, FOOT = 36, 76                  # space round the picture; the footer band
MAX_BYTES = 4_000_000               # Facebook takes much more; a figure this size is a mistake
DEFAULT = "portrait"
FOOT_PX = 22                        # the studio's footer size (mkt/theme.css .slide__foot)


def handle(root: Path) -> str:
    """`author.handle` of studio.yaml, printed bottom left on every image; empty when unset or unreadable."""
    try:
        data = yaml.safe_load((root / "studio.yaml").read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return ""
    author = data.get("author") if isinstance(data, dict) else None
    return str(author.get("handle") or "").strip() if isinstance(author, dict) else ""


def plan(spec: dict, fmt: str = DEFAULT) -> tuple[list[dict], list[str]]:
    """The slides of a figure and what is wrong with them: [{"n", "k", "w", "h", "x", "y", "markup", "scene", "heading"}], [problem]."""
    if fmt not in FORMATS:
        return [], [f"format must be one of {', '.join(FORMATS)}"]
    width, height = FORMATS[fmt]
    sections = spec["sections"]
    problems: list[str] = []
    if len(sections) > MAX_SLIDES:
        problems.append(f"{spec['id']}: {len(sections)} sections make {len(sections)} slides; a post takes {MAX_SLIDES} at most")
    slides = []
    for n, section in enumerate(sections, 1):
        part = copy.deepcopy(spec)
        part["sections"] = [section]
        if n > 1:
            part.pop("subtitle", None)
        built = scenes.build(part, svg.STYLE)
        k = min((width - 2 * PAD) / built["w"], (height - PAD - FOOT) / built["h"])
        smallest = min(i["px"] for i in built["items"] if i["k"] == "text") * k
        where = f"{spec['id']} slide {n}"
        if smallest < MIN_TEXT_PX:
            problems.append(f"{where}: the smallest text would be {smallest:.0f} px on a {width}x{height} slide, the least is {MIN_TEXT_PX} px; "
                            f"split the section or shorten its text")
        w, h = built["w"] * k, built["h"] * k
        slides.append({"n": n, "k": k, "w": w, "h": h, "x": (width - w) / 2, "y": PAD + (height - PAD - FOOT - h) / 2,
                       "markup": svg.figure(part), "scene": built, "heading": section.get("heading") or ""})
    return slides, problems


def page(slide: dict, total: int, fmt: str, author: str) -> str:
    """One slide as a standalone page the size of the canvas: the picture, then the studio's footer."""
    width, height = FORMATS[fmt]
    picture = slide["markup"].replace("<svg ", f'<svg style="width:{slide["w"]:.1f}px;height:{slide["h"]:.1f}px;display:block" ', 1)
    left = f'<span>{esc(author)}</span>' if author else "<span></span>"
    return (f'<div style="position:relative;width:{width}px;height:{height}px;background:{svg.BG};overflow:hidden;font-family:{svg.FONT}">'
            f'<div style="position:absolute;left:{slide["x"]:.1f}px;top:{slide["y"]:.1f}px">{picture}</div>'
            f'<div style="position:absolute;left:{PAD}px;right:{PAD}px;bottom:{(FOOT - FOOT_PX) / 2:.0f}px;display:flex;justify-content:space-between;'
            f'font-size:{FOOT_PX}px;font-weight:600;color:{svg.MUTED};line-height:1">{left}<span>{slide["n"]}/{total}</span></div></div>')


def png_problems(path: Path, fmt: str = DEFAULT) -> list[str]:
    """What is wrong with a written slide: not a PNG, not the canvas size, too heavy."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 24:
        return [f"{path.name} is not a PNG"]
    found = []
    size = (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big"))
    if size != FORMATS[fmt]:
        found.append(f"{path.name} is {size[0]}x{size[1]}, the {fmt} canvas is {FORMATS[fmt][0]}x{FORMATS[fmt][1]}")
    if len(data) > MAX_BYTES:
        found.append(f"{path.name} is {len(data)} bytes, the most is {MAX_BYTES}")
    return found


def alt_text(spec: dict, slides: list[dict]) -> str:
    """One line per slide, from the spec's own words: the figure's description for all of them, then each slide's heading."""
    lines = [spec["desc"].strip()]
    lines += [f"{s['n']}/{len(slides)}: {s['heading'] or spec['title']}" for s in slides]
    return "\n".join(lines) + "\n"


def export(spec: dict, out: Path, root: Path, fmt: str = DEFAULT) -> tuple[list[Path], list[str]]:
    """Writes `out/<id>/NN.png` and `alt.txt`; returns the files and the problems (nothing is written when the plan has problems)."""
    from . import browser

    slides, problems = plan(spec, fmt)
    if problems:
        return [], problems
    folder = out / spec["id"]
    folder.mkdir(parents=True, exist_ok=True)
    for stale in folder.glob("[0-9][0-9].png"):
        stale.unlink()
    author = handle(root)
    files = []
    for slide in slides:
        path = folder / f"{slide['n']:02d}.png"
        browser.png(page(slide, len(slides), fmt, author), path, *FORMATS[fmt], 1.0)
        problems += png_problems(path, fmt)
        files.append(path)
    (folder / "alt.txt").write_text(alt_text(spec, slides), encoding="utf-8")
    return files, problems

