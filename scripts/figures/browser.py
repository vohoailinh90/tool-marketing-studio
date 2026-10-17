"""What only a browser can say about a figure: how wide its text really runs, and what it looks like.

`text.width()` is an estimate. `measure()` draws the figure in Chromium (the one Playwright already drives for the studio's slides)
and compares the real width of every line with the box the layout gave it. `png()` rasterises a figure so a person can look at it.
Playwright is imported here only, so every other module works without it.
"""

from __future__ import annotations

import contextlib
from pathlib import Path

from . import scene as scenes, svg
from .files import write_atomic

class Unavailable(RuntimeError):
    """Playwright or its Chromium cannot be used here; the message says why."""


class Failed(Unavailable):
    """Chromium started and then failed (a crash, a timeout): installing it again would not help."""


def _playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise Unavailable("playwright is not installed") from exc
    return sync_playwright


@contextlib.contextmanager
def _drawing():
    """Playwright's own errors, whatever step raised them, are `Failed`: a sentence for the owner, not a traceback. Anything else is a bug and passes."""
    from playwright.sync_api import Error
    try:
        yield
    except Error as exc:
        first = str(exc).strip().splitlines()
        raise Failed(first[0] if first else type(exc).__name__) from exc


SLACK = 0.5                           # px: a line may be this much wider than its box before it counts as overflowing


def _page(playwright, markup: str, width: int, height: int, scale: float = 1.0):
    try:
        browser = playwright.chromium.launch()
    except Exception as exc:
        raise Unavailable(str(exc).strip().splitlines()[0] if str(exc).strip() else "Chromium did not start") from exc
    try:
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)
        page.set_content('<!doctype html><html><body style="margin:0;background:#ffffff">' + markup + "</body></html>")
    except BaseException:                                       # a browser that started but cannot show the page is not left running
        with contextlib.suppress(Exception):
            browser.close()
        raise
    return browser, page


def measure(spec: dict, st: scenes.Style | None = None) -> list[str]:
    """Lines of the figure that run wider than their box in Chromium, as sentences (empty when every line fits)."""
    sync_playwright = _playwright()
    st = st or svg.STYLE
    scene, markup = scenes.build(spec, st), svg.figure(spec, st)
    boxes: list[tuple[float | None, str]] = []              # what each <text> of the SVG is, in document order
    for item in scene["items"]:
        if item["k"] == "text":
            boxes += [(item["w"], line) for line in item["lines"]]
        elif item["k"] == "badge":
            boxes.append((None, item["label"]))
    with _drawing(), sync_playwright() as p:
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
    sync_playwright = _playwright()
    with _drawing(), sync_playwright() as p:
        browser, page = _page(p, markup, width, height, scale)
        try:
            data = page.screenshot()                          # the bytes, not a path: Playwright would write a path in place
        finally:
            browser.close()
    write_atomic(path, data)
