"""Webfonts cached on disk, so images render the same offline and on any machine.

Be Vietnam Pro (Vietnamese/English) and Noto Sans JP are SIL OFL fonts from Google
Fonts. They are downloaded once into `.fonts/` (gitignored — Noto Sans JP is ~5 MB a
weight) and served to the headless browser by the renderer. Without them the theme
falls back to system fonts (Segoe UI, Yu Gothic, Meiryo on Windows), which still
cover Vietnamese and Japanese.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.request import Request, urlopen

from .model import ROOT

FONT_DIR = ROOT / ".fonts"
FONT_ORIGIN = "https://fonts.studio.invalid"   # never resolved: the renderer answers these requests itself
WANTED = [("Be Vietnam Pro", w) for w in (500, 600, 700, 800)] + [("Noto Sans JP", w) for w in (500, 700, 800)]
CSS_API = "https://fonts.googleapis.com/css2?family={family}:wght@{weight}"
FONT_MAGIC = (b"\x00\x01\x00\x00", b"OTTO", b"true")


def font_file(family: str, weight: int, directory: Path = FONT_DIR) -> Path:
    return directory / f"{family.replace(' ', '')}-{weight}.ttf"


def _download(family: str, weight: int, path: Path) -> None:
    # A plain user agent makes Google Fonts answer with one TrueType file per weight.
    url = CSS_API.format(family=family.replace(" ", "+"), weight=weight)
    css = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8")
    sources = re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css)
    if len(sources) != 1:
        raise ValueError(f"expected one font file, got {len(sources)}")
    data = urlopen(sources[0], timeout=120).read()
    if not data.startswith(FONT_MAGIC):
        raise ValueError("downloaded file is not a TrueType/OpenType font")
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".part")
    partial.write_bytes(data)
    partial.replace(path)


def ensure_fonts(log=print, directory: Path = FONT_DIR, download: bool = True) -> list[tuple[str, int, Path]]:
    """The cached fonts, fetching missing ones when allowed. A failure only costs the font, never the render."""
    have = []
    for family, weight in WANTED:
        path = font_file(family, weight, directory)
        if not path.exists() and download:
            try:
                _download(family, weight, path)
            except Exception as exc:  # network, proxy, unexpected answer: fall back to system fonts
                log(f"font {family} {weight} not cached ({exc}); system fonts will be used")
        if path.exists():
            have.append((family, weight, path))
    return have


def font_face_css(fonts: list[tuple[str, int, Path]]) -> str:
    return "".join(
        f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};font-display:block;"
        f"src:url('{FONT_ORIGIN}/{path.name}') format('truetype');}}"
        for family, weight, path in fonts
    )
