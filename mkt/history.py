"""Posting history across every campaign: which tool, which post, which language, which
platform, when, where — whether it went out through the API or was posted by hand.

The source of truth is each campaign's `published.yaml` ledger. Posts made by hand
(Facebook profile or groups, LinkedIn, X, Zalo…) are added with `mark_posted`, so the
history and the feedback analysis cover them too.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .links import is_configured
from .model import Campaign, Post, campaign_slugs, load_campaign
from .platforms import PLATFORMS
from .publish import PublishError, ledger_key, load_ledger, now, publish_lock, update_ledger


def _parse_when(value: str) -> str:
    """Accept '2026-10-12 20:30', '2026-10-12T20:30' or an ISO time; store ISO with seconds."""
    text = (value or "").strip()
    if not text:
        return now()
    for pattern in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).isoformat(timespec="seconds")
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text).isoformat(timespec="seconds")
    except ValueError:
        raise PublishError(f"cannot read the time '{value}': use YYYY-MM-DD HH:MM") from None


def mark_posted(campaign: Campaign, post: Post, platform: str, *, url: str = "", when: str = "",
                where: str = "", note: str = "") -> dict:
    """Record one post published by hand. `where` names the place (a group, a profile, a page).

    A post can go to many places by hand — three Facebook groups, say — so each record gets
    its own ledger row (`<post>/<lang>/<platform>/m<n>`), apart from the API row.
    """
    if platform not in PLATFORMS:
        raise PublishError(f"unknown platform '{platform}'")
    if url and not is_configured(url):
        raise PublishError("the URL must start with http:// or https://")
    published_at = _parse_when(when)
    with publish_lock(campaign.root):
        ledger = load_ledger(campaign)
        if url and any(isinstance(r, dict) and r.get("url") == url for r in ledger.values()):
            raise PublishError("this URL is already in the history")
        base = ledger_key(post, platform)
        numbers = [int(key.rsplit("/m", 1)[1]) for key in ledger
                   if key.startswith(base + "/m") and key.rsplit("/m", 1)[1].isdigit()]
        return update_ledger(campaign, f"{base}/m{max(numbers, default=0) + 1}", state="done", method="manual",
                             published_at=published_at, url=url, where=where, note=note, recorded_at=now())


def manual_rows(ledger: dict, post_id: str, lang: str, platform: str) -> list[dict]:
    prefix = f"{post_id}/{lang}/{platform}/m"
    return [row for key, row in sorted(ledger.items()) if key.startswith(prefix) and isinstance(row, dict)]


def is_published(ledger: dict, post_id: str, lang: str, platform: str) -> bool:
    base = f"{post_id}/{lang}/{platform}"
    return any(isinstance(row, dict) and row.get("state") == "done" and (key == base or key.startswith(base + "/m"))
               for key, row in ledger.items())


def rows(root: Path) -> list[dict]:
    """Every published post, newest first."""
    from .feedback import load_feedback
    out = []
    for slug in campaign_slugs(root):
        campaign = load_campaign(root, slug)
        for key, row in load_ledger(campaign).items():
            if not isinstance(row, dict) or row.get("state") not in ("done", "pending"):
                continue
            post_id, lang, platform = (str(key).split("/") + ["", "", ""])[:3]
            feedback = load_feedback(campaign, post_id, lang, platform)
            out.append({
                "campaign": slug, "tool": campaign.tool, "tool_name": campaign.tool_name,
                "post": post_id, "lang": lang, "platform": platform,
                "state": row.get("state"), "method": row.get("method", "api"),
                "published_at": row.get("published_at") or row.get("started_at", ""),
                "url": row.get("url", ""), "where": row.get("where") or row.get("page", ""),
                "comments": len(feedback.get("comments") or []),
                "totals": feedback.get("totals") or {}, "scanned_at": feedback.get("scanned_at", ""),
            })
    return sorted(out, key=lambda r: r["published_at"] or "", reverse=True)


def as_markdown(history: list[dict]) -> str:
    lines = ["| Published | Tool | Post | Lang | Platform | Where | How | Comments | Link |",
             "|---|---|---|---|---|---|---|---:|---|"]
    for r in history:
        link = f"[open]({r['url']})" if r["url"] else ""
        lines.append(f"| {r['published_at'][:16].replace('T', ' ')} | {r['tool_name']} | {r['post']} | {r['lang']} | "
                     f"{r['platform']} | {r['where']} | {r['method']} | {r['comments']} | {link} |")
    return "\n".join(lines) + "\n"


def today() -> str:
    return datetime.now(timezone.utc).date().isoformat()
