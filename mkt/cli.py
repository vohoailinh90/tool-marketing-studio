"""Command line for the studio. `python studio.py --help` lists every command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import secrets
from .check import check_campaign, check_post, has_errors
from .i18n import LANGS
from .model import ROOT, SpecError, campaign_slugs, load_campaign, load_config


def _print_issues(issues) -> None:
    for issue in issues:
        print(issue)
    errors = sum(1 for i in issues if i.level == "error")
    print(f"{errors} error(s), {len(issues) - errors} warning(s)")


def _posts(campaign, ids, langs):
    chosen = [p for p in campaign.posts
              if (not ids or p.id in ids) and (not langs or p.lang in langs) and p.lang in campaign.langs]
    if not chosen:
        raise SpecError("no post matches the --post/--lang filter")
    return chosen


def cmd_list(args, root, config):
    from .approvals import approval_state
    from .history import is_published
    from .publish import load_ledger
    for slug in campaign_slugs(root):
        campaign = load_campaign(root, slug)
        ledger = load_ledger(campaign)
        print(f"{slug}  ({campaign.tool_name}; {', '.join(campaign.langs)}; {', '.join(campaign.platforms)})")
        for post in campaign.posts:
            approved, why = approval_state(campaign, post, config)
            sent = [p for p in campaign.platforms if is_published(ledger, post.id, post.lang, p)]
            print(f"  {post.id:<18} {post.lang}  {post.status:<6}  {'approved' if approved else why}"
                  f"{'  published: ' + ', '.join(sent) if sent else ''}")


def cmd_check(args, root, config):
    issues = []
    for slug in args.campaign or campaign_slugs(root):
        issues += check_campaign(load_campaign(root, slug))
    _print_issues(issues)
    return 1 if has_errors(issues) else 0


def cmd_render(args, root, config):
    from .render import render_posts
    campaign = load_campaign(root, args.campaign)
    posts = _posts(campaign, args.post, args.lang)
    blocked = []
    for post in posts:
        errors = [i for i in check_post(campaign, post) if i.level == "error"]
        if errors:
            blocked.append(post)
            _print_issues(errors)
    posts = [p for p in posts if p not in blocked]
    warnings = render_posts(campaign, posts, config, html_only=args.html_only)
    for issue in warnings:
        print(issue)
    return 1 if blocked or has_errors(warnings) else 0


def cmd_approve(args, root, config):
    from .approvals import ApprovalError, approve, blockers
    campaign = load_campaign(root, args.campaign)
    post = campaign.post(args.post, args.lang)
    reasons = blockers(campaign, post, config)
    if reasons:
        print("cannot approve:\n- " + "\n- ".join(reasons))
        return 1
    out = campaign.export_dir(post)
    print(f"== {post.key} — read it as your audience will:\n")
    for text in sorted(out.glob("*.txt")):
        print(f"--- {text.name}\n{text.read_text(encoding='utf-8')}")
    print(f"--- images: {', '.join(p.name for p in sorted(out.glob('*.png')))} in {out.relative_to(root)}")
    if not args.yes and input("\nApprove exactly this? [y/N] ").strip().lower() != "y":
        print("not approved")
        return 1
    try:
        entry = approve(campaign, post, config, by=args.by)
    except ApprovalError as exc:
        print(f"cannot approve: {exc}")
        return 1
    print(f"approved {post.key} at {entry['at']}")
    return 0


def cmd_pack(args, root, config):
    from .publish import build_pack
    campaign = load_campaign(root, args.campaign)
    for post in _posts(campaign, args.post, args.lang):
        for platform in args.platform or campaign.platforms:
            print(build_pack(campaign, post, platform, config).relative_to(root))
    return 0


def cmd_publish(args, root, config):
    from .publish import PublishError, publish_facebook, resolve, smoke_facebook
    try:
        if args.smoke:
            info = smoke_facebook(root)
            print(f"OK: the token reaches the Page '{info['page_name']}' ({info['page_id']}), Graph {info['graph_version']}")
            return 0
        if not (args.campaign and args.post and args.lang):
            print("publish needs CAMPAIGN --post ID --lang LANG (or --smoke facebook)")
            return 2
        campaign = load_campaign(root, args.campaign)
        post = campaign.post(args.post[0], args.lang[0])
        if args.resolve:
            row = resolve(campaign, post, args.platform_one, args.resolve, args.url or "")
            print(f"{post.key}/{args.platform_one}: {row['state']}")
            return 0
        if args.platform_one != "facebook":
            print(f"'{args.platform_one}' has no API publishing: use `studio.py pack` and post by hand")
            return 2
        dry_run = not args.yes
        confirm = None
        if not dry_run:
            confirm = input("Type the Facebook Page name to confirm: ")
        result = publish_facebook(campaign, post, config, confirm_page_name=confirm, dry_run=dry_run)
        if result.get("dry_run"):
            print("DRY RUN — nothing was sent. These requests would be made:")
            print("\n".join(f"  {step}" for step in result["steps"]))
            print("Send for real with --yes.")
        else:
            print(f"published: {result.get('url')}")
        return 0
    except (PublishError, SpecError) as exc:
        print(f"refused: {secrets.redact(exc)}")
        return 1


def _ai_target(args, root):
    campaign = load_campaign(root, args.campaign)
    readme = Path(args.readme).read_text(encoding="utf-8") if args.readme else ""
    return campaign, readme


def cmd_draft(args, root, config):
    from .ai import AIError, draft_post, save_post
    campaign, readme = _ai_target(args, root)
    platforms = args.platform or campaign.platforms
    status = 0
    for lang in args.lang or campaign.langs:
        try:
            data, issues, usage = draft_post(campaign, args.post, lang, platforms, config,
                                             guidance=args.guidance or "", readme=readme)
        except AIError as exc:
            print(f"{lang}: {secrets.redact(exc)}")
            status = 1
            continue
        print(f"{lang}: {usage['input_tokens']} input + {usage['output_tokens']} output tokens")
        _print_issues(issues)
        if data is None or has_errors(issues):
            status = 1
            continue
        print(f"saved {save_post(campaign, lang, args.post, data, overwrite=args.overwrite).relative_to(root)}")
    return status


def cmd_analyze(args, root, config):
    from .ai import AIError, analyze, save_positioning
    campaign, readme = _ai_target(args, root)
    for lang in args.lang or campaign.langs:
        try:
            data, issues, usage = analyze(campaign, lang, config, readme=readme)
        except AIError as exc:
            print(f"{lang}: {secrets.redact(exc)}")
            return 1
        _print_issues(issues)
        if not has_errors(issues):
            print(f"saved {save_positioning(campaign, lang, data).relative_to(root)}")
    return 0


def cmd_prompt(args, root, config):
    from .ai import analysis_prompt, paste_prompt, post_prompt
    campaign, readme = _ai_target(args, root)
    lang = args.lang[0] if args.lang else campaign.langs[0]
    if args.post:
        system, user = post_prompt(campaign, args.post, lang, args.platform or campaign.platforms,
                                   guidance=args.guidance or "", readme=readme)
    else:
        system, user = analysis_prompt(campaign, lang, readme)
    print(paste_prompt(system, user))
    return 0


def cmd_paste(args, root, config):
    from .ai import AIError, accept_pasted_post, save_post
    campaign = load_campaign(root, args.campaign)
    text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    lang = args.lang[0]
    data, issues = accept_pasted_post(campaign, args.post, lang, args.platform or campaign.platforms, text,
                                      guidance=args.guidance or "")
    _print_issues(issues)
    if data is None or has_errors(issues):
        return 1
    try:
        print(f"saved {save_post(campaign, lang, args.post, data, overwrite=args.overwrite).relative_to(root)}")
    except AIError as exc:
        print(exc)
        return 1
    return 0


def cmd_metrics(args, root, config):
    from .metrics import MetricsError, read_rows, report
    campaign = load_campaign(root, args.campaign)
    try:
        rows = read_rows(campaign.dir / "metrics.csv")
    except MetricsError as exc:
        print(exc)
        return 1
    if not rows:
        print(f"no rows yet in {(campaign.dir / 'metrics.csv').relative_to(root)}")
        return 0
    print(report(rows, campaign.data.get("validation") or {}, campaign.langs))
    return 0


def cmd_survey(args, root, config):
    from .survey import summarize
    print(summarize(Path(args.csv), column=args.column or "", split=args.split))
    return 0


def cmd_new(args, root, config):
    from .scaffold import ScaffoldError, new_tool
    try:
        made = new_tool(root, args.slug, args.name, args.repo or "")
    except ScaffoldError as exc:
        print(exc)
        return 1
    for path in made:
        print(f"created {path.relative_to(root)}")
    return 0


def cmd_doctor(args, root, config):
    from .doctor import run
    results = run(root, live=args.live, config=config)
    for name, ok, detail in results:
        print(f"{'✓' if ok else '✗'} {name:<28} {detail}")
    return 0


def cmd_history(args, root, config):
    from .history import as_markdown, rows
    history = rows(root)
    if args.markdown:
        print(as_markdown(history), end="")
        return 0
    if not history:
        print("nothing published yet")
    for r in history:
        print(f"{r['published_at'][:16].replace('T', ' ')}  {r['tool_name']}  {r['post']}/{r['lang']}  {r['platform']}"
              f"  {r['method']}  {r['where']}  comments={r['comments']}  {r['url']}")
    return 0


def cmd_posted(args, root, config):
    from .history import mark_posted
    from .publish import PublishError
    campaign = load_campaign(root, args.campaign)
    try:
        row = mark_posted(campaign, campaign.post(args.post, args.lang), args.platform, url=args.url or "",
                          when=args.at or "", where=args.where or "", note=args.note or "")
    except PublishError as exc:
        print(f"refused: {exc}")
        return 1
    print(f"recorded {args.post}/{args.lang}/{args.platform} at {row['published_at']}")
    return 0


def cmd_feedback(args, root, config):
    from .feedback import add_manual, scan_facebook
    from .publish import PublishError
    campaign = load_campaign(root, args.campaign)
    campaign.post(args.post, args.lang)
    try:
        if args.action == "scan":
            data = scan_facebook(campaign, args.post, args.lang)
        else:
            text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
            data = add_manual(campaign, args.post, args.lang, args.platform, text)
    except PublishError as exc:
        print(f"refused: {secrets.redact(exc)}")
        return 1
    print(f"{len(data.get('comments') or [])} comment(s) stored; totals {data.get('totals') or {}}")
    return 0


def cmd_insights(args, root, config):
    from .ai import AIError, insights, save_insights
    from .history import today
    from .insights import gather
    campaign = load_campaign(root, args.campaign)
    data = gather(campaign)
    data["survey"] = Path(args.survey).read_text(encoding="utf-8") if args.survey else ""
    try:
        report, issues, usage = insights(campaign, args.lang, config, **data)
    except AIError as exc:
        print(secrets.redact(exc))
        return 1
    _print_issues(issues)
    if has_errors(issues):
        return 1
    for path in save_insights(campaign, args.lang, report, day=today()):
        print(f"saved {path.relative_to(root)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="studio.py", description="Tool Marketing Studio")
    sub = parser.add_subparsers(dest="command", required=True)

    def campaign_arg(p, required=True):
        p.add_argument("campaign", nargs=None if required else "?", help="campaign folder name")

    def filters(p):
        p.add_argument("--post", action="append", help="post id (repeatable)")
        p.add_argument("--lang", action="append", choices=LANGS, help="language (repeatable)")

    p = sub.add_parser("list", help="campaigns, posts, approval and publish state"); p.set_defaults(func=cmd_list)
    p = sub.add_parser("check", help="validate campaigns (exit 1 on errors)")
    p.add_argument("campaign", nargs="*"); p.set_defaults(func=cmd_check)
    p = sub.add_parser("render", help="render posts to PNG + platform texts"); campaign_arg(p); filters(p)
    p.add_argument("--html-only", action="store_true", help="write HTML pages only, no browser")
    p.set_defaults(func=cmd_render)
    p = sub.add_parser("approve", help="review the rendered post and approve exactly this version")
    campaign_arg(p); p.add_argument("--post", required=True); p.add_argument("--lang", required=True, choices=LANGS)
    p.add_argument("--by", default=""); p.add_argument("--yes", action="store_true", help="skip the y/N prompt")
    p.set_defaults(func=cmd_approve)
    p = sub.add_parser("pack", help="zip images + texts per platform for manual posting"); campaign_arg(p); filters(p)
    p.add_argument("--platform", action="append"); p.set_defaults(func=cmd_pack)
    p = sub.add_parser("publish", help="post to the Facebook Page (dry-run unless --yes)")
    p.add_argument("campaign", nargs="?"); filters(p)
    p.add_argument("--platform", dest="platform_one", default="facebook")
    p.add_argument("--smoke", choices=["facebook"], help="check the token reaches the Page; required once")
    p.add_argument("--yes", action="store_true", help="really send (asks for the Page name)")
    p.add_argument("--resolve", choices=["done", "failed"], help="settle a pending attempt after checking the Page")
    p.add_argument("--url", help="with --resolve done: the post's URL")
    p.set_defaults(func=cmd_publish)

    for name, func, text in (("draft", cmd_draft, "AI: write a post per language"),
                             ("analyze", cmd_analyze, "AI: positioning per language"),
                             ("prompt", cmd_prompt, "print the AI prompt for copy-paste into claude.ai")):
        p = sub.add_parser(name, help=text); campaign_arg(p)
        if name == "analyze":
            p.add_argument("--lang", action="append", choices=LANGS)
        else:
            p.add_argument("--post", required=(name == "draft"), help="post slot, e.g. 01-pain")
            p.add_argument("--lang", action="append", choices=LANGS)
            p.add_argument("--platform", action="append")
            p.add_argument("--guidance", help="your notes for this post")
        p.add_argument("--readme", help="path to the tool's README to include (sent to the AI)")
        if name == "draft":
            p.add_argument("--overwrite", action="store_true", help="replace an existing draft")
        p.set_defaults(func=func)
    p = sub.add_parser("paste", help="check and save an AI answer pasted from claude.ai"); campaign_arg(p)
    p.add_argument("--post", required=True); p.add_argument("--lang", action="append", required=True, choices=LANGS)
    p.add_argument("--platform", action="append"); p.add_argument("--guidance")
    p.add_argument("--file", help="file holding the answer (default: stdin)")
    p.add_argument("--overwrite", action="store_true"); p.set_defaults(func=cmd_paste)

    p = sub.add_parser("metrics", help="rates and GO / NOT_YET / INSUFFICIENT_DATA per language")
    campaign_arg(p); p.set_defaults(func=cmd_metrics)
    p = sub.add_parser("survey", help="answer counts from a Forms CSV export")
    p.add_argument("csv"); p.add_argument("--column"); p.add_argument("--split", action="store_true",
                                                                       help="split checkbox answers on commas")
    p.set_defaults(func=cmd_survey)
    p = sub.add_parser("new", help="scaffold a new tool and campaign")
    p.add_argument("slug"); p.add_argument("--name", required=True); p.add_argument("--repo")
    p.set_defaults(func=cmd_new)
    p = sub.add_parser("history", help="every published post: tool, platform, time, link, comments")
    p.add_argument("--markdown", action="store_true"); p.set_defaults(func=cmd_history)
    p = sub.add_parser("posted", help="record a post you published by hand")
    campaign_arg(p); p.add_argument("--post", required=True); p.add_argument("--lang", required=True, choices=LANGS)
    p.add_argument("--platform", required=True); p.add_argument("--url"); p.add_argument("--at", help="YYYY-MM-DD HH:MM")
    p.add_argument("--where", help="group / profile / page name"); p.add_argument("--note")
    p.set_defaults(func=cmd_posted)
    p = sub.add_parser("feedback", help="scan Page comments, or add pasted comments")
    p.add_argument("action", choices=["scan", "add"]); campaign_arg(p)
    p.add_argument("--post", required=True); p.add_argument("--lang", required=True, choices=LANGS)
    p.add_argument("--platform", default="facebook"); p.add_argument("--file", help="pasted comments (default: stdin)")
    p.set_defaults(func=cmd_feedback)
    p = sub.add_parser("insights", help="AI: analyse demand from history, metrics and comments")
    campaign_arg(p); p.add_argument("--lang", default="vi", choices=LANGS, help="language of the report")
    p.add_argument("--survey", help="file with a survey summary (studio.py survey output)")
    p.set_defaults(func=cmd_insights)
    p = sub.add_parser("doctor", help="check this machine is ready")
    p.add_argument("--live", action="store_true", help="also make one tiny Claude API call")
    p.set_defaults(func=cmd_doctor)
    return parser


def main(argv=None, root: Path = ROOT) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")   # Windows consoles default to cp1252
    args = build_parser().parse_args(argv)
    secrets.load_env(root)
    try:
        return args.func(args, root, load_config(root)) or 0
    except SpecError as exc:
        print(f"error: {exc}")
        return 1
