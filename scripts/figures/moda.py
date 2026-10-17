"""The Moda design: a figure as Moda markup (XML), to be applied to a canvas with Moda's `canvas_apply_markup`.

Moda is a connector of the owner's Claude account (no script here can call it), so a build stores the markup and a Claude session with
the Moda connector applies it: docs/figures.md. The layout comes from `scene.py`. Every piece of text is XML-escaped and written only
as element content, never as an attribute or a tag, so a sentence cannot add an element, an image or a link to the design.
"""

from __future__ import annotations

from . import scene as scenes
from .text import esc

NAVY, INK, MUTED, CREAM, CORAL, SUN = "#0B1B3A", "#1F2A44", "#5B6478", "#FFF6E5", "#FF6B4A", "#FFC83D"
FILL = {"panel": "#FFFFFF", "card0": "#CFF5EE", "card1": "#FFD9CF", "card2": "#FFF0B8", "card3": "#DDE8FF", "note": NAVY, "badge": NAVY}
COLOR = {"title": NAVY, "muted": MUTED, "head": NAVY, "ink": INK}
# Be Vietnam Pro covers Vietnamese and Latin; measured on Moda it runs about 10% wider than text.width() (the DejaVu Sans table). The Japanese
# font is named but NOT checked against Moda's font list (docs/figures.md).
STYLE = scenes.Style(wscale=1.12, icons=False)
FONTS = {"vi": "Be Vietnam Pro", "en": "Be Vietnam Pro", "ja": "Noto Sans JP"}
SCALE = 2.0


def _n(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


def markup(spec: dict, scale: float = SCALE) -> str:
    scene = scenes.scaled(scenes.build(spec, STYLE), scale)
    font = FONTS[spec.get("lang", "vi")]
    out = [f'<!-- figure {esc(spec["id"])}: Moda canvas {_n(scene["w"])}x{_n(scene["h"])}; create it that size, then apply this markup -->',
           f'<content font-family="{esc(font)}">', f'<background fill="{CREAM}"/>']
    for item in scene["items"]:
        k = item["k"]
        if k == "rect":
            role = item["role"]
            stroke = f' stroke="{NAVY}" stroke-width="{_n(3 * scale / 2)}"' if role.startswith("card") else ' stroke="#CBD5E1" stroke-width="2"' if role == "panel" else ""
            out.append(f'<rectangle x="{_n(item["x"])}" y="{_n(item["y"])}" width="{_n(item["w"])}" height="{_n(item["h"])}" '
                       f'fill="{FILL[role]}"{stroke} corner-radius="{_n(item["r"])}"/>')
        elif k == "text":
            color = "#FFFFFF" if item["inside"] is not None and "note" in _role_of(scene, item["inside"]) else COLOR[item["color"]]
            out.append(f'<text x="{_n(item["x"])}" y="{_n(item["y"])}" width="{_n(item["w"])}" height="{_n(item["h"])}" '
                       f'font-size="{_n(item["px"])}" font-weight="{item["weight"]}" color="{color}" '
                       f'text-align="{item["align"]}" line-height="{item["lh"]}">{esc(item["text"])}</text>')
        elif k == "badge":
            out.append(f'<rectangle x="{_n(item["x"])}" y="{_n(item["y"])}" width="{_n(item["d"])}" height="{_n(item["d"])}" corner-radius="full" '
                       f'fill="{FILL["badge"]}" text="{esc(item["label"])}" font-size="{_n(item["d"] * 0.55)}" font-weight="800" color="#FFFFFF"/>')
        elif k == "tick":
            x, y, d = item["x"], item["y"], item["d"]
            a, b, c = (x + d * 0.27, y + d * 0.52), (x + d * 0.44, y + d * 0.70), (x + d * 0.75, y + d * 0.32)
            for p, q in ((a, b), (b, c)):
                out.append(f'<line x1="{_n(p[0])}" y1="{_n(p[1])}" x2="{_n(q[0])}" y2="{_n(q[1])}" stroke="{SUN}" stroke-width="{_n(2.5 * scale)}"/>')
        elif k in ("arrow", "line"):
            pts = item["pts"]
            width = 2.5 * scale if k == "arrow" else 1.5 * scale
            dash = ' dash="10 8"' if item["dashed"] else ""
            for i, (p, q) in enumerate(zip(pts, pts[1:])):
                head = ' arrow-end="triangle" pointer-length="14" pointer-width="14"' if k == "arrow" and i == len(pts) - 2 else ""
                color = CORAL if k == "arrow" else "#CBD5E1"
                out.append(f'<line x1="{_n(p[0])}" y1="{_n(p[1])}" x2="{_n(q[0])}" y2="{_n(q[1])}" stroke="{color}" stroke-width="{_n(width)}"{dash}{head}/>')
    out.append("</content>")
    return "\n".join(out) + "\n"


def _role_of(scene: dict, index: int) -> str:
    return scene["items"][index].get("role", "")
