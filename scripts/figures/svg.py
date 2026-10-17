"""The lesson figure: a scene as one self-contained SVG, in the look of the figures already in system-design-101/vi/diagrams.

Only plain drawing elements (rect, circle, line, polyline, path, text, g, marker), no <image>, no link, no script, no style sheet:
what `scripts/sd101_check.py` accepts, and what a reader's browser, GitHub and a screen reader show the same way. Icons are drawn
from the shapes of the closed set in `icons/`, never from a file the spec points to. The same scene always gives the same bytes.
"""

from __future__ import annotations

from . import icons, scene as scenes
from .text import esc

FONT = "DejaVu Sans, Arial, sans-serif"
BG, INK, MUTED, LINE, ARROW = "#f8fafc", "#0f172a", "#475569", "#cbd5e1", "#334155"
# fill and accent per colour: light fills keep INK text above 7:1, the accents carry white pictograms and numbers.
LAYERS = [("#dbeafe", "#1d4ed8"), ("#ccfbf1", "#0f766e"), ("#fef3c7", "#b45309"), ("#ede9fe", "#6d28d9")]
FILL = {"panel": ("#ffffff", LINE), "note": ("#dcfce7", "#16a34a"), **{f"card{i}": f for i, f in enumerate(LAYERS)}}
ACCENT = {"note": "#16a34a", **{f"card{i}": f[1] for i, f in enumerate(LAYERS)}}
COLOR = {"title": INK, "muted": MUTED, "head": INK, "ink": INK}
STYLE = scenes.Style(wscale=1.02)      # text.width() is DejaVu Sans itself; the 2% is for kerning and rounding (tests/test_figures.py re-measures every line)


def n(value: float) -> str:
    """A coordinate: at most one decimal, no trailing zero."""
    return f"{value:.1f}".rstrip("0").rstrip(".")


def _points(pts) -> str:
    return " ".join(f"{n(x)},{n(y)}" for x, y in pts)


def _text(item: dict) -> str:
    """One <text> per line, so a line is a string of its own for a screen reader and for the abbreviation check."""
    out = []
    px, lh = item["px"], item["lh"]
    anchor, x = ("middle", item["x"] + item["w"] / 2) if item["align"] == "center" else ("start", item["x"])
    weight = "bold" if item["weight"] >= 700 else "normal"
    for i, line in enumerate(item["lines"]):
        base = item["y"] + i * px * lh + px * 0.5 * (lh - 1) + px * 0.8
        out.append(f'<text x="{n(x)}" y="{n(base)}" font-size="{n(px)}" fill="{COLOR[item["color"]]}" font-weight="{weight}" '
                   f'text-anchor="{anchor}">{esc(line)}</text>')
    return "\n".join(out)


def figure(spec: dict, st: scenes.Style | None = None) -> str:
    scene = scenes.build(spec, st or STYLE)
    w, h = scene["w"], scene["h"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{esc(scene["title"])}</title>',
           f'<desc id="desc">{esc(scene["desc"])}</desc>',
           f'<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
           f'<path d="M0,0 L6,3 L0,6" fill="none" stroke="{ARROW}" stroke-width="1.5"/></marker></defs>',
           f'<rect width="{w}" height="{h}" fill="{BG}"/>',
           f'<g font-family="{FONT}" fill="{INK}">']
    for item in scene["items"]:
        kind = item["k"]
        if kind == "rect":
            fill, stroke = FILL[item["role"]]
            out.append(f'<rect x="{n(item["x"])}" y="{n(item["y"])}" width="{n(item["w"])}" height="{n(item["h"])}" rx="{n(item["r"])}" '
                       f'fill="{fill}" stroke="{stroke}" stroke-width="{1 if item["role"] == "panel" else 1.5}"/>')
        elif kind == "text":
            out.append(_text(item))
        elif kind == "icon":
            out.append(icons.group(item["name"], item["x"], item["y"], item["d"], tile=ACCENT[item["role"]]))
        elif kind == "badge":
            d = item["d"]
            out.append(f'<circle cx="{n(item["x"] + d / 2)}" cy="{n(item["y"] + d / 2)}" r="{n(d / 2)}" fill="{ACCENT[item["role"]]}"/>')
            out.append(f'<text x="{n(item["x"] + d / 2)}" y="{n(item["y"] + d / 2 + 5.5)}" font-size="16" fill="#ffffff" font-weight="bold" '
                       f'text-anchor="middle">{esc(item["label"])}</text>')
        elif kind == "tick":
            x, y, d = item["x"], item["y"], item["d"]
            out.append(f'<circle cx="{n(x + d / 2)}" cy="{n(y + d / 2)}" r="{n(d / 2)}" fill="{ACCENT["note"]}"/>')
            out.append(f'<polyline points="{_points([(x + d * .27, y + d * .52), (x + d * .44, y + d * .70), (x + d * .75, y + d * .32)])}" '
                       f'fill="none" stroke="#ffffff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
        elif kind == "arrow":
            dash = ' stroke-dasharray="5 4"' if item["dashed"] else ""
            out.append(f'<polyline points="{_points(item["pts"])}" fill="none" stroke="{ARROW}" stroke-width="1.8"{dash} '
                       f'stroke-linejoin="round" marker-end="url(#arrow)"/>')
        elif kind == "line":
            out.append(f'<polyline points="{_points(item["pts"])}" fill="none" stroke="{LINE}" stroke-width="2" stroke-dasharray="4 4"/>')
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"
