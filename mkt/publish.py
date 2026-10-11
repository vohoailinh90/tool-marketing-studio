"""Publishing: manual packs for every platform, and the Facebook Page API.

Facebook only allows API posts to Pages — not personal profiles, not Groups. Everything
else (profile, groups, LinkedIn, X, Zalo, note…) gets a pack: the images plus the text
files, ready to post by hand.

Safety rails, each a refusal with its reason:
  * the post must be approved, and unchanged since (approvals.content_sha);
  * the Facebook connection must have passed `--smoke` for this Page and Graph version;
  * dry-run is the default; a real send is one (post, language, platform) at a time;
  * a ledger row is written BEFORE the first remote call. `done` or `pending` blocks a
    second attempt — pending means "it may have gone out; look on the Page and resolve".
"""

from __future__ import annotations

import json
import os
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from . import secrets
from .approvals import approval_state, content_sha, export_problems, manifest
from .links import is_configured
from .model import Campaign, Post, dump_yaml, load_yaml
from .platforms import PLATFORMS

DEFAULT_GRAPH_VERSION = "v23.0"
# Graph API "unknown error" and "service temporarily unavailable": the request may have been
# applied. Unverified against live docs from here; treating them as unknown is the safe side.
TRANSIENT_CODES = (1, 2)
STATE_DIR = ".studio"


class PublishError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- manual packs

def pack_files(campaign: Campaign, post: Post, platform: str) -> list[Path]:
    out = campaign.export_dir(post)
    shown = manifest(campaign, post)
    images = [out / name for name in shown.get("slides", [])]
    limit = PLATFORMS[platform].get("max_images")
    if limit:
        images = images[:limit]
    # Only the texts render listed (and export_problems verified), never whatever else is in the folder.
    texts = sorted(out / name for name in map(str, shown.get("texts", []))
                   if name == f"{platform}.txt" or name.startswith(f"{platform}-"))
    return images + texts


def build_pack(campaign: Campaign, post: Post, platform: str, config: dict) -> Path:
    """A zip with this post's images and text for one platform. Refuses stale or unrendered images."""
    if platform not in PLATFORMS:
        raise PublishError(f"unknown platform '{platform}'")
    shown = manifest(campaign, post)
    if not shown:
        raise PublishError("not rendered yet: run `studio.py render` first")
    if shown.get("sha") != content_sha(campaign, post, config):
        raise PublishError("the images are older than the post: render again")
    problems = export_problems(campaign, post)
    if problems:
        raise PublishError("; ".join(problems))
    files = pack_files(campaign, post, platform)
    if not any(f.name == f"{platform}.txt" or f.name == "x-thread.txt" for f in files):
        raise PublishError(f"the post has no '{platform}' text: add platforms.{platform} to it")
    target = campaign.dir / "packs" / f"{post.id}-{post.lang}-{platform}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.name)
    return target


# ---------------------------------------------------------------- ledger

def _ledger_path(campaign: Campaign) -> Path:
    return campaign.dir / "published.yaml"


def ledger_key(post: Post, platform: str) -> str:
    return f"{post.id}/{post.lang}/{platform}"


def load_ledger(campaign: Campaign) -> dict:
    path = _ledger_path(campaign)
    return load_yaml(path) if path.exists() else {}


def _save_ledger(campaign: Campaign, data: dict) -> None:
    path = _ledger_path(campaign)
    partial = path.with_suffix(".yaml.part")
    partial.write_text(dump_yaml(data), encoding="utf-8")
    partial.replace(path)


def update_ledger(campaign: Campaign, key: str, **fields) -> dict:
    data = load_ledger(campaign)
    row = dict(data.get(key) or {})
    row.update(fields)
    data[key] = row
    _save_ledger(campaign, data)
    return row


@contextmanager
def publish_lock(root: Path):
    """One publish at a time: Streamlit reruns and double clicks must not race to the API."""
    directory = root / STATE_DIR
    directory.mkdir(exist_ok=True)
    path = directory / "publish.lock"
    try:
        handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise PublishError(f"another publish is running (or crashed): delete {path} once you are sure it is not")
    try:
        os.write(handle, now().encode())
        yield
    finally:
        os.close(handle)
        path.unlink(missing_ok=True)


def resolve(campaign: Campaign, post: Post, platform: str, outcome: str, url: str = "") -> dict:
    """A human settles a `pending` row after looking at the Page: it did go out (done) or did not (failed)."""
    if outcome not in ("done", "failed"):
        raise PublishError("resolve as 'done' or 'failed'")
    if url and not is_configured(url):
        raise PublishError("the URL must start with http:// or https://")
    key = ledger_key(post, platform)
    with publish_lock(campaign.root):
        row = load_ledger(campaign).get(key)
        if not row or row.get("state") != "pending":
            raise PublishError(f"{key} is not pending")
        return update_ledger(campaign, key, state=outcome, resolved_at=now(), resolved_by="human",
                             **({"url": url} if url else {}))


# ---------------------------------------------------------------- Facebook Page

def _state_path(root: Path) -> Path:
    return root / STATE_DIR / "state.json"


def load_state(root: Path) -> dict:
    path = _state_path(root)
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        return {}


def _save_state(root: Path, state: dict) -> None:
    path = _state_path(root)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


class FacebookPage:
    """Graph API calls for one Page. `session` is anything with requests.Session's `request`."""

    def __init__(self, page_id: str, token: str, version: str = DEFAULT_GRAPH_VERSION, session=None):
        if not page_id or not token:
            raise PublishError("set FB_PAGE_ID and FB_PAGE_TOKEN in .env (see docs/facebook-page.md)")
        self.page_id, self.token, self.version = page_id, token, version or DEFAULT_GRAPH_VERSION
        if session is None:
            import requests
            session = requests.Session()
        self.session = session

    @property
    def base(self) -> str:
        return f"https://graph.facebook.com/{self.version}"

    def call(self, method: str, path: str, *, data=None, files=None, params=None) -> dict:
        # The token travels in a header, never in the URL, so it cannot leak into logs or history.
        try:
            response = self.session.request(method, f"{self.base}/{path}", params=params, data=data,
                                            files=files, headers={"Authorization": f"Bearer {self.token}"},
                                            timeout=60)
        except Exception as exc:  # network: the outcome is unknown
            raise UnknownOutcome(secrets.redact(exc, [self.token])) from None
        status = response.status_code
        try:
            body = response.json()
        except ValueError:
            body = None
        if status >= 500 or not isinstance(body, dict):
            # A gateway error or an unreadable answer says nothing about whether the request
            # was applied: for a feed post that means it may be live.
            raise UnknownOutcome(f"Facebook answered HTTP {status} without a usable body: it may have gone through")
        error = body.get("error")
        if status >= 400 or error:
            error = error if isinstance(error, dict) else {}
            message = secrets.redact(f"Facebook refused: {error.get('message') or f'HTTP {status}'}", [self.token])
            if error.get("code") in TRANSIENT_CODES or error.get("is_transient"):
                raise UnknownOutcome(message + " (temporary error: it may have gone through)")
            raise PublishError(message)
        return body

    def whoami(self) -> dict:
        return self.call("GET", "me", params={"fields": "id,name"})

    def plan(self, images: list[Path], caption: str, comment: str) -> list[str]:
        steps = [f"POST {self.base}/{self.page_id}/photos published=false source={p.name} ({p.stat().st_size} bytes)"
                 for p in images]
        steps.append(f"POST {self.base}/{self.page_id}/feed message=<{len(caption)} chars> "
                     f"attached_media=[{len(images)} photo id(s)]")
        if comment:
            steps.append(f"POST {self.base}/<post id>/comments message=<{len(comment)} chars>")
        return steps


class UnknownOutcome(PublishError):
    """The request may or may not have reached Facebook."""


def smoke_facebook(root: Path, *, session=None) -> dict:
    """Prove the token reaches the intended Page before anything is posted, and remember it."""
    page = FacebookPage(secrets.get("FB_PAGE_ID"), secrets.get("FB_PAGE_TOKEN"),
                        secrets.get("FB_GRAPH_VERSION", DEFAULT_GRAPH_VERSION), session)
    me = page.whoami()
    if str(me.get("id")) != str(page.page_id):
        raise PublishError(f"the token belongs to '{me.get('name')}' ({me.get('id')}), not FB_PAGE_ID {page.page_id}: "
                           "use a Page access token for that Page")
    if not str(me.get("name") or "").strip():
        raise PublishError("Facebook returned no Page name, so publishing could not be confirmed by name")
    state = load_state(root)
    state["facebook"] = {"page_id": page.page_id, "page_name": str(me["name"]).strip(),
                         "graph_version": page.version, "checked_at": now()}
    _save_state(root, state)
    return state["facebook"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def preconditions(campaign: Campaign, post: Post, platform: str, config: dict) -> list[str]:
    reasons = []
    if platform != "facebook":
        reasons.append(f"'{platform}' has no API publishing here: download its pack and post by hand")
    if platform not in campaign.platforms:
        reasons.append(f"'{platform}' is not in the campaign's platforms")
    if post.status not in ("ready", "posted"):
        reasons.append(f"status is '{post.status}': only a ready post can be published")
    approved, why = approval_state(campaign, post, config)
    if not approved:
        reasons.append(why)
    shown = manifest(campaign, post)
    if not shown or shown.get("sha") != content_sha(campaign, post, config):
        reasons.append("the images are not up to date: render again")
    else:
        reasons += export_problems(campaign, post)
    row = load_ledger(campaign).get(ledger_key(post, platform)) or {}
    if row.get("state") == "done":
        reasons.append(f"already published: {row.get('url', '')}")
    if row.get("state") == "pending":
        reasons.append("a previous attempt may have posted: check the Page, then `studio.py publish --resolve`")
    return reasons


def publish_facebook(campaign: Campaign, post: Post, config: dict, *, confirm_page_name: str | None,
                     dry_run: bool = True, session=None, log=print) -> dict:
    """Post one approved post in one language to the Facebook Page. Dry-run returns the plan only."""
    reasons = preconditions(campaign, post, "facebook", config)
    if reasons:
        raise PublishError("; ".join(reasons))
    out, shown = campaign.export_dir(post), manifest(campaign, post)
    images = [out / name for name in shown["slides"]]
    texts = set(map(str, shown.get("texts", [])))   # a file render did not write is never sent
    caption, comment = (_read(out / name) if name in texts else "" for name in ("facebook.txt", "facebook-comment.txt"))
    page = FacebookPage(secrets.get("FB_PAGE_ID"), secrets.get("FB_PAGE_TOKEN"),
                        secrets.get("FB_GRAPH_VERSION", DEFAULT_GRAPH_VERSION), session)
    if dry_run:
        return {"dry_run": True, "steps": page.plan(images, caption, comment)}

    smoke = load_state(campaign.root).get("facebook") or {}
    if smoke.get("page_id") != page.page_id or smoke.get("graph_version") != page.version:
        raise PublishError("run `studio.py publish --smoke facebook` first: it checks the token reaches this Page")
    if confirm_page_name is None or confirm_page_name.strip() != smoke.get("page_name", "").strip():
        raise PublishError(f"type the Page name exactly to confirm: '{smoke.get('page_name')}'")

    key = ledger_key(post, "facebook")
    sha = content_sha(campaign, post, config)
    with publish_lock(campaign.root):
        if preconditions(campaign, post, "facebook", config):   # re-check under the lock
            raise PublishError("; ".join(preconditions(campaign, post, "facebook", config)))
        update_ledger(campaign, key, state="pending", started_at=now(), sha=sha, page=smoke.get("page_name"),
                      steps={})
        steps: dict = {"photos": []}
        try:
            for path in images:
                with path.open("rb") as handle:
                    photo = page.call("POST", f"{page.page_id}/photos", data={"published": "false"},
                                      files={"source": (path.name, handle, "image/png")})
                steps["photos"].append(photo["id"])
                update_ledger(campaign, key, steps=dict(steps))
        except Exception as exc:
            # Unpublished photos are invisible on the Page, so any failure here is safe to retry.
            update_ledger(campaign, key, state="failed", error=f"photo upload: {secrets.redact(exc, [page.token])}",
                          steps=dict(steps))
            raise

        form = {"message": caption}
        for index, media_id in enumerate(steps["photos"]):
            form[f"attached_media[{index}]"] = json.dumps({"media_fbid": media_id})
        try:
            created = page.call("POST", f"{page.page_id}/feed", data=form)
        except UnknownOutcome as exc:
            update_ledger(campaign, key, error=f"feed post outcome unknown: {exc}", steps=dict(steps))
            raise   # stays pending: it may be live
        except PublishError as exc:
            update_ledger(campaign, key, state="failed", error=str(exc), steps=dict(steps))
            raise
        post_id = created.get("id")
        if not post_id:   # a success without an id: it may be live, so it stays pending
            update_ledger(campaign, key, error="Facebook answered without a post id", steps=dict(steps))
            raise UnknownOutcome("Facebook answered without a post id: check the Page, then resolve")
        steps["post"] = post_id
        url = f"https://www.facebook.com/{post_id}"
        update_ledger(campaign, key, state="done", url=url, remote_id=post_id, published_at=now(), steps=dict(steps))
        log(f"published {key}: {url}")

        if comment:
            try:
                made = page.call("POST", f"{post_id}/comments", data={"message": comment})
                steps["comment"] = made.get("id", "")
            except PublishError as exc:   # the post is live; only the comment is missing
                steps["comment_error"] = str(exc)
                log(f"the post is live, but the first comment failed: {exc} — add it by hand")
            update_ledger(campaign, key, steps=dict(steps))
    return load_ledger(campaign)[key]
