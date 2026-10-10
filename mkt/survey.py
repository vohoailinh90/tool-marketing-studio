"""`studio.py survey`: answer counts from a Google Forms / Microsoft Forms CSV export.

Counting is computable, so it is a script. Raw exports hold respondents' e-mails: keep
them in research/raw/ (gitignored) and commit only the summary this prints.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

SKIP = ("timestamp", "dấu thời gian", "タイムスタンプ", "email", "e-mail", "メール", "địa chỉ email")


def read(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def summarize(path: Path, column: str = "", split: bool = False, top: int = 15) -> str:
    columns, rows = read(path)
    chosen = [c for c in columns if column.lower() in c.lower()] if column else \
        [c for c in columns if not any(word in c.lower() for word in SKIP)]
    if not chosen:
        raise ValueError(f"no column matches '{column}'. Columns: {', '.join(columns)}")
    out = [f"{len(rows)} response(s) in {path.name}"]
    for name in chosen:
        values = [(row.get(name) or "").strip() for row in rows]
        answered = [v for v in values if v]
        if split:
            answered = [part.strip() for v in answered for part in v.split(",") if part.strip()]
        counts = Counter(answered)
        out.append(f"\n## {name}  (answered: {sum(1 for v in values if v)}/{len(rows)})")
        if len(counts) > top and all(n == 1 for n in counts.values()):
            out.append("   free-text answers — read them; first 5:")
            out += [f"   - {v}" for v in answered[:5]]
            continue
        for value, n in counts.most_common(top):
            share = n / len(rows) if rows else 0
            out.append(f"   {n:>4}  {share:6.1%}  {value}")
    return "\n".join(out)
