"""What only a browser can say about a figure: how wide its text really runs, and what it looks like.

`text.width()` is an estimate. `measure()` draws the figure in Chromium (the one Playwright already drives for the studio's slides)
and compares the real width of every line with the box the layout gave it. `png()` rasterises a figure so a person can look at it.
Playwright is imported here only, so every other module works without it.
"""

from __future__ import annotations

from pathlib import Path

from . import scene as scenes, svg

SLACK = 0.5                           # px: a line may be this much wider than its box before it counts as overflowing


def _page(playwright, markup: str, width: int, height: int, scale: float = 1.0):
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)
    page.set_content('<!doctype html><html><body style="margin:0;background:#ffffff">' + markup + "</body></html>")
    return browser, page


def measure(spec: dict, st: scenes.Style | None = None) -> list[str]:
    """Lines of the figure that run wider than their box in Chromium, as sentences (empty when every line fits)."""
    from playwright.sync_api import sync_playwright

    st = st or svg.STYLE
    scene, markup = scenes.build(spec, st), svg.figure(spec, st)
    boxes: list[tuple[float | None, str]] = []              # what each <text> of the SVG is, in document order
    for item in scene["items"]:
        if item["k"] == "text":
            boxes += [(item["w"], line) for line in item["lines"]]
        elif item["k"] == "badge":
            boxes.append((None, item["label"]))
    with sync_playwright() as p:
        browser, page = _page(p, markup, scene["w"], scene["h"])
        try:
            widths = page.evaluate("[...document.querySelectorAll('svg text')].map(t => t.getComputedTextLength())")
        finally:
            browser.close()
    if len(widths) != len(boxes):
        return [f"the figure has {len(widths)} text elements, the layout expected {len(boxes)}"]
    return [f"{line!r} is {real:.1f} px wide in the browser, its box is {box:.1f} px"
            for (box, line), real in zip(boxes, widths) if box is not None and real > box + SLACK]


def png(markup: str, path: Path, width: int, height: int, scale: float = 2.0) -> None:
    """The SVG (or any markup that fills `width` x `height`) as a PNG, `scale` device pixels per px."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _page(p, markup, width, height, scale)
        try:
            page.screenshot(path=str(path))
        finally:
            browser.close()
