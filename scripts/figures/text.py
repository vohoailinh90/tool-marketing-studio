"""Text measuring and wrapping shared by every writer, so the same words get the same lines on every picture."""

from __future__ import annotations

import re
import unicodedata
from xml.sax.saxutils import escape

# XML 1.0 forbids these; a stray one in a sentence would make an editor refuse the whole document.
XML_BAD = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff\ud800-\udfff]")


# Advance widths in 1/1000 em of DejaVu Sans, the widest of the fonts the figures name, measured once in Chromium: ASCII 32-126 in order,
# regular then bold. tests/test_figures.py measures them again. Any other font runs narrower, so these are safe for all of them.
_REGULAR = (
    318, 401, 460, 838, 636, 950, 780, 275, 390, 390, 500, 838, 318, 361, 318, 337, 636, 636, 636, 636, 636, 636, 636, 636, 636,
    636, 337, 337, 838, 838, 838, 531, 1000, 684, 686, 698, 770, 632, 575, 775, 752, 295, 295, 656, 557, 863, 748, 787, 603,
    787, 695, 635, 611, 732, 684, 989, 685, 611, 685, 390, 337, 390, 838, 500, 500, 613, 635, 550, 635, 615, 352, 635, 634, 278,
    278, 579, 278, 974, 634, 612, 635, 635, 411, 521, 392, 634, 592, 818, 592, 592, 525, 636, 337, 636, 838,
)
_BOLD = (
    348, 456, 521, 838, 696, 1002, 872, 306, 457, 457, 523, 838, 380, 415, 380, 365, 696, 696, 696, 696, 696, 696, 696, 696,
    696, 696, 400, 400, 838, 838, 838, 580, 1000, 774, 762, 734, 830, 683, 683, 821, 837, 372, 372, 775, 637, 995, 837, 850,
    733, 850, 770, 720, 682, 812, 774, 1103, 771, 724, 725, 457, 365, 457, 838, 500, 500, 675, 716, 593, 716, 678, 435, 716,
    712, 343, 343, 665, 343, 1042, 712, 687, 716, 716, 493, 595, 478, 712, 652, 924, 645, 652, 582, 712, 365, 712, 838,
)
_OTHER = {"·": (318, 380), "–": (500, 500), "—": (1000, 1000), "…": (1000, 1000), "’": (318, 380), "“": (518, 657), "”": (518, 657), "→": (838, 838), "×": (838, 838), "°": (500, 500), "€": (636, 696), "≥": (838, 838), "≤": (838, 838), "•": (590, 639)}              # (regular, bold)
FALLBACK = (700, 780)                  # any other narrow character: wider than every Latin letter, so a guess never overflows


def esc(text) -> str:
    """Text for an XML element or a double-quoted attribute: control characters dropped, the five specials escaped."""
    return escape(XML_BAD.sub("", str(text)), {'"': "&quot;"})


def one_line(text) -> str:
    """The text on one line, in canonical composed form (a decomposed Vietnamese letter becomes one character, so no accent is left to be cut off)."""
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", str(text)).strip())


def combining(ch: str) -> bool:
    """A mark that sits on the letter before it (an accent that has no composed form): never a place to end a line."""
    return unicodedata.category(ch)[0] == "M"


def wide(ch: str) -> bool:
    o = ord(ch)
    return o >= 0x1100 and (o <= 0x115F or 0x2E80 <= o <= 0xA4CF or 0xAC00 <= o <= 0xD7A3
                            or 0xF900 <= o <= 0xFAFF or 0xFE30 <= o <= 0xFE6F or 0xFF00 <= o <= 0xFF60
                            or 0x1F300 <= o <= 0x1FAFF)



def _em(c: str, bold: bool = False) -> float:
    if wide(c):
        return 1.0
    if " " <= c <= "~":
        return (_BOLD if bold else _REGULAR)[ord(c) - 32] / 1000
    if c in _OTHER:
        return _OTHER[c][bold] / 1000
    if combining(c):
        return 0.0                                          # drawn on the letter before it, advances nothing
    base = unicodedata.normalize("NFD", c)[0]               # ă, ơ, ế ... advance like the letter under the mark
    if " " <= base <= "~" and base != c:
        return _em(base, bold)
    return FALLBACK[bold] / 1000


def width(text: str, px: float, bold: bool = False) -> float:
    """Advance width of `text` at `px` in DejaVu Sans, regular or bold: the widest the figures' fonts run, so text never meets the shape beside it."""
    return sum(px * _em(c, bold) for c in text)


def _pieces(text: str) -> list[tuple[str, bool]]:
    """(piece, glued) for each place a line may end. A line can end at a space, and inside a word only next to a wide (CJK)
    character, since Japanese has no spaces to break at. A run of narrow characters inside such a word (`AI`, `GitHub`) stays
    whole, and `glued` means the piece continues the word before it: nothing is ever put between the pieces of one word."""
    out = []
    for word in str(text).split():
        runs, run = [], ""
        for ch in word:
            if wide(ch):
                if run:
                    runs.append(run)
                run = ""
                runs.append(ch)
            else:
                run += ch
        if run:
            runs.append(run)
        out += [(r, i > 0) for i, r in enumerate(runs)]
    return out


def wrap(text: str, px: float, max_w: float, scale: float = 1.0, bold: bool = False) -> list[str]:
    """Lines no wider than `max_w` (the estimate times `scale`), never changing the text: the spaces are exactly the text's own,
    and a word wider than the box is broken where the line ends rather than overflowing."""
    lines, cur = [], ""
    for tok, glued in _pieces(text):
        sep = "" if (not cur or glued) else " "
        if width(cur + sep + tok, px * scale, bold) <= max_w:
            cur += sep + tok
            continue
        if cur:
            lines.append(cur)
        cur = ""
        for ch in tok:
            if cur and not combining(ch) and width(cur + ch, px * scale, bold) > max_w:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
    if cur:
        lines.append(cur)
    return lines or [""]
