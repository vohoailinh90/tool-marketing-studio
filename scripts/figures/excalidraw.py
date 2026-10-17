"""The hand-drawn board: a figure as an `.excalidraw` file, open it at excalidraw.com and edit it by hand.

The layout comes from `scene.py`; this module only writes it in Excalidraw's JSON. Text is the spec's own, set in Excalifont (the
font Excalidraw ships), colours are the pastel fills Excalidraw offers, and seeds are numbered, so the same spec always gives the
same bytes. No pictograms (the board is for sketching by hand); the SVG and the draw.io file carry them.
"""

from __future__ import annotations

import json

from . import scene as scenes
from .text import width

INK, MUTED = "#1e1e1e", "#555555"
FILL = {"panel": "#ffffff", "card0": "#a5d8ff", "card1": "#b2f2bb", "card2": "#ffec99", "card3": "#d0bfff", "note": "#d3f9d8", "badge": "#ffffff"}
COLOR = {"title": INK, "muted": MUTED, "head": INK, "ink": INK}
STYLE = scenes.Style(icons=False)
FONT = 5                       # Excalifont
SCALE = 2.0                    # the editor file is twice the lesson figure: room to move things about


class _Writer:
    def __init__(self) -> None:
        self.elements: list[dict] = []

    def add(self, kind: str, x: float, y: float, w: float, h: float, **kw) -> dict:
        n = len(self.elements) + 1
        element = {"id": f"f{n:04d}", "type": kind, "x": round(x, 1), "y": round(y, 1), "width": round(w, 1), "height": round(h, 1),
                   "angle": 0, "strokeColor": INK, "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 2,
                   "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
                   "seed": 1000 + n * 37, "version": 1, "versionNonce": 5000 + n * 53, "isDeleted": False, "boundElements": None,
                   "updated": 1, "link": None, "locked": False}
        element.update(kw)
        self.elements.append(element)
        return element

    def line(self, pts: list[tuple[float, float]], *, arrow: bool, dashed: bool = False) -> None:
        x0, y0 = pts[0]
        rel = [[round(x - x0, 1), round(y - y0, 1)] for x, y in pts]
        xs, ys = [p[0] for p in rel], [p[1] for p in rel]
        self.add("arrow" if arrow else "line", x0, y0, max(xs) - min(xs), max(ys) - min(ys), points=rel, roundness=None,
                 lastCommittedPoint=None, startBinding=None, endBinding=None, startArrowhead=None,
                 endArrowhead="arrow" if arrow else None, elbowed=False, strokeStyle="dashed" if dashed else "solid")

    def text(self, x: float, y: float, s: str, px: float, lh: float, color: str, h: float | None = None) -> None:
        w = max(width(line, px) for line in s.split("\n"))
        self.add("text", x, y, w, h if h is not None else len(s.split("\n")) * px * lh, strokeWidth=1, text=s, originalText=s, fontSize=px,
                 fontFamily=FONT, textAlign="left", verticalAlign="top", containerId=None, autoResize=True, lineHeight=lh, strokeColor=color)


def board(spec: dict, scale: float = SCALE) -> str:
    scene = scenes.scaled(scenes.build(spec, STYLE), scale)
    out = _Writer()
    for item in scene["items"]:
        k = item["k"]
        if k == "rect":
            panel = item["role"] == "panel"
            out.add("rectangle", item["x"], item["y"], item["w"], item["h"], backgroundColor=FILL[item["role"]],
                    strokeStyle="dashed" if panel else "solid", roundness={"type": 3})
        elif k == "text":
            body = "\n".join(item["lines"])
            w = max(width(line, item["px"]) for line in item["lines"])
            x = item["x"] + (item["w"] - w) / 2 if item["align"] == "center" else item["x"]
            out.add("text", x, item["y"], w, item["h"], strokeWidth=1, text=body, originalText=body, fontSize=item["px"],
                    fontFamily=FONT, textAlign="left", verticalAlign="top", containerId=None, autoResize=True,
                    lineHeight=item["lh"], strokeColor=COLOR[item["color"]])
        elif k == "badge":
            d = item["d"]
            out.add("ellipse", item["x"], item["y"], d, d, backgroundColor=FILL["badge"], roundness={"type": 2})
            px = d * 0.9
            out.text(item["x"] + (d - width(item["label"], px)) / 2, item["y"] + (d - px * 1.25) / 2, item["label"], px, 1.25, INK)
        elif k == "tick":
            x, y, d = item["x"], item["y"], item["d"]
            out.add("ellipse", x, y, d, d, backgroundColor=FILL["badge"], roundness={"type": 2})
            out.line([(x + d * 0.27, y + d * 0.52), (x + d * 0.44, y + d * 0.70), (x + d * 0.75, y + d * 0.32)], arrow=False)
        elif k == "arrow":
            out.line(item["pts"], arrow=True, dashed=item["dashed"])
        elif k == "line":
            out.line(item["pts"], arrow=False, dashed=item["dashed"])
    # One element per line: a change to one card shows as a one-line diff in git.
    lines = ",\n".join(json.dumps(e, ensure_ascii=False, separators=(",", ":")) for e in out.elements)
    return ('{"type":"excalidraw","version":2,"source":"https://excalidraw.com","elements":[\n' + lines
            + '\n],"appState":{"viewBackgroundColor":"#ffffff","gridSize":20},"files":{}}\n')
