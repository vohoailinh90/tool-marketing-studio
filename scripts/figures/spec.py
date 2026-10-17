"""The figure spec: what a figure says, in a closed vocabulary. Everything else (places, sizes, colours, arrows) is drawn by script.

A spec is a JSON object:

    {"id": "sd-01-001", "lang": "vi", "title": "...", "subtitle": "...", "desc": "...",
     "sections": [
       {"kind": "parts", "heading": "...", "items": [{"name": "...", "role": "...", "icon": "server"}], "flow": [[0, 1], [1, 2]]},
       {"kind": "steps", "heading": "...", "items": [{"title": "...", "text": "..."}]},
       {"kind": "notes", "heading": "...", "items": ["..."]},
       {"kind": "sequence", "heading": "...", "actors": [{"name": "...", "icon": "monitor"}, {"name": "..."}],
        "messages": [{"from": 0, "to": 1, "text": "...", "reply": false}]}]}

`problems()` is the verdict (a list of sentences, empty when the spec is good). A spec is data: no key outside this vocabulary,
no URL, no icon outside `icons.NAMES`, and counts and lengths that fit a 320 px column.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from mkt.check import has_url

from . import icons
from .text import combining, measurable, one_line

ID = re.compile(r"[a-z0-9][a-z0-9-]{1,40}")
KINDS = {
    "parts": {"heading", "items", "flow"},
    "steps": {"heading", "items"},
    "notes": {"heading", "items"},
    "sequence": {"heading", "actors", "messages"},
}
TOP_KEYS = {"id", "lang", "title", "subtitle", "desc", "sections"}
LANGS = ("vi", "en", "ja")
MAX_RAILS = 4                       # cross links that run beside the cards of one `parts` section
HIDDEN = {"Cc", "Cf", "Cs", "Zl", "Zp"}      # Unicode categories nobody sees: controls, format (zero-width, direction marks, joiners), surrogates, separators
LINK = re.compile(r"://")                  # any scheme, `ftp://` included: has_url reads only http(s), www. and domains


class SpecError(ValueError):
    """The spec cannot be drawn; `args[0]` is the list of problems."""


def _no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"the key {key!r} is written twice")
        out[key] = value
    return out


def load(path: Path) -> dict:
    """The spec in a file. SpecError when it cannot be read, is not JSON, names a key twice or is not valid."""
    try:
        spec = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_no_duplicates)
    except (OSError, ValueError, RecursionError) as exc:
        raise SpecError([f"{path}: {exc}"]) from exc
    found = problems(spec)
    if found:
        raise SpecError([f"{path}: {p}" for p in found])
    return spec


def hidden(value: str) -> bool:
    """True when the text holds a character that is not seen but changes what is drawn or in which order: a control (a tab and a new line
    are fine), a format character, a lone surrogate, a line or paragraph separator, or one of the two non-characters XML refuses."""
    return any((unicodedata.category(c) in HIDDEN and c not in "\n\t") or c in "\ufffe\uffff" for c in value)


def orphan_mark(value: str) -> bool:
    """True when a combining mark has no letter before it (at the start, after a space, or after a line break): it would be drawn on nothing."""
    base = False
    for c in value:
        if combining(c):
            if not base:
                return True
        else:
            base = not c.isspace()
    return False


def _text(value, where: str, low: int, high: int, found: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        found.append(f"{where} must be text")
        return
    shown = one_line(value)                                  # what is drawn: whitespace collapsed, composed form
    if len(shown) < low or len(shown) > high:
        found.append(f"{where} is {len(shown)} characters, expected {low}-{high}")
    if LINK.search(value) or has_url(value):             # has_url is the studio's rule for posts: bare domains and spaced schemes too
        found.append(f"{where} holds a link or a source-image host; a figure carries no address")
    if hidden(value):
        found.append(f"{where} holds a control or invisible character")
    elif orphan_mark(value):
        found.append(f"{where} holds a combining mark with no letter before it")
    else:
        unknown = sorted({c for c in value if not measurable(c)})
        if unknown:
            shown = ", ".join(f"{c!r} (U+{ord(c):04X})" for c in unknown[:3])
            found.append(f"{where} holds a character the figure cannot measure: {shown}; write it as a word or use a measured symbol (scripts/figures/text.py)")


def _index(value, size: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < size


def _icons(items: list, where: str, found: list[str]) -> None:
    """All or none of the cards name an icon: a row with one bare card looks like a mistake."""
    named = [isinstance(x, dict) and x.get("icon") is not None for x in items]
    if any(named) and not all(named):
        found.append(f"{where}: name an icon for every item or for none")
    for i, item in enumerate(items):
        icon = item.get("icon") if isinstance(item, dict) else None
        if icon is not None and icon not in icons.NAMES:
            found.append(f"{where}[{i}].icon {icon!r} is not in the icon set (python3 -m scripts.figures icons)")


def _keys(obj: dict, allowed: set[str], where: str, found: list[str]) -> None:
    extra = sorted(set(obj) - allowed, key=str)
    if extra:
        found.append(f"{where} has unknown keys {', '.join(map(str, extra))}")


def forward(a: int, b: int) -> bool:
    """A link straight down to the next card: drawn in the gap between the two, never on a rail."""
    return b == a + 1


def rails_needed(flow: list) -> int:
    from .scene import assign_rails       # the one place that knows how rails are shared
    return max(assign_rails([(a, b) for a, b in flow if not forward(a, b)]).values(), default=-1) + 1


def _parts(sec: dict, where: str, found: list[str]) -> None:
    before = len(found)
    items = sec.get("items")
    if not isinstance(items, list) or not 2 <= len(items) <= 6:
        found.append(f"{where}.items must be a list of 2-6 cards")
        return
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            found.append(f"{where}.items[{i}] must be an object")
            continue
        _keys(item, {"name", "role", "icon"}, f"{where}.items[{i}]", found)
        _text(item.get("name"), f"{where}.items[{i}].name", 1, 32, found)
        _text(item.get("role"), f"{where}.items[{i}].role", 1, 110, found)
    _icons([x for x in items if isinstance(x, dict)], f"{where}.items", found)
    flow = sec.get("flow", [])
    if not isinstance(flow, list) or len(flow) > 8:
        found.append(f"{where}.flow must be a list of at most 8 [from, to] pairs")
        return
    seen = set()
    for i, pair in enumerate(flow):
        if not (isinstance(pair, list) and len(pair) == 2 and all(_index(n, len(items)) for n in pair)) or pair[0] == pair[1]:
            found.append(f"{where}.flow[{i}] must be two different card numbers between 0 and {len(items) - 1}")
        elif tuple(pair) in seen:
            found.append(f"{where}.flow[{i}] repeats {pair}")
        else:
            seen.add(tuple(pair))
    if len(found) == before and rails_needed(flow) > MAX_RAILS:
        found.append(f"{where}.flow needs more than {MAX_RAILS} lanes beside the cards; keep the links between neighbours or split the figure")


def _steps(sec: dict, where: str, found: list[str]) -> None:
    items = sec.get("items")
    if not isinstance(items, list) or not 2 <= len(items) <= 8:
        found.append(f"{where}.items must be a list of 2-8 steps")
        return
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            found.append(f"{where}.items[{i}] must be an object")
            continue
        _keys(item, {"title", "text"}, f"{where}.items[{i}]", found)
        _text(item.get("title"), f"{where}.items[{i}].title", 1, 48, found)
        _text(item.get("text"), f"{where}.items[{i}].text", 1, 140, found)


def _notes(sec: dict, where: str, found: list[str]) -> None:
    items = sec.get("items")
    if not isinstance(items, list) or not 2 <= len(items) <= 8:
        found.append(f"{where}.items must be a list of 2-8 notes")
        return
    for i, item in enumerate(items):
        _text(item, f"{where}.items[{i}]", 1, 120, found)


def _sequence(sec: dict, where: str, found: list[str]) -> None:
    actors, messages = sec.get("actors"), sec.get("messages")
    if not isinstance(actors, list) or not 2 <= len(actors) <= 3:
        found.append(f"{where}.actors must be a list of 2-3 actors")
        return
    for i, actor in enumerate(actors):
        if not isinstance(actor, dict):
            found.append(f"{where}.actors[{i}] must be an object")
            continue
        _keys(actor, {"name", "icon"}, f"{where}.actors[{i}]", found)
        _text(actor.get("name"), f"{where}.actors[{i}].name", 1, 20, found)
    _icons([x for x in actors if isinstance(x, dict)], f"{where}.actors", found)
    if not isinstance(messages, list) or not 2 <= len(messages) <= 10:
        found.append(f"{where}.messages must be a list of 2-10 messages")
        return
    for i, message in enumerate(messages):
        if not isinstance(message, dict):
            found.append(f"{where}.messages[{i}] must be an object")
            continue
        _keys(message, {"from", "to", "text", "reply"}, f"{where}.messages[{i}]", found)
        if not (_index(message.get("from"), len(actors)) and _index(message.get("to"), len(actors))) or message.get("from") == message.get("to"):
            found.append(f"{where}.messages[{i}] must go from one actor to a different one (numbers 0-{len(actors) - 1})")
        if "reply" in message and not isinstance(message["reply"], bool):
            found.append(f"{where}.messages[{i}].reply must be true or false")
        _text(message.get("text"), f"{where}.messages[{i}].text", 1, 60, found)


CHECKS = {"parts": _parts, "steps": _steps, "notes": _notes, "sequence": _sequence}


def problems(spec) -> list[str]:
    """Every reason the spec cannot be drawn, in reading order."""
    if not isinstance(spec, dict):
        return ["the spec must be a JSON object"]
    found: list[str] = []
    _keys(spec, TOP_KEYS, "the spec", found)
    if not (isinstance(spec.get("id"), str) and ID.fullmatch(spec["id"])):
        found.append("id must be lowercase letters, digits and hyphens (the lesson id, e.g. sd-01-001)")
    if spec.get("lang", "vi") not in LANGS:
        found.append(f"lang must be one of {', '.join(LANGS)}")
    _text(spec.get("title"), "title", 1, 60, found)
    if "subtitle" in spec:
        _text(spec["subtitle"], "subtitle", 1, 100, found)
    _text(spec.get("desc"), "desc", 20, 700, found)
    sections = spec.get("sections")
    if not isinstance(sections, list) or not 1 <= len(sections) <= 6:
        found.append("sections must be a list of 1-6 sections")
        return found
    for i, sec in enumerate(sections):
        where = f"sections[{i}]"
        if not isinstance(sec, dict) or not isinstance(sec.get("kind"), str) or sec["kind"] not in KINDS:
            found.append(f"{where}.kind must be one of {', '.join(sorted(KINDS))}")
            continue
        _keys(sec, KINDS[sec["kind"]] | {"kind"}, where, found)
        if "heading" in sec:
            _text(sec["heading"], f"{where}.heading", 1, 50, found)
        CHECKS[sec["kind"]](sec, where, found)
    return found
