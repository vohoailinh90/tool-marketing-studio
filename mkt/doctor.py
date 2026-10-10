"""`studio.py doctor`: is this machine ready to render, draft and publish? One line per check."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from . import secrets
from .fonts import FONT_DIR, WANTED, font_file
from .publish import DEFAULT_GRAPH_VERSION, load_state


def _has(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def run(root: Path, *, live: bool = False, config: dict | None = None) -> list[tuple[str, bool, str]]:
    results = []

    def add(name, ok, detail=""):
        results.append((name, ok, detail))

    add("python >= 3.10", sys.version_info >= (3, 10), sys.version.split()[0])
    for module, why in (("yaml", "required"), ("segno", "QR codes"), ("playwright", "rendering images"),
                        ("requests", "Facebook publishing"), ("anthropic", "AI drafting (optional)"),
                        ("streamlit", "the app (optional)")):
        add(f"package {module}", _has(module), why)

    if _has("playwright"):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                browser.close()
            add("chromium", True, "launches")
        except Exception as exc:
            add("chromium", False, f"run: python -m playwright install chromium ({str(exc).splitlines()[0]})")

    cached = [f"{family} {weight}" for family, weight in WANTED if font_file(family, weight).exists()]
    add("fonts cached", len(cached) == len(WANTED),
        f"{len(cached)}/{len(WANTED)} in {FONT_DIR.name}/ (fetched on first render; system fonts otherwise)")

    has_key = bool(secrets.get("ANTHROPIC_API_KEY") or secrets.get("ANTHROPIC_AUTH_TOKEN"))
    add("Claude API credential", has_key, "set ANTHROPIC_API_KEY in .env — or use copy-paste mode")
    if live and has_key and _has("anthropic"):
        try:
            from .ai import Claude
            text, _, usage = Claude(config or {}).complete("Answer with one word.", [{"role": "user", "content": "ping"}])
            add("Claude API call", True, f"answered ({usage['output_tokens']} output tokens)")
        except Exception as exc:
            add("Claude API call", False, secrets.redact(exc))

    page, token = secrets.get("FB_PAGE_ID"), secrets.get("FB_PAGE_TOKEN")
    add("Facebook Page credentials", bool(page and token), "FB_PAGE_ID + FB_PAGE_TOKEN in .env (optional)")
    smoke = load_state(root).get("facebook") or {}
    version = secrets.get("FB_GRAPH_VERSION", DEFAULT_GRAPH_VERSION)
    add("Facebook smoke check", smoke.get("page_id") == page and smoke.get("graph_version") == version and bool(page),
        f"last: {smoke.get('page_name', '—')} {smoke.get('checked_at', '')} — run: studio.py publish --smoke facebook")
    return results
