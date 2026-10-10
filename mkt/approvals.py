"""The human gate between a draft and a public post.

`approve` records the hash of everything that shapes what the audience sees — the post
(minus its status), brand, handle, links, referenced images and the engine version.
Any later edit changes the hash and silently voids the approval, so publishing never
sends something nobody looked at.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone


from . import __version__
from .check import check_post, has_errors
from .layouts import AssetError, resolve_asset
from .links import post_link
from .model import Campaign, Post, dump_yaml, load_yaml


class ApprovalError(ValueError):
    pass


def handle(config: dict) -> str:
    return str((config.get("author") or {}).get("handle") or "")


def content_sha(campaign: Campaign, post: Post, config: dict) -> str:
    images = {}
    for slide in post.slides:
        if isinstance(slide, dict) and slide.get("layout") == "image":
            try:
                path = resolve_asset(slide.get("src"), [campaign.dir, campaign.tool_dir])
                images[str(slide["src"])] = hashlib.sha256(path.read_bytes()).hexdigest()
            except AssetError:
                images[str(slide.get("src"))] = None
    payload = {
        "post": {key: value for key, value in post.data.items() if key != "status"},
        "lang": post.lang,
        "tool": campaign.tool_name,
        "brand": campaign.brand,
        "handle": handle(config),
        "links": {p: post_link(campaign, post, p) for p in sorted(set(campaign.platforms) | {"qr"})},
        "images": images,
        "engine": __version__,
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def manifest(campaign: Campaign, post: Post) -> dict:
    path = campaign.export_dir(post) / "manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


EXPORT_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def export_problems(campaign: Campaign, post: Post) -> list[str]:
    """The exported images and texts must be exactly what `render` wrote (manifest hashes)."""
    shown = manifest(campaign, post)
    out = campaign.export_dir(post)
    hashes = shown.get("files")
    if not isinstance(hashes, dict) or not hashes:
        return ["the export has no file hashes: render again"]
    problems = []
    for name in list(shown.get("slides") or []) + list(shown.get("texts") or []):
        path = out / str(name)
        if not EXPORT_NAME.match(str(name)) or not path.is_file():
            problems.append(f"export file missing or invalid: {name}")
        elif hashes.get(name) != hashlib.sha256(path.read_bytes()).hexdigest():
            problems.append(f"{name} changed after rendering: render again")
    return problems



def _approvals_path(campaign: Campaign):
    return campaign.dir / "approvals.yaml"


def load_approvals(campaign: Campaign) -> dict:
    path = _approvals_path(campaign)
    return load_yaml(path) if path.exists() else {}


def blockers(campaign: Campaign, post: Post, config: dict) -> list[str]:
    """Why this post cannot be approved right now; empty when it can."""
    reasons = []
    if post.status not in ("ready", "posted"):
        reasons.append(f"status is '{post.status}'; set it to 'ready' after editing")
    errors = [str(i) for i in check_post(campaign, post) if i.level == "error"]
    reasons += errors
    shown = manifest(campaign, post)
    if not shown:
        reasons.append("not rendered yet: run `studio.py render`")
    elif shown.get("sha") != content_sha(campaign, post, config):
        reasons.append("the images are older than the post: render again")
    elif shown.get("overflow"):
        reasons.append(f"text overflows on slide(s) {shown['overflow']}: shorten it and render again")
    else:
        reasons += export_problems(campaign, post)
    return reasons


def approve(campaign: Campaign, post: Post, config: dict, *, by: str = "") -> dict:
    reasons = blockers(campaign, post, config)
    if reasons:
        raise ApprovalError("; ".join(reasons))
    data = load_approvals(campaign)
    entry = {"sha": content_sha(campaign, post, config),
             "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if by:
        entry["by"] = by
    data.setdefault(post.id, {})[post.lang] = entry
    _approvals_path(campaign).write_text(dump_yaml(data), encoding="utf-8")
    return entry


def approval_state(campaign: Campaign, post: Post, config: dict) -> tuple[bool, str]:
    """(approved, reason). An approval counts only while it matches the post as it is now."""
    entry = (load_approvals(campaign).get(post.id) or {}).get(post.lang)
    if not entry:
        return False, "not approved"
    if post.status not in ("ready", "posted"):
        return False, f"status is '{post.status}': set it back to ready to use the approval"
    if entry.get("sha") != content_sha(campaign, post, config):
        return False, "edited since it was approved: review and approve again"
    if has_errors(check_post(campaign, post)):
        return False, "check reports errors"
    return True, f"approved {entry.get('at', '')}"



