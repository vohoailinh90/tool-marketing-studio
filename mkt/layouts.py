"""Slide layouts. Each one turns a slide spec into the HTML of the slide body.

A layout is registered with the fields a slide must give it, so `studio.py check`
can reject a slide before it is rendered half-empty. Every string goes through
`esc`/`fmt`, so slide text can never inject markup into the page.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath, PureWindowsPath

from .text import duration, esc, fmt, ui


IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".webp")


class AssetError(ValueError):
    pass


def resolve_asset(src, roots: list[Path]) -> Path:
    """The file an `image` slide may show: relative, no `..`, an image type, inside one of `roots`.

    Post text can come from an AI draft that read an untrusted README, so a slide
    must never be able to pull an arbitrary local file into a published image.
    """
    text = str(src or "")
    if not text or PurePosixPath(text).is_absolute() or PureWindowsPath(text).is_absolute() \
            or PureWindowsPath(text).drive or ".." in PurePosixPath(text.replace("\\", "/")).parts:
        raise AssetError(f"image src must be a relative path without '..': {text!r}")
    if PurePosixPath(text).suffix.lower() not in IMAGE_TYPES:
        raise AssetError(f"image src must be one of {', '.join(IMAGE_TYPES)}: {text!r}")
    for root in roots:
        candidate = (root / text).resolve()
        if candidate.is_relative_to(root.resolve()) and candidate.is_file():
            return candidate
    raise AssetError(f"image not found under the campaign or tool folder: {text!r}")


@dataclass
class Ctx:
    lang: str
    campaign_dir: Path
    tool_dir: Path | None = None
    link: str = ""        # tracked link for this post and language, "" when not set yet
    qr_svg: str = ""      # inline SVG of `link`, "" when there is no real link
    extra: dict = field(default_factory=dict)


LAYOUTS: dict[str, tuple] = {}

# Values a slide may give for fields that end up in a class name. Anything else falls
# back to the default here and is an error in `studio.py check` — never markup.
ENUMS = {
    "tone": ("bad", "ok", "accent"),
    "variant": ("before", "after"),
    "style": ("app", "sheet"),
    "cell_tone": ("ok", "warn", "bad", "muted"),
}

# The keys each layout reads. A key outside this list is an error in `check`, so a
# typo is caught and nothing unexpected rides along into the page.
FIELDS = {
    "cover": ("emoji", "eyebrow", "title", "subtitle", "badge"),
    "pains": ("eyebrow", "title", "items", "tone", "note"),
    "checklist": ("eyebrow", "title", "items", "tone", "note"),
    "chat": ("eyebrow", "title", "group", "messages", "note"),
    "flow": ("eyebrow", "title", "variant", "steps", "total_label", "note"),
    "stat": ("eyebrow", "before", "after", "value", "label", "caption"),
    "compare": ("eyebrow", "title", "before", "after", "note"),
    "table": ("eyebrow", "title", "columns", "rows", "style", "total_row", "note"),
    "features": ("eyebrow", "title", "items", "note"),
    "quote": ("text", "author", "role"),
    "poll": ("eyebrow", "question", "options", "hint"),
    "cta": ("emoji", "eyebrow", "title", "text", "keyword", "button", "show_link", "scan", "hint"),
    "email": ("eyebrow", "title", "subject", "from", "infobar", "buttons", "body", "note"),
    "timeline": ("eyebrow", "title", "items", "note"),
    "image": ("eyebrow", "title", "src", "caption", "note"),
}


def enum(value, kind: str, default: str) -> str:
    return value if value in ENUMS[kind] else default

# What each layout is for and which fields it reads (* = required). This is the schema the
# AI drafting prompt hands to Claude, so it is written for a reader, not for the code.
LAYOUT_DOCS = {
    "cover": "emoji, eyebrow, title*, subtitle, badge — the hook: the first image people see",
    "pains": "title*, items*: [{emoji, text}] (3–6), tone: bad|ok|accent, note — problems the reader has",
    "checklist": "title*, items*: [text] (3–6), note — who it is for, or what they get",
    "chat": "title, group, messages*: [{from, text} | {me: true, text}] (4–7), note — a relatable chat that shows the pain",
    "flow": "title*, variant: before|after, steps*: [{text, minutes?, emoji?}] (3–7), total_label, note — a process; "
            "minutes are whole numbers and their total is computed",
    "stat": "eyebrow, before + after (or value), label, caption — one big number",
    "compare": "title, before*: {label?, items: [text]}, after*: {label?, items: [text]}, note — before vs with the tool",
    "table": "title, columns*: [text], rows*: [[text | {text, tone: ok|warn|bad|muted}]], style: app|sheet, "
             "total_row: true|false, note — a screen or a spreadsheet as an illustration",
    "features": "title*, items*: [{emoji, title, text}] (2–6), note",
    "quote": "text*, author, role",
    "poll": "eyebrow, question*, options*: [text] (2–4), hint — invites one-letter comments",
    "cta": "emoji, title*, text, keyword, button, show_link: true|false — the last image",
    "email": "title, subject*, from, infobar, buttons: [text], body*, note — a mock e-mail",
    "timeline": "title*, items*: [{when, text}] (3–6), note",
    "image": "title, src* (an image file inside the campaign folder), caption — a real screenshot",
}


def layout(name: str, required: tuple[str, ...] = ()):
    def register(func):
        LAYOUTS[name] = (func, required)
        return func
    return register


def _title(s: dict, cls: str = "title") -> str:
    out = ""
    if s.get("eyebrow"):
        out += f'<p class="eyebrow">{fmt(s["eyebrow"])}</p>'
    if s.get("title"):
        out += f'<h2 class="{cls}">{fmt(s["title"])}</h2>'
    return out


def _note(s: dict) -> str:
    return f'<p class="note">{fmt(s["note"])}</p>' if s.get("note") else ""


def _hue(name: str) -> int:
    return int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:4], 16) % 360


@layout("cover", ("title",))
def cover(s: dict, ctx: Ctx) -> str:
    emoji = f'<div class="cover__emoji">{esc(s["emoji"])}</div>' if s.get("emoji") else ""
    eyebrow = f'<p class="eyebrow">{fmt(s["eyebrow"])}</p>' if s.get("eyebrow") else ""
    subtitle = f'<p class="cover__subtitle">{fmt(s["subtitle"])}</p>' if s.get("subtitle") else ""
    badge = f'<p class="cover__badge">{fmt(s["badge"])}</p>' if s.get("badge") else ""
    return (f'<div class="cover">{emoji}{eyebrow}<h1 class="cover__title">{fmt(s["title"])}</h1>'
            f"{subtitle}{badge}</div>")


@layout("pains", ("title", "items"))
def pains(s: dict, ctx: Ctx) -> str:
    tone = enum(s.get("tone"), "tone", "bad")
    default_icon = {"bad": "✗", "ok": "✓", "accent": "•"}.get(tone, "•")
    rows = "".join(
        f'<li class="card card--{esc(tone)}"><span class="card__icon">{esc(item.get("emoji", default_icon))}</span>'
        f'<span class="card__text">{fmt(item["text"])}</span></li>'
        for item in (_as_items(s["items"]))
    )
    return f'{_title(s)}<ul class="cards">{rows}</ul>{_note(s)}'


@layout("checklist", ("title", "items"))
def checklist(s: dict, ctx: Ctx) -> str:
    return pains({**s, "tone": s.get("tone", "ok")}, ctx)


@layout("chat", ("messages",))
def chat(s: dict, ctx: Ctx) -> str:
    msgs = []
    for m in s["messages"]:
        name = str(m.get("from", ""))
        if m.get("me"):
            msgs.append(f'<div class="msg msg--me"><p class="bubble">{fmt(m["text"])}</p></div>')
            continue
        # "Chị Hà" → H, "Hannah" → H, "佐藤" → 佐: the given name is the last word.
        initial = esc(m.get("initial") or (name.split()[-1][:1].upper() if name.split() else "?"))
        msgs.append(
            f'<div class="msg"><span class="avatar" style="--h:{_hue(name)}">{initial}</span>'
            f'<div class="msg__col"><span class="msg__name">{esc(name)}</span>'
            f'<p class="bubble">{fmt(m["text"])}</p></div></div>'
        )
    head = f'<div class="chat__head">💬 {esc(s["group"])}</div>' if s.get("group") else ""
    return f'{_title(s)}<div class="chat">{head}<div class="chat__body">{"".join(msgs)}</div></div>{_note(s)}'


@layout("flow", ("title", "steps"))
def flow(s: dict, ctx: Ctx) -> str:
    variant = enum(s.get("variant"), "variant", "after")
    steps, total = [], 0
    for index, step in enumerate(s["steps"], 1):
        minutes = step.get("minutes")
        time = ""
        if minutes is not None:
            total += int(minutes)
            time = f'<span class="flow__time">⏱ {esc(duration(minutes, ctx.lang))}</span>'
        marker = esc(step["emoji"]) if step.get("emoji") else str(index)
        steps.append(
            f'<li class="flow__step"><span class="flow__num">{marker}</span>'
            f'<span class="flow__text">{fmt(step["text"])}</span>{time}</li>'
        )
    total_html = ""
    if total:
        label = s.get("total_label") or ui("total", ctx.lang)
        total_html = (f'<div class="flow__total"><span>{fmt(label)}</span>'
                      f'<strong>~{esc(duration(total, ctx.lang))}</strong></div>')
    return f'{_title(s)}<ol class="flow flow--{esc(variant)}">{"".join(steps)}</ol>{total_html}{_note(s)}'


@layout("stat", ())
def stat(s: dict, ctx: Ctx) -> str:
    if s.get("before") and s.get("after"):
        figure = (f'<div class="stat__pair"><span class="stat__before">{fmt(s["before"])}</span>'
                  f'<span class="stat__arrow">→</span><span class="stat__after">{fmt(s["after"])}</span></div>')
    else:
        figure = f'<div class="stat__value">{fmt(s.get("value", ""))}</div>'
    eyebrow = f'<p class="eyebrow">{fmt(s["eyebrow"])}</p>' if s.get("eyebrow") else ""
    label = f'<p class="stat__label">{fmt(s["label"])}</p>' if s.get("label") else ""
    caption = f'<p class="stat__caption">{fmt(s["caption"])}</p>' if s.get("caption") else ""
    return f'<div class="stat">{eyebrow}{figure}{label}{caption}</div>'


@layout("compare", ("before", "after"))
def compare(s: dict, ctx: Ctx) -> str:
    def column(side: str, mark: str) -> str:
        data = s[side]
        label = data.get("label") or ui(side, ctx.lang)
        items = "".join(f'<li><span class="mark">{mark}</span><span>{fmt(t)}</span></li>' for t in data["items"])
        return f'<div class="side side--{side}"><h3>{fmt(label)}</h3><ul>{items}</ul></div>'
    return f'{_title(s)}<div class="compare">{column("before", "✗")}{column("after", "✓")}</div>{_note(s)}'


@layout("table", ("columns", "rows"))
def table(s: dict, ctx: Ctx) -> str:
    style = enum(s.get("style"), "style", "app")
    head = "".join(f"<th>{fmt(c)}</th>" for c in s["columns"])
    if style == "sheet":
        letters = "".join(f"<th>{chr(65 + i)}</th>" for i in range(len(s["columns"])))
        head = f'<tr class="sheet__letters"><th></th>{letters}</tr><tr><th>1</th>{head}</tr>'
    else:
        head = f"<tr>{head}</tr>"
    body = []
    for r, row in enumerate(s["rows"], 2):
        cells = []
        for cell in row:
            if isinstance(cell, dict):
                tone = enum(cell.get("tone"), "cell_tone", "")
                cells.append(f'<td class="tone-{esc(tone)}">{fmt(cell.get("text", ""))}</td>')
            else:
                cells.append(f"<td>{fmt(cell)}</td>")
        lead = f"<th>{r}</th>" if style == "sheet" else ""
        body.append(f"<tr>{lead}{''.join(cells)}</tr>")
    total = " has-total" if s.get("total_row") else ""
    return (f'{_title(s)}<div class="table-wrap table--{esc(style)}{total}"><table><thead>{head}</thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>{_note(s)}')


@layout("features", ("title", "items"))
def features(s: dict, ctx: Ctx) -> str:
    cards = "".join(
        f'<div class="feature"><span class="feature__icon">{esc(item.get("emoji", "✦"))}</span>'
        f'<h3>{fmt(item["title"])}</h3><p>{fmt(item.get("text", ""))}</p></div>'
        for item in s["items"]
    )
    return f'{_title(s)}<div class="features">{cards}</div>{_note(s)}'


@layout("quote", ("text",))
def quote(s: dict, ctx: Ctx) -> str:
    who = ""
    if s.get("author"):
        role = f'<span class="quote__role">{fmt(s["role"])}</span>' if s.get("role") else ""
        who = f'<p class="quote__who"><strong>{fmt(s["author"])}</strong>{role}</p>'
    return f'<figure class="quote"><span class="quote__mark">“</span><blockquote>{fmt(s["text"])}</blockquote>{who}</figure>'


@layout("poll", ("question", "options"))
def poll(s: dict, ctx: Ctx) -> str:
    options = "".join(
        f'<li><span class="poll__key">{chr(65 + i)}</span><span>{fmt(option)}</span></li>'
        for i, option in enumerate(s["options"])
    )
    hint = s.get("hint") or ui("poll_hint", ctx.lang)
    eyebrow = f'<p class="eyebrow">{fmt(s["eyebrow"])}</p>' if s.get("eyebrow") else ""
    return (f'{eyebrow}<h2 class="title">{fmt(s["question"])}</h2><ol class="poll">{options}</ol>'
            f'<p class="poll__hint">{fmt(hint)}</p>')


@layout("cta", ("title",))
def cta(s: dict, ctx: Ctx) -> str:
    text = f'<p class="cta__text">{fmt(s["text"])}</p>' if s.get("text") else ""
    keyword = ""
    if s.get("keyword"):
        keyword = (f'<div class="cta__keyword">{esc(ui("comment", ctx.lang))} '
                   f'<strong>“{esc(s["keyword"])}”</strong></div>')
    action = ""
    if s.get("show_link", True):
        if ctx.qr_svg:
            action = (f'<div class="cta__qr"><div class="qr">{ctx.qr_svg}</div>'
                      f'<p>{fmt(s.get("scan") or ui("scan", ctx.lang))}</p></div>')
        else:
            action = f'<p class="cta__hint">{fmt(s.get("hint") or ui("link_in_comment", ctx.lang))}</p>'
    button = f'<div class="cta__button">{fmt(s["button"])}</div>' if s.get("button") else ""
    emoji = f'<div class="cover__emoji">{esc(s["emoji"])}</div>' if s.get("emoji") else ""
    return f'<div class="cta">{emoji}{_title(s)}{text}{button}{keyword}{action}</div>'


@layout("email", ("subject", "body"))
def email(s: dict, ctx: Ctx) -> str:
    buttons = "".join(f"<span>{fmt(b)}</span>" for b in s.get("buttons", []))
    infobar = f'<div class="mail__infobar">ℹ️ {fmt(s["infobar"])}</div>' if s.get("infobar") else ""
    vote = f'<div class="mail__vote">{buttons}</div>' if buttons else ""
    sender = f'<p class="mail__from">{fmt(s["from"])}</p>' if s.get("from") else ""
    return (f'{_title(s)}<div class="mail"><div class="mail__bar"><i></i><i></i><i></i><span>Outlook</span></div>'
            f'<div class="mail__head"><p class="mail__subject">{fmt(s["subject"])}</p>{sender}</div>'
            f'{infobar}{vote}<div class="mail__body">{fmt(s["body"])}</div></div>{_note(s)}')


@layout("timeline", ("title", "items"))
def timeline(s: dict, ctx: Ctx) -> str:
    items = "".join(
        f'<li><span class="tl__when">{fmt(item.get("when", ""))}</span>'
        f'<span class="tl__text">{fmt(item["text"])}</span></li>'
        for item in s["items"]
    )
    return f'{_title(s)}<ol class="timeline">{items}</ol>{_note(s)}'


@layout("image", ("src",))
def image(s: dict, ctx: Ctx) -> str:
    roots = [ctx.campaign_dir] + ([ctx.tool_dir] if ctx.tool_dir else [])
    src = resolve_asset(s["src"], roots).as_uri()
    caption = f'<figcaption>{fmt(s["caption"])}</figcaption>' if s.get("caption") else ""
    return f'{_title(s)}<figure class="shot"><img src="{esc(src)}" alt="">{caption}</figure>{_note(s)}'


def _as_items(items) -> list[dict]:
    return [item if isinstance(item, dict) else {"text": item} for item in items]


def render_body(slide: dict, ctx: Ctx) -> str:
    func, _required = LAYOUTS[slide["layout"]]
    return func(slide, ctx)
