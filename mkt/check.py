"""`studio.py check`: everything about a campaign that is computable, checked before
anything is rendered, approved or published."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from . import diagram
from .i18n import LANGS
from .layouts import ENUMS, FIELDS, LAYOUTS, AssetError, resolve_asset
from .links import PLACEHOLDER, is_configured
from .model import POST_STATUSES, SLUG, TOOL_STATUSES, Campaign, Post
from .page import FORMATS
from .platforms import PLATFORMS
from .text import plain

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
TODO = re.compile(r"\bTODO\b")


def trie_pattern(words) -> str:
    """One alternation for many words with shared prefixes factored out, so a miss fails fast."""
    tree: dict = {}
    for word in words:
        node = tree
        for char in word:
            node = node.setdefault(char, {})
        node[""] = {}

    def walk(node: dict) -> str:
        alts = [re.escape(char) + walk(child) for char, child in sorted(node.items()) if char]
        if not alts:
            return ""
        group = alts[0] if len(alts) == 1 else "(?:" + "|".join(alts) + ")"
        return f"(?:{group})?" if "" in node else group
    return walk(tree)


# Every top-level domain in the root zone, so a bare domain is caught whatever its ending.
TLDS = {word for line in (Path(__file__).with_name("tlds.txt")).read_text(encoding="utf-8").splitlines()
        if not line.startswith("#") for word in line.split()}
# A link in any spelling a platform would still turn into a link: scheme (also hxxp and
# with spaces), www., or a bare domain. Text is NFKC-normalised first, so full-width
# letters and dots are caught too. A domain must not run on into a Latin letter (`TP.Huế` is not
# `.hu`), but may touch Japanese text on either side: it has no spaces (`詳細はexample.comへ`).
# Labels are capped at 63 characters and a domain at 10 dots, and the endings are one prefix trie,
# so a long run of labels is checked in linear time.
START, LABEL, MORE = r"(?<![a-z0-9-])", r"[a-z0-9-]{1,63}", r"(?:\.[a-z0-9-]{1,63}){0,10}"
END = r"(?![a-z0-9\u00c0-\u024f\u0300-\u036f\u1e00-\u1eff-])"   # ASCII, Latin with accents (Vietnamese)
URL = re.compile(
    r"(?i)(?:" + START + r"h[tx]{2}ps?\s*:\s*//|" + START + r"www\.|"
    + START + r"[a-z0-9][a-z0-9-]{0,62}" + MORE + r"\.(?:" + trie_pattern(TLDS) + r")" + END + r"|"
    + START + LABEL + MORE + r"\.[a-z]{2,}/[\w/%-])")   # any domain followed by a path


def has_url(text: str) -> bool:
    return bool(URL.search(unicodedata.normalize("NFKC", text)))


# Where a post may say {link}: the comment under a Facebook post, a LinkedIn caption, an X thread.
LINK_ALLOWED = {("facebook", "first_comment"), ("linkedin", "caption"), ("x", "thread")}
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
FULLWIDTH = str.maketrans("０１２３４５６７８９", "0123456789")
HOOK_LIMIT = 125        # Facebook folds a post behind "See more" after about this many characters
MAX_SLIDES = 10
POST_KEYS = ("id", "status", "format", "series", "link", "slides", "platforms", "notes")
# Layouts that state facts about the tool. chat/email/table/poll show made-up examples.
ILLUSTRATIVE = ("chat", "email", "table", "poll")


@dataclass(frozen=True)
class Issue:
    level: str   # "error" blocks approval and publishing; "warn" is advice
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.where}: {self.message}"


def has_errors(issues) -> bool:
    return any(issue.level == "error" for issue in issues)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def numbers(value) -> set[str]:
    """Every number in a value, separators dropped, so 500.000, 500,000 and ５００,０００ agree."""
    found = set()
    for text in strings(value):
        for token in NUMBER.findall(text.translate(FULLWIDTH)):
            found.add(re.sub(r"[.,]", "", token))
    return found


def claim_numbers(post: Post) -> set[str]:
    """Numbers in the parts of a post that state facts: claim-bearing slides and captions."""
    found = numbers(post.platforms)
    for slide in post.slides:
        if isinstance(slide, dict) and slide.get("layout") not in ILLUSTRATIVE:
            found |= numbers({k: v for k, v in slide.items() if k != "layout"})
            for step in slide.get("steps") or []:
                if isinstance(step, dict) and isinstance(step.get("minutes"), int):
                    found.add(str(step["minutes"]))
    return found


def x_length(text: str) -> int:
    """Length as X counts it: most non-Latin characters (CJK, Vietnamese ệ, emoji) weigh 2, a link 23."""
    total = 0
    for char in text.replace("{link}", "x" * 23):
        code = ord(char)
        light = code <= 4351 or 8192 <= code <= 8205 or 8208 <= code <= 8223 or 8242 <= code <= 8247
        total += 1 if light else 2
    return total


def check_brief(tool: str, brief: dict) -> list[Issue]:
    where = f"tools/{tool}/brief.yaml"
    if not brief:
        return [Issue("error", where, "missing or empty")]
    issues = [Issue("error", where, f"missing '{key}'") for key in ("slug", "name", "status") if not brief.get(key)]
    if brief.get("slug") and brief["slug"] != tool:
        issues.append(Issue("error", where, f"slug '{brief['slug']}' differs from the folder '{tool}'"))
    if brief.get("status") and brief["status"] not in TOOL_STATUSES:
        issues.append(Issue("error", where, f"status must be one of {', '.join(TOOL_STATUSES)}"))
    if not HEX.match(str((brief.get("brand") or {}).get("accent", ""))):
        issues.append(Issue("error", where, "brand.accent must be a #rrggbb colour"))
    if any(TODO.search(text) for text in strings(brief)):
        issues.append(Issue("warn", where, "still contains TODO"))
    return issues


def check_positioning(campaign: Campaign) -> list[Issue]:
    issues = []
    for lang in campaign.langs:
        where = f"tools/{campaign.tool}/positioning/{lang}.yaml"
        data = campaign.positioning.get(lang)
        if not data:
            issues.append(Issue("warn", where, "missing: AI drafts for this language have no positioning to start from"))
            continue
        for key in ("one_liner", "audience", "pains"):
            if not data.get(key):
                issues.append(Issue("error", where, f"missing '{key}'"))
        if any(TODO.search(text) for text in strings(data)):
            issues.append(Issue("warn", where, "still contains TODO"))
    return issues


def check_post(campaign: Campaign, post: Post) -> list[Issue]:
    where = f"{campaign.slug}/{post.lang}/{post.id}"
    data, issues = post.data, []
    final = post.status in ("ready", "posted")

    def add(level, message, spot=where):
        issues.append(Issue(level, spot, message))

    if not SLUG.match(post.id):
        add("error", "file name must use a-z, 0-9 and - only")
    if data.get("id") not in (None, post.id):
        add("error", f"id '{data.get('id')}' differs from the file name")
    for key in data:
        if key not in POST_KEYS:
            add("warn", f"unknown key '{key}' is ignored")
    if post.status not in POST_STATUSES:
        add("error", f"status must be one of {', '.join(POST_STATUSES)}")
    if not isinstance(post.format, str) or post.format not in FORMATS:
        add("error", f"format must be one of {', '.join(FORMATS)}")
    if not post.slides:
        add("error", "no slides")
    elif len(post.slides) > MAX_SLIDES:
        add("warn", f"{len(post.slides)} slides; keep a post to {MAX_SLIDES} or fewer")

    for text in strings({k: data.get(k) for k in ("series", "slides", "platforms")}):
        if has_url(text):
            add("error", "a URL is written into the post; links come only from campaign `links:` via {link}")
            break
    if any("{link}" in text for text in strings({k: data.get(k) for k in ("series", "slides")})):
        add("error", "{link} cannot go on an image; put it in the first comment")
    for platform, spec in post.platforms.items():
        for field, value in (spec.items() if isinstance(spec, dict) else []):
            if (platform, field) not in LINK_ALLOWED and any("{link}" in text for text in strings(value)):
                add("error", f"{{link}} is not allowed in {platform}.{field}")
    if any(TODO.search(text) for text in strings(data)):
        add("error" if final else "warn", "still contains TODO")

    roots = [campaign.dir, campaign.tool_dir]
    for index, slide in enumerate(post.slides, 1):
        spot = f"{where} slide {index}"
        if not isinstance(slide, dict) or "layout" not in slide:
            add("error", "a slide needs a 'layout'", spot)
            continue
        name = slide["layout"]
        if not isinstance(name, str) or name not in LAYOUTS:
            add("error", f"unknown layout '{name}' (known: {', '.join(sorted(LAYOUTS))})", spot)
            continue
        for key in LAYOUTS[name][1]:
            if slide.get(key) in (None, "", [], {}):
                add("error", f"layout '{name}' needs '{key}'", spot)
        for key in slide:
            if key != "layout" and key not in FIELDS[name]:
                add("error", f"layout '{name}' has no field '{key}' (fields: {', '.join(FIELDS[name])})", spot)
        for key, kind in (("tone", "tone"), ("variant", "variant"), ("style", "style")):
            if key in slide and slide[key] not in ENUMS[kind]:
                add("error", f"'{key}' must be one of {', '.join(ENUMS[kind])}", spot)
        for row in slide.get("rows") or [] if name == "table" else []:
            for cell in row if isinstance(row, list) else []:
                if isinstance(cell, dict) and "tone" in cell and cell["tone"] not in ENUMS["cell_tone"]:
                    add("error", f"table cell tone must be one of {', '.join(ENUMS['cell_tone'])}", spot)
        if name == "image" and slide.get("src"):
            try:
                resolve_asset(slide["src"], roots)
            except AssetError as exc:
                add("error", str(exc), spot)
        if name == "diagram" and slide.get("source") not in (None, "", [], {}):     # the required-field check reports those
            for problem in diagram.source_problems(slide["source"]):
                add("error", problem, spot)
        if name == "flow":
            for step in slide.get("steps") or []:
                if isinstance(step, dict) and "minutes" in step and not isinstance(step["minutes"], int):
                    add("error", "flow step 'minutes' must be a whole number", spot)

    wanted = [p for p in campaign.platforms if p in PLATFORMS]
    for platform, spec in post.platforms.items():
        spot = f"{where} {platform}"
        if platform not in PLATFORMS:
            add("error", f"unknown platform '{platform}' (known: {', '.join(PLATFORMS)})", spot)
            continue
        if not isinstance(spec, dict):
            add("error", "platform entry must be a mapping", spot)
            continue
        rules = PLATFORMS[platform]
        for key in spec:
            if key not in rules["fields"]:
                add("warn", f"unknown field '{key}' is ignored", spot)
        for key in rules["required"]:
            if not spec.get(key):
                add("error", f"needs '{key}'", spot)
        caption = str(spec.get("caption") or "")
        if "caption_limit" in rules and len(caption) > rules["caption_limit"]:
            add("error", f"caption is {len(caption)} chars; {platform} allows {rules['caption_limit']}", spot)
        if platform == "facebook" and caption:
            first_line = plain(caption).strip().split("\n", 1)[0]
            if len(first_line) > HOOK_LIMIT:
                add("warn", f"hook (first line) is {len(first_line)} chars; Facebook folds after ~{HOOK_LIMIT}", spot)
        for number, item in enumerate(spec.get("thread") or [], 1):
            if x_length(str(item)) > rules.get("item_limit", 10**9):
                add("error", f"thread item {number} is {x_length(str(item))} of {rules['item_limit']} weighted chars", spot)
    for platform in wanted:
        if platform not in post.platforms:
            add("error" if final else "warn", f"no text for campaign platform '{platform}'")

    target = data.get("link", "survey")
    if target and not isinstance(target, str):
        add("error", "link must name one of the campaign links")
    elif target:
        url = (campaign.data.get("links") or {}).get(target)
        if url is None:
            add("error", f"link '{target}' is not defined in campaign links")
        elif not is_configured(url):
            add("error" if final else "warn", f"links.{target} is not a real URL yet; the post would ship without its link")
    return issues


def check_campaign(campaign: Campaign) -> list[Issue]:
    where = f"campaigns/{campaign.slug}/campaign.yaml"
    data = campaign.data
    issues = check_brief(campaign.tool, campaign.brief) + check_positioning(campaign)
    for key in ("tool", "langs", "platforms", "goal"):
        if not data.get(key):
            issues.append(Issue("error", where, f"missing '{key}'"))
    for lang in campaign.langs:
        if lang not in LANGS:
            issues.append(Issue("error", where, f"unknown language '{lang}' (known: {', '.join(LANGS)})"))
    for platform in campaign.platforms:
        if platform not in PLATFORMS:
            issues.append(Issue("error", where, f"unknown platform '{platform}' (known: {', '.join(PLATFORMS)})"))
    for name, url in (data.get("links") or {}).items():
        if not is_configured(url) and PLACEHOLDER not in str(url):
            issues.append(Issue("error", where, f"links.{name} must be an http(s) URL or contain {PLACEHOLDER}"))
    keys = {(post.id, post.lang) for post in campaign.posts}
    for entry in data.get("schedule") or []:
        if (entry.get("post"), entry.get("lang")) not in keys:
            issues.append(Issue("error", where, f"schedule names unknown post {entry.get('post')}/{entry.get('lang')}"))
    if not campaign.posts:
        issues.append(Issue("error", where, "no posts in posts/<lang>/"))

    for post in campaign.posts:
        if post.lang not in campaign.langs:
            issues.append(Issue("warn", f"{campaign.slug}/{post.lang}/{post.id}", "language is not in the campaign's langs"))
        issues += check_post(campaign, post)

    # Each language is written on its own, so nothing ties the facts together but this:
    # the numbers a slot states should be the same numbers in every language.
    for slot in campaign.slots:
        versions = {post.lang: claim_numbers(post) for post in campaign.posts if post.id == slot}
        for lang in campaign.langs:
            if lang not in versions:
                issues.append(Issue("warn", f"{campaign.slug}/{slot}", f"no {lang} version"))
        if len(versions) > 1:
            union = set().union(*versions.values())
            for lang, found in versions.items():
                missing = sorted(union - found, key=lambda n: (len(n), n))
                if missing:
                    issues.append(Issue("warn", f"{campaign.slug}/{lang}/{slot}",
                                        f"numbers stated in another language but not here: {', '.join(missing)}"))
    return issues


def unsourced_numbers(campaign: Campaign, post: Post, extra: str = "") -> list[Issue]:
    """For an AI draft: a number the brief, positioning and campaign never stated is a claim
    nobody checked. Claim-bearing parts make it an error, made-up illustrations a warning."""
    allowed = numbers(campaign.brief) | numbers(campaign.positioning) | numbers(campaign.data) | numbers(extra)
    allowed |= {str(n) for n in range(0, 11)}       # counting words: 3 steps, 1 click, 10 questions
    where = f"{campaign.slug}/{post.lang}/{post.id}"
    issues = []
    bad = sorted(claim_numbers(post) - allowed, key=lambda n: (len(n), n))
    if bad:
        issues.append(Issue("error", where, f"numbers not found in the brief/positioning/campaign: {', '.join(bad)}"))
    illustrative = set()
    for slide in post.slides:
        if isinstance(slide, dict) and slide.get("layout") in ILLUSTRATIVE:
            illustrative |= numbers(slide)
    loose = sorted(illustrative - allowed, key=lambda n: (len(n), n))
    if loose:
        issues.append(Issue("warn", where, f"example numbers in illustrations — make sure they read as examples: {', '.join(loose)}"))
    return issues
