"""Wraps a layout body in a full HTML page: theme, fonts, header chip and footer."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from .layouts import Ctx, render_body
from .text import esc

FORMATS = {
    "portrait": (1080, 1350),   # Facebook/Instagram feed, 4:5 — the default
    "square": (1080, 1080),
    "landscape": (1200, 630),   # link preview / cover
}

FONTS_URL = ("https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;600;700;800"
             "&family=Noto+Sans+JP:wght@500;700;800&display=block")

THEME_CSS = (Path(__file__).with_name("theme.css")).read_text(encoding="utf-8")

# Shrinks text in steps until the body fits, and reports whether it still overflows.
# The renderer turns a remaining overflow into a warning instead of a clipped image nobody notices.
FIT_JS = """
window.fit = async () => {
  await document.fonts.ready;
  const root = document.documentElement;
  const body = document.querySelector('.slide__body');
  const need = () => {
    const kids = [...body.children];
    const gap = parseFloat(getComputedStyle(body).rowGap) || 0;
    const h = kids.reduce((sum, k) => sum + k.getBoundingClientRect().height, 0) + gap * Math.max(kids.length - 1, 0);
    return {h, w: Math.max(body.scrollWidth, ...kids.map(k => k.scrollWidth))};
  };
  const over = () => { const n = need(); return n.h > body.clientHeight + 1 || n.w > body.clientWidth + 1; };
  let scale = 1;
  while (over() && scale > 0.7) {
    scale = Math.round((scale - 0.04) * 100) / 100;
    root.style.setProperty('--scale', scale);
  }
  return {scale, overflow: over()};
};
"""


# The page is opened from a file:// URL in a browser with JavaScript on, so even though every
# string is escaped, the page also declares what it may load: no frames, no network but the
# fonts, no script but fit() itself. A slip in escaping cannot then read a local file into
# the image or call out.
FIT_HASH = base64.b64encode(hashlib.sha256(FIT_JS.encode("utf-8")).digest()).decode("ascii")
CSP = ("default-src 'none'; "
       f"script-src 'sha256-{FIT_HASH}'; "
       "style-src 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.studio.invalid https://fonts.gstatic.com; "
       "img-src file: data:")


def build_page(slide: dict, ctx: Ctx, *, brand: dict, tool_name: str, series: str,
               handle: str, index: int, total: int, fmt_name: str, font_css: str = "") -> str:
    """One slide as a standalone page. With `font_css` (cached fonts) the page needs no network;
    without it, it links Google Fonts and falls back to system fonts when offline."""
    width, height = FORMATS[fmt_name]
    body = render_body(slide, ctx)
    accent = brand.get("accent", "#2563eb")
    emoji = esc(brand.get("emoji", ""))
    series_html = f'<span class="series">{esc(series)}</span>' if series else "<span></span>"
    handle_html = f'<span class="handle">{esc(handle)}</span>' if handle else "<span></span>"
    style = (f"--w:{width}px;--h:{height}px;--accent:{esc(accent)};"
             "--accent-soft:color-mix(in srgb, var(--accent) 12%, white);"
             "--accent-strong:color-mix(in srgb, var(--accent) 78%, black);")
    fonts = (f"<style>{font_css}</style>" if font_css
             else f'<link rel="stylesheet" href="{FONTS_URL}">')
    return f"""<!doctype html>
<html lang="{esc(ctx.lang)}">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="viewport" content="width={width}">
{fonts}
<style>{THEME_CSS}</style>
<script>{FIT_JS}</script>
</head>
<body>
<main class="slide slide--{esc(slide['layout'])} fmt-{esc(fmt_name)}" style="{style}">
  <header class="slide__top"><span class="chip">{emoji} {esc(tool_name)}</span>{series_html}</header>
  <section class="slide__body">{body}</section>
  <footer class="slide__foot">{handle_html}<span class="page">{index}/{total}</span></footer>
</main>
</body>
</html>
"""
