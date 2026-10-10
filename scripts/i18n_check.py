"""Verdict on the app's UI catalogs: web/src/locales/{vi,ja,en}.json.

Every key in every language, no empty message, the same {placeholders} in each
language. Computable, so a script and a CI step — not a reviewer comparing files by eye.
Exit 0 when clean, 1 with one line per problem.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ROOT / "web" / "src" / "locales"
LANGS = ("vi", "ja", "en")
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def problems(directory: Path = LOCALES) -> list[str]:
    found: list[str] = []
    catalogs = {}
    for lang in LANGS:
        path = directory / f"{lang}.json"
        try:
            catalogs[lang] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            found.append(f"{path.name}: cannot read ({exc})")
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
            if not isinstance(text, str) or not text.strip():
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
    for line in found:
        print(line)
    print(f"i18n_check: {len(found)} problem(s)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
