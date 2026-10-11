"""A throwaway studio root with one tool, one campaign and one post, for tests."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
       b"\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82")

BRIEF = {
    "slug": "demo", "name": "Demo Tool", "status": "beta",
    "brand": {"emoji": "🧰", "accent": "#2563eb"},
    "claims": [{"id": "time", "text": "Saves about 20 minutes per event", "evidence": "estimate", "verified": False}],
}
POSITIONING = {"lang": "vi", "one_liner": "Một tool", "audience": "Dân văn phòng", "pains": ["Đếm tay"]}
CAMPAIGN = {
    "tool": "demo", "langs": ["vi", "en"], "platforms": ["facebook"], "goal": "Validate demand",
    "links": {"survey": "https://example.com/form?src={source}"},
    "validation": {"min_counts": {"reach": 100, "link_clicks": 10}, "go_if": {"signups": 3, "click_rate": 0.01}},
}


def post_data(**changes) -> dict:
    data = {
        "id": "01-pain", "status": "ready", "format": "portrait", "series": "Demo · #1", "link": "survey",
        "slides": [
            {"layout": "cover", "title": "Bạn có **mệt** không?"},
            {"layout": "flow", "title": "Làm tay", "steps": [{"text": "Đếm", "minutes": 20}]},
            {"layout": "cta", "title": "Thử nhé"},
        ],
        "platforms": {"facebook": {"caption": "Một dòng mở đầu\n\nNội dung", "first_comment": "Khảo sát: {link}",
                                   "hashtags": ["demo"]}},
    }
    data.update(changes)
    return data


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def make_root(**post_changes) -> Path:
    root = Path(tempfile.mkdtemp(prefix="studio-test-"))
    write_yaml(root / "tools/demo/brief.yaml", BRIEF)
    for lang in ("vi", "en"):
        write_yaml(root / f"tools/demo/positioning/{lang}.yaml", {**POSITIONING, "lang": lang})
    write_yaml(root / "campaigns/demo/campaign.yaml", CAMPAIGN)
    write_yaml(root / "campaigns/demo/posts/vi/01-pain.yaml", post_data(**post_changes))
    return root


def cleanup(root: Path) -> None:
    shutil.rmtree(root, ignore_errors=True)


def fake_render(campaign, post, config: dict | None = None) -> None:
    """What `render` leaves behind, without a browser: two PNGs, the platform texts, a manifest."""
    from mkt.approvals import content_sha
    from mkt.render import write_texts
    out = campaign.export_dir(post)
    out.mkdir(parents=True, exist_ok=True)
    for name in ("01.png", "02.png"):
        (out / name).write_bytes(PNG)
    texts = write_texts(campaign, post, out)
    files = {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in ["01.png", "02.png"] + texts}
    (out / "manifest.json").write_text(json.dumps({
        "sha": content_sha(campaign, post, config or {}), "slides": ["01.png", "02.png"], "files": files,
        "texts": texts, "overflow": [], "rendered_at": "2026-10-10T00:00:00+00:00"}), encoding="utf-8")


class FakeResponse:
    def __init__(self, status: int, body: dict):
        self.status_code = status
        self._body = body

    def json(self):
        return self._body


class FakeSession:
    """Answers Graph API calls from a script and records what was sent."""

    def __init__(self, script):
        self.script = list(script)   # (status, body) or an Exception, one per call
        self.calls = []

    def request(self, method, url, params=None, data=None, files=None, headers=None, timeout=None):
        self.calls.append({"method": method, "url": url, "params": params, "data": data,
                           "files": sorted(files) if files else None, "headers": headers})
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return FakeResponse(*step)
