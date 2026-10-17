"""Whether a figure can be read on a phone, as arithmetic.

The store's rule (brainstorm/system-design-101-vi/DECISIONS.md, "Hình trên điện thoại"): no horizontal scrolling, and the text a
reader has to read is at least 14 px at a 375 px screen and at least 12 px at a 320 px screen, where the figure is shown at
min(1, (screen - 32) / figure width) of its size. That is computable from the SVG, so it is a check and not a reviewer's guess.
It does not replace looking at the figure on a phone or on GitHub: it says the sizes are right, not that the figure reads well.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from .text import width

SCREENS = ((375, 14.0), (320, 12.0))          # screen width, smallest effective px of text
GUTTER = 32                                   # what a lesson page keeps free beside a figure
FIT = 1.02                                    # what text.width() is multiplied by, as the figure style does (browser.measure() is the exact test)


def _number(value: str | None) -> float | None:
    match = re.match(r"\s*(-?\d+(?:\.\d+)?)", value or "")
    return float(match.group(1)) if match else None


def check(markup: str) -> list[str]:
    """Reasons the figure is not readable on a phone (empty when it is): text too small once the figure is scaled to the screen, or
    text that runs past the edge of the drawing."""
    try:
        root = ET.fromstring(markup)
    except ET.ParseError as exc:
        return [f"not well-formed XML: {exc}"]
    box = [_number(part) for part in re.split(r"[\s,]+", root.get("viewBox", "").strip())]
    if len(box) != 4 or None in box:
        return ["the figure has no viewBox"]
    size = box[2]
    found: list[str] = []
    for element in root.iter("{http://www.w3.org/2000/svg}text"):
        px = _number(element.get("font-size"))
        label = "".join(element.itertext()).strip()
        if px is None:
            found.append(f"the text {label!r} has no font-size")
            continue
        for screen, least in SCREENS:
            effective = px * min(1.0, (screen - GUTTER) / size)
            if effective < least:
                found.append(f"the text {label!r} is {effective:.1f} px on a {screen} px screen, the least is {least:g} px")
        x = _number(element.get("x")) or 0.0
        run = width(label, px, element.get("font-weight") == "bold") * FIT
        anchor = element.get("text-anchor", "start")
        left = x - (run if anchor == "end" else run / 2 if anchor == "middle" else 0)
        if left < -0.5 or left + run > size + 0.5:
            found.append(f"the text {label!r} runs past the edge of the drawing")
    return found
