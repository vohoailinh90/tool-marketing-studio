"""The draw.io diagram: a figure as a `.drawio` file, open it at app.diagrams.net and edit it by hand.

The layout comes from `scene.py`; this module only writes it in draw.io's XML. What draw.io adds over the other files:
- every card is one shape that holds its own text, so dragging a card moves its words, number, tick and pictogram with it;
- the arrows between cards are connectors attached to the cards (`source`/`target`) with the lane the layout gave them, so they follow
  a card that is moved;
- every card or actor carries its pictogram from the closed set in `icons/` when the spec names them.
Text is the spec's own, set in Helvetica (draw.io's default; it falls back by itself for Vietnamese and Japanese). Nothing here calls a
model or the network, ids are numbered, and the same spec always gives the same bytes.
"""

from __future__ import annotations

import html

from . import icons, scene as scenes, svg
from .text import XML_BAD

STYLE = scenes.Style()
FONT = "Helvetica"
SCALE = 2.0                 # the editor file is twice the lesson figure: room to move things about
ICON_PX = 64                # the size the icon is drawn at inside its own file; draw.io scales it to the card, so it does not follow the scale
FIXED = "movable=0;resizable=0;rotatable=0;deletable=0;editable=0;connectable=0;"      # the page behind the diagram


def _attr(text) -> str:
    return html.escape(XML_BAD.sub("", str(text)), quote=True)


def _n(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def _label(blocks: list[dict]) -> str:
    """The HTML of one label: a block per text item, the lines exactly as `scene` broke them."""
    parts, previous = [], None
    for b in blocks:
        gap = 0 if previous is None else max(round(b["y"] - (previous["y"] + previous["h"])), 0)
        lines = "<br>".join(html.escape(XML_BAD.sub("", line), quote=False) for line in b["lines"])
        style = f"font-size:{_n(b['px'])}px;font-weight:{'bold' if b['weight'] >= 700 else 'normal'};line-height:{b['lh']};color:{svg.COLOR[b['color']]}"
        parts.append(f'<div style="{style};margin-top:{gap}px">{lines}</div>' if gap else f'<div style="{style}">{lines}</div>')
        previous = b
    return "".join(parts)


class _Cells:
    def __init__(self) -> None:
        self.rows: list[str] = []
        self.count = 1                                     # ids 0 and 1 are the root and the layer

    def new_id(self) -> str:
        self.count += 1
        return f"c{self.count}"

    def vertex(self, x, y, w, h, style: str, value: str = "", parent: str = "1") -> str:
        cid = self.new_id()
        self.rows.append(f'<mxCell id="{cid}" value="{_attr(value)}" style="{style}" vertex="1" parent="{parent}">'
                         f'<mxGeometry x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" as="geometry"/></mxCell>')
        return cid

    def edge(self, style: str, *, source: str | None = None, target: str | None = None, waypoints=(), ends=None, parent: str = "1") -> str:
        cid = self.new_id()
        terms = (f' source="{source}"' if source else "") + (f' target="{target}"' if target else "")
        geometry = '<mxGeometry relative="1" as="geometry">'
        if ends:
            geometry += (f'<mxPoint x="{_n(ends[0][0])}" y="{_n(ends[0][1])}" as="sourcePoint"/>'
                         f'<mxPoint x="{_n(ends[1][0])}" y="{_n(ends[1][1])}" as="targetPoint"/>')
        if waypoints:
            geometry += '<Array as="points">' + "".join(f'<mxPoint x="{_n(x, 2)}" y="{_n(y, 2)}"/>' for x, y in waypoints) + "</Array>"
        self.rows.append(f'<mxCell id="{cid}" style="{style}" edge="1" parent="{parent}"{terms}>{geometry}</mxGeometry></mxCell>')
        return cid


def _connector(scale: float, *, dashed: bool = False, hop: bool = False, **ports: float) -> str:
    base = (f"html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;endArrow=block;endFill=1;endSize=4;strokeColor={svg.ARROW};"
            f"strokeWidth={_n(1.8 * scale)};exitPerimeter=0;entryPerimeter=0;" + ("dashed=1;" if dashed else "")
            + (f"jumpStyle=arc;jumpSize={_n(5 * scale)};" if hop else ""))
    return base + "".join(f"{k}={_n(v, 4)};" for k, v in ports.items())


def diagram(spec: dict, scale: float = SCALE) -> str:
    scene = scenes.scaled(scenes.build(spec, STYLE), scale)
    items = scene["items"]
    cells = _Cells()
    cells.vertex(0, 0, scene["w"], scene["h"], f"rounded=0;html=1;fillColor={svg.BG};strokeColor=none;{FIXED}")

    inside: dict[int, list[dict]] = {}                       # the text items that sit in each rectangle, in order
    for item in items:
        if item["k"] == "text" and item["inside"] is not None:
            inside.setdefault(item["inside"], []).append(item)

    font = f"fontFamily={FONT};"
    ids: dict[int, str] = {}                                 # scene index of a rectangle -> its cell id
    boxes: dict[int, dict] = {}
    card = None                                              # the rectangle the next badge, tick or pictogram belongs to
    for index, item in enumerate(items):
        kind = item["k"]
        if kind == "rect":
            blocks = inside.get(index, [])
            fill, stroke = svg.FILL[item["role"]]
            style = (f"rounded=1;absoluteArcSize=1;arcSize={_n(item['r'])};html=1;whiteSpace=wrap;fillColor={fill};strokeColor={stroke};"
                     f"strokeWidth={_n((1 if item['role'] == 'panel' else 1.5) * scale)};{font}")
            if blocks and blocks[0]["align"] == "center":
                first = blocks[0]
                style += (f"align=center;verticalAlign=top;spacingTop={_n(first['y'] - item['y'])};spacingLeft={_n(first['x'] - item['x'])};"
                          f"spacingRight={_n(item['x'] + item['w'] - first['x'] - first['w'])};spacing=0;")
            elif blocks:
                first = blocks[0]
                style += (f"align=left;verticalAlign=top;spacingTop={_n(first['y'] - item['y'])};spacingLeft={_n(first['x'] - item['x'])};"
                          f"spacingRight={_n(item['x'] + item['w'] - first['x'] - first['w'])};spacing=0;")
            ids[index], boxes[index], card = cells.vertex(item["x"], item["y"], item["w"], item["h"], style, _label(blocks) if blocks else ""), item, index
        elif kind == "text" and item["inside"] is None:
            style = (f"text;html=1;whiteSpace=wrap;align={item['align']};verticalAlign=top;spacing=0;{font}"
                     f"fontSize={_n(item['px'])};fontColor={svg.COLOR[item['color']]};{'fontStyle=1;' if item['weight'] >= 700 else ''}")
            cells.vertex(item["x"], item["y"], item["w"], item["h"], style, _label([item]))
        elif kind == "badge":
            c = boxes[card]
            cells.vertex(item["x"] - c["x"], item["y"] - c["y"], item["d"], item["d"],
                         f"ellipse;html=1;aspect=fixed;fillColor={svg.ACCENT[item['role']]};strokeColor=none;fontColor=#FFFFFF;"
                         f"fontSize={_n(item['d'] * 0.55)};fontStyle=1;{font}", item["label"], parent=ids[card])
        elif kind == "icon":
            c = boxes[card]
            cells.vertex(item["x"] - c["x"], item["y"] - c["y"], item["d"], item["d"],
                         f"shape=image;html=1;aspect=fixed;imageAspect=0;image={icons.data_uri(item['name'], size=ICON_PX, tile=svg.ACCENT[item['role']])};",
                         parent=ids[card])
        elif kind == "tick":
            c = boxes[card]
            x, y, d = item["x"] - c["x"], item["y"] - c["y"], item["d"]
            cells.vertex(x, y, d, d, f"ellipse;html=1;aspect=fixed;fillColor={svg.ACCENT['note']};strokeColor=none;", parent=ids[card])
            cells.edge(f"html=1;endArrow=none;strokeColor=#FFFFFF;strokeWidth={_n(2.4 * scale)};", parent=ids[card],
                       ends=((x + d * .27, y + d * .52), (x + d * .75, y + d * .32)), waypoints=[(x + d * .44, y + d * .70)])

    for item in items:
        kind = item["k"]
        if kind == "arrow" and item["src"] is not None:      # a connector between two cards: ports and lane come from the layout
            a, b = boxes[item["src"]], boxes[item["dst"]]
            (x0, y0), (x1, y1) = item["pts"][0], item["pts"][-1]
            fraction = lambda value, origin, size: min(1.0, max(0.0, (value - origin) / size))     # the head stops 2 px off the card: attach on its edge
            ports = dict(exitX=fraction(x0, a["x"], a["w"]), exitY=fraction(y0, a["y"], a["h"]), entryX=fraction(x1, b["x"], b["w"]), entryY=fraction(y1, b["y"], b["h"]))
            cells.edge(_connector(scale, dashed=item["dashed"], hop=len(item["pts"]) > 2, **ports), source=ids[item["src"]], target=ids[item["dst"]],
                       waypoints=item["pts"][1:-1])
        elif kind == "arrow":                                # a message between two lifelines: free ends
            cells.edge(_connector(scale, dashed=item["dashed"]), ends=(item["pts"][0], item["pts"][-1]))
        elif kind == "line":
            cells.edge(f"html=1;endArrow=none;dashed=1;strokeColor={svg.LINE};strokeWidth={_n(2 * scale)};", ends=(item["pts"][0], item["pts"][-1]))

    name = _attr(scene["title"])
    model = (f'<mxGraphModel dx="{_n(scene["w"])}" dy="{_n(scene["h"])}" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
             f'fold="1" page="1" pageScale="1" pageWidth="{_n(scene["w"])}" pageHeight="{_n(scene["h"])}" background="{svg.BG}" math="0" shadow="0">'
             '<root><mxCell id="0"/><mxCell id="1" parent="0"/>\n' + "\n".join(cells.rows) + "\n</root></mxGraphModel>")
    return f'<mxfile host="figures" compressed="false"><diagram id="{_attr(spec["id"])}" name="{name}">{model}</diagram></mxfile>\n'
