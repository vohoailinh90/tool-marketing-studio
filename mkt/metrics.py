"""`studio.py metrics`: the numbers you copy from Facebook Insights → rates and a verdict.

The verdict is per language and refuses to call anything below the campaign's minimum
counts: two clicks out of ten is not a signal, it is noise.
"""

from __future__ import annotations

import csv
from pathlib import Path

COUNTS = ("reach", "reactions", "comments", "shares", "link_clicks", "survey_responses", "signups", "dms")
COLUMNS = ("date", "post", "lang", "platform") + COUNTS
RATES = {
    "engagement_rate": (("reactions", "comments", "shares"), "reach"),
    "click_rate": (("link_clicks",), "reach"),
    "response_rate": (("survey_responses",), "link_clicks"),
    "signup_rate": (("signups",), "survey_responses"),
}


class MetricsError(ValueError):
    pass


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise MetricsError(f"{path.name} lacks column(s): {', '.join(missing)}")
        rows = []
        for number, row in enumerate(reader, 2):
            clean = {key: row[key].strip() for key in ("date", "post", "lang", "platform")}
            for key in COUNTS:
                value = (row.get(key) or "0").strip() or "0"
                if not value.isdigit():
                    raise MetricsError(f"{path.name} line {number}: {key} must be a whole number, got '{value}'")
                clean[key] = int(value)
            rows.append(clean)
        return rows


def totals(rows: list[dict]) -> dict:
    out = {key: sum(row[key] for row in rows) for key in COUNTS}
    for name, (parts, base) in RATES.items():
        denominator = out[base]
        out[name] = (sum(out[p] for p in parts) / denominator) if denominator else None
    return out


def verdict(summary: dict, validation: dict) -> tuple[str, list[str]]:
    """GO / NOT_YET / INSUFFICIENT_DATA with the reason for each line."""
    lines, short = [], False
    for key, minimum in (validation.get("min_counts") or {}).items():
        have = summary.get(key, 0) or 0
        ok = have >= minimum
        short |= not ok
        lines.append(f"{'✓' if ok else '·'} minimum {key}: {have} / {minimum}")
    met = True
    for key, target in (validation.get("go_if") or {}).items():
        have = summary.get(key)
        ok = have is not None and have >= target
        met &= ok
        shown = f"{have:.2%}" if isinstance(have, float) else str(have)
        lines.append(f"{'✓' if ok else '✗'} target {key}: {shown} / {target}")
    if short:
        return "INSUFFICIENT_DATA", lines
    return ("GO" if met else "NOT_YET"), lines


def report(rows: list[dict], validation: dict, langs: list[str]) -> str:
    out = []
    for lang in langs:
        summary = totals([row for row in rows if row["lang"] == lang])
        decision, lines = verdict(summary, validation)
        out.append(f"== {lang}: {decision}")
        for name in RATES:
            value = summary[name]
            base = RATES[name][1]
            out.append(f"   {name}: {'—' if value is None else f'{value:.2%}'} (n={summary[base]} {base})")
        out += [f"   {line}" for line in lines]
    posts = sorted({(row["post"], row["lang"]) for row in rows})
    if posts:
        out.append("== per post")
        for post, lang in posts:
            s = totals([r for r in rows if r["post"] == post and r["lang"] == lang])
            rate = "—" if s["click_rate"] is None else f"{s['click_rate']:.2%}"
            out.append(f"   {post}/{lang}: reach {s['reach']}, clicks {s['link_clicks']} ({rate}), "
                       f"responses {s['survey_responses']}, signups {s['signups']}")
    return "\n".join(out)


def append_row(path: Path, row: dict) -> dict:
    """Add one row (creating the file with its header). Counts must be whole numbers."""
    clean = {key: str(row.get(key, "")).strip() for key in ("date", "post", "lang", "platform")}
    if not all(clean.values()):
        raise MetricsError("date, post, lang and platform are required")
    for key in COUNTS:
        value = str(row.get(key, 0) or 0).strip()
        if not value.isdigit():
            raise MetricsError(f"{key} must be a whole number, got '{value}'")
        clean[key] = int(value)
    new = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        if new:
            writer.writeheader()
        writer.writerow(clean)
    return clean
