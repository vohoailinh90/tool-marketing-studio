"""Gathers what the insights analysis reads: history, computed metrics and feedback."""

from __future__ import annotations

from .feedback import all_feedback
from .history import rows
from .metrics import MetricsError, RATES, read_rows, totals, verdict
from .model import Campaign


def gather(campaign: Campaign) -> dict:
    history = [r for r in rows(campaign.root) if r["campaign"] == campaign.slug]
    try:
        metric_rows = read_rows(campaign.dir / "metrics.csv")
    except MetricsError:
        metric_rows = []
    validation = campaign.data.get("validation") or {}
    metrics = {}
    for lang in campaign.langs:
        summary = totals([r for r in metric_rows if r["lang"] == lang])
        decision, lines = verdict(summary, validation)
        metrics[lang] = {"verdict": decision, "checks": lines,
                         **{k: summary[k] for k in summary if k not in RATES},
                         **{k: (round(summary[k], 4) if summary[k] is not None else None) for k in RATES}}
    slim = [{k: r[k] for k in ("post", "lang", "platform", "published_at", "method", "where", "comments", "totals")}
            for r in history]
    return {"history": slim, "metrics": metrics, "feedback": all_feedback(campaign)}
