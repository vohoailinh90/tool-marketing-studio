"""Verdict on the UI catalogs: web/src/locales/{vi,ja,en}.json (the app) and
office/src/locales/{vi,ja,en}.json (the agent office, whose catalogs are nested objects).

Every key in every language, no empty message, the same {placeholders} in each
language. Computable, so a script and a CI step — not a reviewer comparing files by eye.
A nested object is checked leaf by leaf under its dotted key (`player.play`).
Exit 0 when clean, 1 with one line per problem.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ROOT / "web" / "src" / "locales"
OFFICE_LOCALES = ROOT / "office" / "src" / "locales"
LANGS = ("vi", "ja", "en")
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    """`{"a": {"b": "x"}}` -> `{"a.b": "x"}`; a flat catalog comes back unchanged.

    An empty object stays a leaf (so it is reported, not silently dropped). Raises `KeyError(name)` when two
    paths flatten to the same name, such as a key `"a.b"` next to an object `"a"` holding `"b"`.
    """
    if not isinstance(value, dict) or (not value and prefix):
        return {prefix[:-1]: value}
    flat: dict[str, Any] = {}
    for key, item in value.items():
        for name, leaf in flatten(item, f"{prefix}{key}.").items():
            if name in flat:
                raise KeyError(name)
            flat[name] = leaf
    return flat


def problems(directory: Path = LOCALES) -> list[str]:
    found: list[str] = []
    catalogs = {}
    for lang in LANGS:
        path = directory / f"{lang}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            found.append(f"{path.name}: cannot read ({exc})")
            continue
        if not isinstance(data, dict):
            found.append(f"{path.name}: must be a JSON object")
            continue
        try:
            catalogs[lang] = flatten(data)
        except KeyError as exc:
            found.append(f"{path.name}: key {exc.args[0]!r} is defined twice (a dotted key and a nested object)")
    if len(catalogs) != len(LANGS):
        return found
    keys = set().union(*(set(c) for c in catalogs.values()))
    for key in sorted(keys):
        reference = None
        for lang in LANGS:
            text = catalogs[lang].get(key)
            if text is None:
                found.append(f"{lang}.json: missing key '{key}'")
                continue
            if not isinstance(text, str):
                found.append(f"{lang}.json: '{key}' is not a message (expected a string)")
                continue
            if not text.strip():
                found.append(f"{lang}.json: '{key}' is empty")
                continue
            marks = set(PLACEHOLDER.findall(text))
            if reference is None:
                reference = (lang, marks)
            elif marks != reference[1]:
                found.append(f"{lang}.json: '{key}' has placeholders {sorted(marks)}, "
                             f"{reference[0]}.json has {sorted(reference[1])}")
    return found


def main() -> int:
    found = problems()
    if OFFICE_LOCALES.is_dir():
        found += [f"office: {line}" for line in problems(OFFICE_LOCALES)]
    for line in found:
        print(line)
    print(f"i18n_check: {len(found)} problem(s)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
