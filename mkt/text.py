"""Small text helpers shared by layouts, captions and checks."""

from __future__ import annotations

import html
import re

_STRONG = re.compile(r"\*\*(.+?)\*\*", re.S)
_STRIKE = re.compile(r"~~(.+?)~~", re.S)

# Fixed words the layouts print themselves. A slide can override each one.
UI = {
    "before": {"vi": "Trước đây", "ja": "これまで", "en": "Before"},
    "after": {"vi": "Với tool", "ja": "ツール導入後", "en": "With the tool"},
    "total": {"vi": "Tổng", "ja": "合計", "en": "Total"},
    "scan": {"vi": "Quét mã QR để mở", "ja": "QRコードから開けます", "en": "Scan the QR code to open"},
    "link_in_comment": {
        "vi": "Link ở comment đầu tiên 👇",
        "ja": "リンクは最初のコメントに 👇",
        "en": "Link in the first comment 👇",
    },
    "comment": {"vi": "Comment", "ja": "コメントで", "en": "Comment"},
    "poll_hint": {
        "vi": "Trả lời bằng 1 chữ cái ở phần comment 👇",
        "ja": "コメント欄にアルファベット1文字で教えてください 👇",
        "en": "Answer with one letter in the comments 👇",
    },
}


def ui(key: str, lang: str) -> str:
    return UI[key][lang]


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def fmt(value) -> str:
    """Escape text, then apply the two inline marks posts may use: **highlight** and ~~strike~~."""
    text = esc(value)
    text = _STRONG.sub(r'<strong class="hl">\1</strong>', text)
    text = _STRIKE.sub(r"<s>\1</s>", text)
    return text.replace("\n", "<br>")


def plain(value) -> str:
    """Text with the inline marks removed, as a reader would see it."""
    text = "" if value is None else str(value)
    return _STRIKE.sub(r"\1", _STRONG.sub(r"\1", text))


def duration(minutes: int, lang: str) -> str:
    """Format a duration the way each language writes it: 1 giờ 30 phút / 1時間30分 / 1 h 30 min."""
    hours, rest = divmod(int(minutes), 60)
    units = {"vi": ("giờ", "phút"), "ja": ("時間", "分"), "en": ("h", "min")}[lang]
    sep = "" if lang == "ja" else " "
    parts = []
    if hours:
        parts.append(f"{hours}{sep}{units[0]}")
    if rest or not hours:
        parts.append(f"{rest}{sep}{units[1]}")
    return ("" if lang == "ja" else " ").join(parts)
