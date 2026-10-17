"""`studio.py render`: post YAML → one HTML page per slide → PNG, plus the platform text files.

Output per post and language, in campaigns/<slug>/export/<lang>/<post>/:
  01.png, 02.png, …         the images, in posting order
  facebook.txt, …           caption per platform, links filled in
  facebook-comment.txt      the first comment (where the link goes on Facebook)
  manifest.json             what was rendered from what: the approval gate compares its hash
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .approvals import content_sha, handle
from .check import Issue
from .diagram import DiagramError, render_in_page, text_warnings
from .fonts import FONT_DIR, FONT_ORIGIN, ensure_fonts, font_face_css
from .layouts import Ctx
from .links import post_link, qr_svg
from .model import Campaign, Post
from .page import FORMATS, build_page
from .platforms import platform_texts


def write_texts(campaign: Campaign, post: Post, out: Path) -> list[str]:
    written = []
    for platform in campaign.platforms:
        spec = post.platforms.get(platform)
        if not isinstance(spec, dict):
            continue
        for name, text in platform_texts(platform, spec, post_link(campaign, post, platform)).items():
            (out / name).write_text(text, encoding="utf-8")
            written.append(name)
    return written


def build_pages(campaign: Campaign, post: Post, config: dict, font_css: str = "") -> list[str]:
    link = post_link(campaign, post, "qr")
    ctx = Ctx(lang=post.lang, campaign_dir=campaign.dir, tool_dir=campaign.tool_dir,
              link=link, qr_svg=qr_svg(link))
    total = len(post.slides)
    return [
        build_page(slide, ctx, brand=campaign.brand, tool_name=campaign.tool_name,
                   series=str(post.data.get("series") or ""), handle=handle(config),
                   index=index, total=total, fmt_name=post.format, font_css=font_css)
        for index, slide in enumerate(post.slides, 1)
    ]


def _serve_font(route) -> None:
    name = route.request.url.rsplit("/", 1)[-1]
    path = FONT_DIR / name
    if not re.fullmatch(r"[A-Za-z]+-\d{3}\.ttf", name) or not path.is_file():
        route.abort()
        return
    route.fulfill(path=str(path), headers={"Access-Control-Allow-Origin": "*", "Content-Type": "font/ttf"})


def _launch(playwright):
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    return playwright.chromium.launch(proxy={"server": proxy} if proxy else None)


def render_posts(campaign: Campaign, posts: list[Post], config: dict, *, html_only: bool = False,
                 log=print) -> list[Issue]:
    """Render `posts`; returns warnings (overflowing slides). Errors in a post stop only that post."""
    issues: list[Issue] = []
    fonts = [] if html_only else ensure_fonts(log)
    font_css = font_face_css(fonts)
    build_root = campaign.root / "build" / campaign.slug

    def one(page, post: Post) -> None:
        where = f"{campaign.slug}/{post.lang}/{post.id}"
        pages = build_pages(campaign, post, config, font_css)
        html_dir = build_root / post.lang / post.id
        html_dir.mkdir(parents=True, exist_ok=True)
        for stale in html_dir.glob("*.html"):
            stale.unlink()
        html_files = []
        for index, html in enumerate(pages, 1):
            path = html_dir / f"{index:02d}.html"
            path.write_text(html, encoding="utf-8")
            html_files.append(path)
        if page is None:
            log(f"{where}: {len(html_files)} HTML page(s) in {html_dir}")
            return
        out = campaign.export_dir(post)
        out.mkdir(parents=True, exist_ok=True)
        for stale in list(out.glob("*.png")) + list(out.glob("*.txt")):
            stale.unlink()
        width, height = FORMATS[post.format]
        page.set_viewport_size({"width": width, "height": height})
        names, overflow, scales = [], [], []
        try:
            for index, path in enumerate(html_files, 1):
                page.goto(path.as_uri(), wait_until="load" if font_css else "networkidle")
                drawn = post.slides[index - 1].get("layout") == "diagram"
                if drawn:
                    render_in_page(page)
                fit = page.evaluate("fit()")
                scales.append(fit["scale"])
                if fit["overflow"]:
                    overflow.append(index)
                    issues.append(Issue("warn", f"{where} slide {index}", "text still overflows at the smallest size: shorten it"))
                for advice in text_warnings(page) if drawn else []:
                    issues.append(Issue("warn", f"{where} slide {index}", advice))
                name = f"{index:02d}.png"
                page.locator(".slide").screenshot(path=str(out / name))
                names.append(name)
        except DiagramError as exc:
            # A half-rendered post must not look rendered: drop what this run wrote, and the old manifest with it.
            for leftover in list(out.glob("*.png")) + list(out.glob("*.txt")) + [out / "manifest.json"]:
                leftover.unlink(missing_ok=True)
            issues.append(Issue("error", f"{where} slide {index}", str(exc)))
            return
        texts = write_texts(campaign, post, out)
        hashes = {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in names + texts}
        (out / "manifest.json").write_text(json.dumps({
            "sha": content_sha(campaign, post, config),
            "rendered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "engine": __version__,
            "format": post.format,
            "slides": names,
            "texts": texts,
            "overflow": overflow,
            "scales": scales,
            "files": hashes,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        log(f"{where}: {len(names)} image(s) → {out.relative_to(campaign.root)}")

    if html_only:
        for post in posts:
            one(None, post)
        return issues

    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = _launch(playwright)
        try:
            page = browser.new_page(device_scale_factor=1)
            page.route(f"{FONT_ORIGIN}/**", _serve_font)
            for post in posts:
                one(page, post)
        finally:
            browser.close()
    return issues
