"""Feedback on published posts: reactions and comments, scanned from the Facebook Page
by API, or pasted in by hand for every other platform.

Stored per post, language and platform in campaigns/<slug>/feedback/ — gitignored,
because comments are other people's words. Only comment text, time and like count are
kept; commenter names and ids are never requested. The AI analysis (insights/) is what
gets committed.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from . import secrets
from .model import Campaign, dump_yaml, load_yaml
from .publish import DEFAULT_GRAPH_VERSION, FacebookPage, PublishError, load_ledger, now

MAX_COMMENTS = 500


def _path(campaign: Campaign, post_id: str, lang: str, platform: str) -> Path:
    return campaign.dir / "feedback" / f"{post_id}__{lang}__{platform}.yaml"


def load_feedback(campaign: Campaign, post_id: str, lang: str, platform: str) -> dict:
    path = _path(campaign, post_id, lang, platform)
    return load_yaml(path) if path.exists() else {}


def _save(campaign: Campaign, post_id: str, lang: str, platform: str, data: dict) -> Path:
    path = _path(campaign, post_id, lang, platform)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(data), encoding="utf-8")
    return path


def _merge(existing: list[dict], new: list[dict]) -> list[dict]:
    """Add comments not seen before (by id, or by text for pasted ones)."""
    def key(c):
        return c.get("id") or "text:" + hashlib.sha256(c.get("text", "").strip().encode("utf-8")).hexdigest()[:16]
    seen = {key(c) for c in existing}
    merged = list(existing)
    for comment in new:
        if comment.get("text", "").strip() and key(comment) not in seen:
            merged.append(comment)
            seen.add(key(comment))
    return merged


def add_manual(campaign: Campaign, post_id: str, lang: str, platform: str, pasted: str,
               totals: dict | None = None) -> dict:
    """Comments copied from a post: one per paragraph (separate them with a blank line)."""
    paragraphs = [p.strip() for p in pasted.replace("\r\n", "\n").split("\n\n") if p.strip()]
    data = load_feedback(campaign, post_id, lang, platform)
    data["comments"] = _merge(data.get("comments") or [],
                              [{"text": p, "source": "pasted", "added_at": now()} for p in paragraphs])
    if isinstance(totals, dict):
        clean = {k: int(str(v).strip()) for k, v in totals.items()
                 if k in ("reactions", "comments", "shares") and str(v).strip().isdecimal()}
        data["totals"] = {**(data.get("totals") or {}), **clean}
    data["updated_at"] = now()
    _save(campaign, post_id, lang, platform, data)
    return data


def scan_facebook(campaign: Campaign, post_id: str, lang: str, *, session=None) -> dict:
    """Read reactions, shares and comments of a post this studio published to the Page."""
    row = load_ledger(campaign).get(f"{post_id}/{lang}/facebook") or {}
    remote = row.get("remote_id")
    if row.get("state") != "done" or not remote:
        raise PublishError("only posts published to the Page through the studio can be scanned; "
                           "paste comments for posts made by hand")
    page = FacebookPage(secrets.get("FB_PAGE_ID"), secrets.get("FB_PAGE_TOKEN"),
                        secrets.get("FB_GRAPH_VERSION", DEFAULT_GRAPH_VERSION), session)
    summary = page.call("GET", remote, params={
        "fields": "reactions.summary(total_count).limit(0),comments.summary(total_count).limit(0),shares"})
    totals = {
        "reactions": int(((summary.get("reactions") or {}).get("summary") or {}).get("total_count", 0)),
        "comments": int(((summary.get("comments") or {}).get("summary") or {}).get("total_count", 0)),
        "shares": int((summary.get("shares") or {}).get("count", 0)),
    }
    comments, after = [], None
    while len(comments) < MAX_COMMENTS:
        params = {"fields": "id,message,created_time,like_count", "filter": "stream", "limit": 100}
        if after:
            params["after"] = after
        page_data = page.call("GET", f"{remote}/comments", params=params)
        for item in page_data.get("data") or []:
            comments.append({"id": item.get("id"), "text": item.get("message", ""),
                             "created_time": item.get("created_time", ""), "likes": int(item.get("like_count", 0)),
                             "source": "facebook"})
        after = ((page_data.get("paging") or {}).get("cursors") or {}).get("after")
        if not (page_data.get("paging") or {}).get("next") or not after:
            break
    data = load_feedback(campaign, post_id, lang, "facebook")
    data["comments"] = _merge(data.get("comments") or [], comments)
    data["totals"] = {**(data.get("totals") or {}), **totals}
    data["scanned_at"] = now()
    _save(campaign, post_id, lang, "facebook", data)
    return data


def all_feedback(campaign: Campaign) -> list[dict]:
    """Every feedback file of a campaign, with its post, language and platform."""
    out = []
    base = campaign.dir / "feedback"
    for path in sorted(base.glob("*__*__*.yaml")) if base.is_dir() else []:
        post_id, lang, platform = path.stem.split("__")
        out.append({"post": post_id, "lang": lang, "platform": platform, **load_yaml(path)})
    return out


