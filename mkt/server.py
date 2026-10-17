"""The app's local API (FastAPI). `python app.py` serves it with the built web UI.

It holds the user's API keys and can publish, so it trusts nobody but the page it
served itself:
  * it listens on 127.0.0.1 only (app.py), and refuses any other Host header, which
    also defeats DNS rebinding;
  * every /api call must carry the session token that index.html was served with, and
    every /files download the same token as `?t=` — another website open in the same
    browser cannot read the page, so it cannot learn the token;
  * request bodies are JSON, so a cross-site form post cannot reach a handler.
All rules (checks, approval, publish refusals) stay in mkt/; this file only maps HTTP to them.
"""

from __future__ import annotations

import hmac
import re
import secrets as token_lib
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from . import ai, secrets
from .approvals import ApprovalError, approval_state, approve, blockers, manifest
from .check import check_campaign, check_post, has_errors
from .i18n import LANG_NAMES, LANGS
from .links import post_link
from .feedback import add_manual, all_feedback, scan_facebook
from .history import is_published, manual_rows, mark_posted, rows as history_rows, today
from .insights import gather
from .metrics import MetricsError, RATES, append_row, read_rows, totals, verdict
from .model import ROOT, SLUG, Post, SpecError, campaign_slugs, load_campaign, load_config, load_yaml
from .platforms import PLATFORMS
from .publish import (PublishError, build_pack, load_ledger, load_state, publish_facebook, resolve,
                      smoke_facebook)

FILE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")
STATUS_LINE = re.compile(r"(?m)^status:\s*\S+")


def issue_dicts(issues) -> list[dict]:
    return [{"level": i.level, "where": i.where, "message": i.message} for i in issues]


def create_app(root: Path = ROOT, *, port: int = 8765, dist: Path | None = None,
               token: str | None = None) -> FastAPI:
    app = FastAPI(title="Tool Marketing Studio", docs_url=None, redoc_url=None, openapi_url=None)
    session_token = token or token_lib.token_urlsafe(32)
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    dist = dist or root / "web" / "dist"
    app.state.token = session_token
    secrets.load_env(root)

    def config() -> dict:
        return load_config(root)

    def campaign(slug: str):
        if not SLUG.match(slug):
            raise HTTPException(404, "unknown campaign")
        try:
            return load_campaign(root, slug)
        except SpecError as exc:
            raise HTTPException(404, str(exc))

    def post_of(c, lang: str, post_id: str):
        if lang not in LANGS or not SLUG.match(post_id):
            raise HTTPException(404, "unknown post")
        try:
            return c.post(post_id, lang)
        except SpecError as exc:
            raise HTTPException(404, str(exc))

    def fail(exc: Exception, status: int = 400):
        raise HTTPException(status, secrets.redact(exc))

    @app.middleware("http")
    async def guard(request: Request, call_next):
        if request.headers.get("host") not in allowed_hosts:
            return JSONResponse({"detail": "forbidden host"}, status_code=403)
        path = request.url.path
        if path.startswith("/api/"):
            given = request.headers.get("x-studio-token", "")
            if not hmac.compare_digest(given, session_token):
                return JSONResponse({"detail": "missing or wrong session token: reload the page"}, status_code=403)
            if request.method in ("POST", "PUT") and "application/json" not in request.headers.get("content-type", ""):
                return JSONResponse({"detail": "JSON body required"}, status_code=415)
        if path.startswith("/files/"):
            if not hmac.compare_digest(request.query_params.get("t", ""), session_token):
                return JSONResponse({"detail": "forbidden"}, status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    # ------------------------------------------------------------- overview

    @app.get("/api/state")
    def state():
        ai_cfg = config().get("ai") or {}
        smoke = load_state(root).get("facebook") or {}
        return {
            "campaigns": campaign_slugs(root),
            "langs": [{"code": code, "name": LANG_NAMES[code]} for code in LANGS],
            "platforms": [{"code": code, "api": PLATFORMS[code]["api"] is not None} for code in PLATFORMS],
            "slots": [{"id": slot, "purpose": purpose} for slot, purpose in ai.SLOTS.items()],
            "ai": {"has_key": bool(secrets.get("ANTHROPIC_API_KEY") or secrets.get("ANTHROPIC_AUTH_TOKEN")),
                   "model": ai_cfg.get("model", "claude-opus-5-5")},
            "facebook": {"configured": bool(secrets.get("FB_PAGE_ID") and secrets.get("FB_PAGE_TOKEN")),
                         "page_name": smoke.get("page_name", ""), "checked_at": smoke.get("checked_at", "")},
        }

    @app.get("/api/campaigns/{slug}")
    def campaign_view(slug: str):
        c, cfg = campaign(slug), config()
        ledger = load_ledger(c)
        issues = check_campaign(c)
        posts = []
        for p in c.posts:
            own = check_post(c, p)
            approved, reason = approval_state(c, p, cfg)
            shown = manifest(c, p)
            posts.append({
                "id": p.id, "lang": p.lang, "status": p.status, "approved": approved, "approval": reason,
                "rendered": bool(shown), "thumb": shown.get("slides", [None])[0] if shown else None,
                "errors": sum(1 for i in own if i.level == "error"),
                "warnings": sum(1 for i in own if i.level == "warn"),
                "published": {pl: ("done" if is_published(ledger, p.id, p.lang, pl)
                                   else (ledger.get(f"{p.id}/{p.lang}/{pl}") or {}).get("state")) for pl in c.platforms},
            })
        return {
            "slug": c.slug, "tool": c.tool, "tool_name": c.tool_name, "brand": c.brand, "langs": c.langs,
            "platforms": c.platforms, "slots": c.slots, "goal": c.data.get("goal", ""),
            "links": {name: ("configured" if str(url).startswith("http") and "REPLACE_ME" not in str(url) else "placeholder")
                      for name, url in (c.data.get("links") or {}).items()},
            "positioning": c.positioning, "posts": posts,
            "issues": issue_dicts(i for i in issues if i.where.startswith(("tools/", "campaigns/"))),
        }

    # ------------------------------------------------------------- one post

    @app.get("/api/campaigns/{slug}/posts/{lang}/{post_id}")
    def post_view(slug: str, lang: str, post_id: str):
        c, cfg = campaign(slug), config()
        p = post_of(c, lang, post_id)
        shown = manifest(c, p)
        out = c.export_dir(p)
        approved, reason = approval_state(c, p, cfg)
        ledger = load_ledger(c)
        return {
            "id": p.id, "lang": p.lang, "status": p.status,
            "yaml": p.path.read_text(encoding="utf-8"),
            "issues": issue_dicts(check_post(c, p)),
            "manifest": shown,
            "texts": {name: (out / name).read_text(encoding="utf-8") for name in shown.get("texts", [])
                      if (out / name).exists()},
            "approved": approved, "approval": reason, "blockers": blockers(c, p, cfg),
            "links": {pl: post_link(c, p, pl) for pl in c.platforms},
            "ledger": {pl: ledger.get(f"{p.id}/{p.lang}/{pl}") for pl in c.platforms},
            "manual": {pl: manual_rows(ledger, p.id, p.lang, pl) for pl in c.platforms},
        }

    @app.put("/api/campaigns/{slug}/posts/{lang}/{post_id}")
    def post_save(slug: str, lang: str, post_id: str, body: dict = Body(...)):
        import yaml
        c = campaign(slug)
        p = post_of(c, lang, post_id)
        text = str(body.get("yaml", ""))
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            fail(f"invalid YAML: {exc}")
        if not isinstance(data, dict):
            fail("the post must be a YAML mapping")
        if not isinstance(data.get("slides", []), list) or not isinstance(data.get("platforms", {}), dict):
            fail("slides must be a list and platforms a mapping")
        if data.get("id") not in (None, post_id):
            fail(f"id must stay '{post_id}'")
        # Check the new version before it replaces the file: a shape the checker cannot read
        # must not overwrite a post that worked.
        try:
            issues = check_post(c, Post(post_id, lang, p.path, data))
        except (TypeError, AttributeError, ValueError, KeyError) as exc:
            fail(f"the post's structure is invalid: {exc}")
        p.path.write_text(text, encoding="utf-8")
        return {"issues": issue_dicts(issues)}

    @app.post("/api/campaigns/{slug}/posts/{lang}/{post_id}/status")
    def post_status(slug: str, lang: str, post_id: str, body: dict = Body(...)):
        status = body.get("status")
        if status not in ("draft", "ready"):
            fail("status must be draft or ready")
        p = post_of(campaign(slug), lang, post_id)
        text = p.path.read_text(encoding="utf-8")
        new, count = STATUS_LINE.subn(f"status: {status}", text, count=1)
        p.path.write_text(new if count else f"status: {status}\n{text}", encoding="utf-8")
        return {"status": status}

    @app.post("/api/campaigns/{slug}/posts/{lang}/{post_id}/render")
    def post_render(slug: str, lang: str, post_id: str, body: dict = Body(default={})):
        from .render import render_posts
        c, cfg = campaign(slug), config()
        p = post_of(c, lang, post_id)
        errors = [i for i in check_post(c, p) if i.level == "error"]
        if errors:
            return {"rendered": False, "issues": issue_dicts(errors)}
        warnings = render_posts(c, [p], cfg, log=lambda *_: None)
        return {"rendered": not has_errors(warnings), "issues": issue_dicts(warnings)}

    @app.post("/api/campaigns/{slug}/posts/{lang}/{post_id}/approve")
    def post_approve(slug: str, lang: str, post_id: str, body: dict = Body(...)):
        if body.get("confirm") is not True:
            fail("approval needs confirm: true")
        c = campaign(slug)
        try:
            return approve(c, post_of(c, lang, post_id), config(), by="app")
        except ApprovalError as exc:
            fail(exc, 409)

    @app.post("/api/campaigns/{slug}/posts/{lang}/{post_id}/publish/facebook")
    def post_publish(slug: str, lang: str, post_id: str, body: dict = Body(...)):
        c = campaign(slug)
        p = post_of(c, lang, post_id)
        try:
            # Only an explicit `false` sends for real; anything else (missing, null, 0, "no") is a dry run.
            confirm = body.get("confirm_page_name")
            return publish_facebook(c, p, config(), dry_run=body.get("dry_run") is not False,
                                    confirm_page_name=confirm if isinstance(confirm, str) else None,
                                    log=lambda *_: None)
        except PublishError as exc:
            fail(exc, 409)

    @app.post("/api/campaigns/{slug}/posts/{lang}/{post_id}/resolve/{platform}")
    def post_resolve(slug: str, lang: str, post_id: str, platform: str, body: dict = Body(...)):
        c = campaign(slug)
        try:
            return resolve(c, post_of(c, lang, post_id), platform, str(body.get("outcome")), str(body.get("url") or ""))
        except PublishError as exc:
            fail(exc, 409)

    @app.post("/api/facebook/smoke")
    def facebook_smoke(body: dict = Body(default={})):
        try:
            return smoke_facebook(root)
        except PublishError as exc:
            fail(exc, 409)

    # ------------------------------------------------------------- AI

    def ai_args(body: dict, c) -> tuple[list[str], list[str], str, str]:
        def listed(value, default):
            return value if isinstance(value, list) and value else default
        langs = [lang for lang in listed(body.get("langs"), c.langs) if lang in LANGS]
        platforms = [p for p in listed(body.get("platforms"), c.platforms) if p in PLATFORMS]
        return langs, platforms, str(body.get("guidance") or ""), str(body.get("readme") or "")

    @app.post("/api/campaigns/{slug}/ai/analyze")
    def ai_analyze(slug: str, body: dict = Body(...)):
        c = campaign(slug)
        langs, _, _, readme = ai_args(body, c)
        results = []
        for lang in langs:
            try:
                data, issues, usage = ai.analyze(c, lang, config(), readme=readme)
            except ai.AIError as exc:
                results.append({"lang": lang, "error": secrets.redact(exc)})
                continue
            saved = None if has_errors(issues) else str(ai.save_positioning(c, lang, data).relative_to(root))
            results.append({"lang": lang, "issues": issue_dicts(issues), "saved": saved, "usage": usage})
        return {"results": results}

    @app.post("/api/campaigns/{slug}/ai/draft")
    def ai_draft(slug: str, body: dict = Body(...)):
        c = campaign(slug)
        langs, platforms, guidance, readme = ai_args(body, c)
        slot = str(body.get("slot") or "")
        if not SLUG.match(slot):
            fail("the post id must use a-z, 0-9 and -")
        results = []
        for lang in langs:
            try:
                data, issues, usage = ai.draft_post(c, slot, lang, platforms, config(), guidance=guidance, readme=readme)
                saved = None
                if data is not None and not has_errors(issues):
                    saved = str(ai.save_post(c, lang, slot, data, overwrite=bool(body.get("overwrite"))).relative_to(root))
                results.append({"lang": lang, "issues": issue_dicts(issues), "saved": saved, "usage": usage})
            except ai.AIError as exc:
                results.append({"lang": lang, "error": secrets.redact(exc)})
        return {"results": results}

    @app.post("/api/campaigns/{slug}/ai/prompt")
    def ai_prompt(slug: str, body: dict = Body(...)):
        c = campaign(slug)
        langs, platforms, guidance, readme = ai_args(body, c)
        prompts = {}
        try:
            for lang in langs:
                if body.get("kind") == "analyze":
                    system, user = ai.analysis_prompt(c, lang, readme)
                else:
                    system, user = ai.post_prompt(c, str(body.get("slot") or ""), lang, platforms,
                                                  guidance=guidance, readme=readme)
                prompts[lang] = ai.paste_prompt(system, user)
        except ai.AIError as exc:
            fail(exc)
        return {"prompts": prompts}

    @app.post("/api/campaigns/{slug}/ai/paste")
    def ai_paste(slug: str, body: dict = Body(...)):
        c = campaign(slug)
        _, platforms, guidance, _ = ai_args(body, c)
        lang, text = str(body.get("lang")), str(body.get("text") or "")
        if lang not in LANGS:
            fail("unknown language")
        if body.get("kind") == "analyze":
            try:
                data, issues = ai.sanitize_positioning(ai.parse_yaml_answer(text), lang)
            except ai.AIError as exc:
                fail(exc)
            saved = None if has_errors(issues) else str(ai.save_positioning(c, lang, data).relative_to(root))
            return {"issues": issue_dicts(issues), "saved": saved}
        slot = str(body.get("slot") or "")
        if not SLUG.match(slot):
            fail("the post id must use a-z, 0-9 and -")
        data, issues = ai.accept_pasted_post(c, slot, lang, platforms, text, guidance=guidance)
        saved = None
        if data is not None and not has_errors(issues):
            try:
                saved = str(ai.save_post(c, lang, slot, data, overwrite=bool(body.get("overwrite"))).relative_to(root))
            except ai.AIError as exc:
                fail(exc, 409)
        return {"issues": issue_dicts(issues), "saved": saved}

    # ------------------------------------------------------------- measure

    @app.get("/api/campaigns/{slug}/metrics")
    def metrics(slug: str):
        c = campaign(slug)
        try:
            rows = read_rows(c.dir / "metrics.csv")
        except MetricsError as exc:
            fail(exc)
        validation = c.data.get("validation") or {}
        result = []
        for lang in c.langs:
            summary = totals([r for r in rows if r["lang"] == lang])
            decision, lines = verdict(summary, validation)
            result.append({"lang": lang, "verdict": decision, "lines": lines, "totals": summary,
                           "rates": {name: {"value": summary[name], "n": summary[RATES[name][1]]} for name in RATES}})
        return {"rows": len(rows), "langs": result}

    @app.post("/api/campaigns/{slug}/metrics")
    def metrics_add(slug: str, body: dict = Body(...)):
        c = campaign(slug)
        if body.get("lang") not in c.langs or body.get("platform") not in PLATFORMS:
            fail("unknown language or platform")
        try:
            return append_row(c.dir / "metrics.csv", body)
        except MetricsError as exc:
            fail(exc)

    # ------------------------------------------------------------- history and feedback

    @app.get("/api/history")
    def history():
        return {"rows": history_rows(root)}

    @app.post("/api/campaigns/{slug}/posts/{lang}/{post_id}/posted")
    def posted(slug: str, lang: str, post_id: str, body: dict = Body(...)):
        c = campaign(slug)
        try:
            return mark_posted(c, post_of(c, lang, post_id), str(body.get("platform")), url=str(body.get("url") or ""),
                               when=str(body.get("when") or ""), where=str(body.get("where") or ""),
                               note=str(body.get("note") or ""))
        except PublishError as exc:
            fail(exc, 409)

    @app.get("/api/campaigns/{slug}/feedback")
    def feedback_view(slug: str):
        return {"items": all_feedback(campaign(slug))}

    @app.post("/api/campaigns/{slug}/posts/{lang}/{post_id}/feedback/scan")
    def feedback_scan(slug: str, lang: str, post_id: str, body: dict = Body(default={})):
        c = campaign(slug)
        post_of(c, lang, post_id)
        try:
            data = scan_facebook(c, post_id, lang)
        except PublishError as exc:
            fail(exc, 409)
        return {"comments": len(data.get("comments") or []), "totals": data.get("totals") or {}}

    @app.post("/api/campaigns/{slug}/posts/{lang}/{post_id}/feedback")
    def feedback_add(slug: str, lang: str, post_id: str, body: dict = Body(...)):
        c = campaign(slug)
        post_of(c, lang, post_id)
        platform = str(body.get("platform"))
        if platform not in PLATFORMS:
            fail("unknown platform")
        totals = body.get("totals") if isinstance(body.get("totals"), dict) else {}
        data = add_manual(c, post_id, lang, platform, str(body.get("text") or ""), totals)
        return {"comments": len(data.get("comments") or []), "totals": data.get("totals") or {}}

    @app.get("/api/campaigns/{slug}/insights")
    def insights_list(slug: str):
        c = campaign(slug)
        base = c.dir / "insights"
        reports = []
        for path in sorted(base.glob("*.yaml"), reverse=True) if base.is_dir() else []:
            day, _, lang = path.stem.rpartition("-")
            reports.append({"date": day, "lang": lang, "report": load_yaml(path)})
        return {"reports": reports}

    def insights_inputs(c, body: dict) -> tuple[str, dict]:
        lang = str(body.get("lang") or "vi")
        if lang not in LANGS:
            fail("unknown language")
        data = gather(c)
        data["survey"] = str(body.get("survey") or "")
        return lang, data

    @app.post("/api/campaigns/{slug}/ai/insights")
    def ai_insights(slug: str, body: dict = Body(...)):
        c = campaign(slug)
        lang, data = insights_inputs(c, body)
        try:
            report, issues, usage = ai.insights(c, lang, config(), **data)
        except ai.AIError as exc:
            fail(exc, 502)
        if has_errors(issues):
            return {"issues": issue_dicts(issues), "saved": None, "usage": usage}
        paths = ai.save_insights(c, lang, report, day=today())
        return {"issues": issue_dicts(issues), "saved": [str(p.relative_to(root)) for p in paths],
                "report": report, "usage": usage}

    @app.post("/api/campaigns/{slug}/ai/insights/prompt")
    def ai_insights_prompt(slug: str, body: dict = Body(...)):
        c = campaign(slug)
        lang, data = insights_inputs(c, body)
        system, user = ai.insights_prompt(c, lang, **data)
        return {"prompt": ai.paste_prompt(system, user)}

    @app.post("/api/campaigns/{slug}/ai/insights/paste")
    def ai_insights_paste(slug: str, body: dict = Body(...)):
        c = campaign(slug)
        lang, data = insights_inputs(c, body)
        try:
            report = ai.parse_yaml_answer(str(body.get("text") or ""))
        except ai.AIError as exc:
            fail(exc)
        issues = ai.check_insights(report, data["feedback"])
        if has_errors(issues):
            return {"issues": issue_dicts(issues), "saved": None}
        paths = ai.save_insights(c, lang, report, day=today())
        return {"issues": issue_dicts(issues), "saved": [str(p.relative_to(root)) for p in paths], "report": report}

    # ------------------------------------------------------------- files

    @app.get("/files/{slug}/{lang}/{post_id}/{name}")
    def export_file(slug: str, lang: str, post_id: str, name: str):
        c = campaign(slug)
        p = post_of(c, lang, post_id)
        if not FILE_NAME.match(name) or not name.endswith(".png"):
            raise HTTPException(404)
        path = c.export_dir(p) / name
        if not path.is_file():
            raise HTTPException(404)
        return FileResponse(path, media_type="image/png")

    @app.get("/files/{slug}/{lang}/{post_id}/pack/{platform}")
    def pack_file(slug: str, lang: str, post_id: str, platform: str):
        c = campaign(slug)
        try:
            path = build_pack(c, post_of(c, lang, post_id), platform, config())
        except PublishError as exc:
            raise HTTPException(409, secrets.redact(exc))
        return FileResponse(path, media_type="application/zip", filename=path.name)

    # ------------------------------------------------------------- the UI

    def index() -> HTMLResponse:
        page = dist / "index.html"
        if not page.exists():
            return HTMLResponse("<h1>web/dist is missing</h1><p>Run <code>npm run build</code> in web/.</p>", 500)
        html = page.read_text(encoding="utf-8").replace(
            "</head>", f'<meta name="studio-token" content="{session_token}"></head>', 1)
        return HTMLResponse(html)

    @app.get("/assets/{name}")
    def asset(name: str):
        path = dist / "assets" / name
        if not FILE_NAME.match(name) or not path.is_file():
            raise HTTPException(404)
        return FileResponse(path)

    @app.get("/favicon.svg")
    def favicon():
        path = dist / "favicon.svg"
        if not path.is_file():
            raise HTTPException(404)
        return FileResponse(path, media_type="image/svg+xml")

    @app.get("/{rest:path}")
    def spa(rest: str):
        if rest.startswith(("api/", "files/")):
            raise HTTPException(404)
        return index()

    return app



