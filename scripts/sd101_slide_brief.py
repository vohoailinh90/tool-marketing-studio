#!/usr/bin/env python3
"""Turn a written System Design lesson into the brief a session builds its Moda deck from.

A deck is built from the lesson and nothing else (docs/sd101-slides.md), so the part of the work that is only reading
the lesson is computable and belongs in a script: which line of the lesson goes on which slide, which colour a concept
keeps from the first slide to the last, which lines are still longer than the 10-word budget. What stays with the
session is the part that is language and design: condensing each line to its budget and drawing the slide.

  python3 scripts/sd101_slide_brief.py sd-01-027                 # a Markdown brief to build from
  python3 scripts/sd101_slide_brief.py sd-01-027 sd-01-028       # several lessons, one after the other
  python3 scripts/sd101_slide_brief.py sd-01-027 --json          # the same, for a tool

The brief only copies lines of the lesson, so it adds no number, claim or example. It does not claim a deck (use
`sd101_slides.py claim` first) and it writes no file. Exit 0 on success, 1 when a lesson cannot be read, 2 on bad usage.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STORE = ROOT / "system-design-101" / "vi"

LESSON_ID = re.compile(r"sd-(\d{2})-(\d{3})")
# docs/sd101-slides.md: 8 to 10 slides. A deck always holds 6 fixed roles (cover, situation, summary, check question,
# deep dive, terms and sources), so 2 to 4 slides are left for the lesson's concepts.
SLIDE_COUNTS = range(8, 11)
FIXED_SLIDES = 6
CONCEPT_SLIDES = range(SLIDE_COUNTS.start - FIXED_SLIDES, SLIDE_COUNTS.stop - FIXED_SLIDES)
WORD_BUDGET = 10  # words per bullet
# One colour per concept, the same on every slide of the deck: (name, on cream, on dark).
CONCEPT_COLOURS = (("blue", "#1F3FD1", "#7C93FF"), ("amber", "#B45309", "#FFB454"),
                   ("teal", "#0F766E", "#3DD6A0"), ("red", "#E8472B", "#FF6A4D"))
LAYOUTS = ("flow", "cards", "numbered rows", "sequence diagram", "steps")  # rotated so neighbours differ

DETAILS = re.compile(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", re.S)
IMAGE = re.compile(r"^!\[(.*?)\]\((.*?)\)\s*$")
LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
# A typed address (scheme://...) never goes on a slide. The lookbehind lets a match start only at the start of a word, so a
# long word is scanned once and not once per suffix (the quadratic case scripts/sd101_check.py strip_urls was written for).
ADDRESS = re.compile(r"(?<![A-Za-z0-9+.\-])[A-Za-z][A-Za-z0-9+.\-]*://[^\s<>]+")
ADDRESS_TOKEN = "[address]"
# "1 · Simple", "2. Tổ chức": the mark of a figure card's heading, as against a bold line inside a card.
ORDINAL = re.compile(r"^\d+\s*[·.:)]")
# "1. **Label.** text": an entry of a Markdown ordered list is a bullet like "- text" is.
ORDERED = re.compile(r"^\d+[.)]\s+")
TABLE_ROW = re.compile(r"^\|")
# *emphasis*: the stars hug the words, so "2 * 3 * 4" is left alone
EMPHASIS = re.compile(r"\*(?=\S)([^*\n]+?)(?<=\S)\*")
SOURCE_NAME_WORDS = 12  # a source bullet without a link is named by its text up to the first colon, at most this long
# The `##` sections that hold what the summary slide needs: the lesson's limits, myths and how to choose. Other sections
# are the lesson's body (a catalogue, an experiment) and are not summary material.
TAKEAWAY_PREFIXES = ("Giới hạn", "Ngộ nhận", "Chọn", "Ba câu hỏi")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
LEAD = re.compile(r"^\*\*(.+?)\*\*\s*(.*)$", re.S)
BOLD_LEAD = re.compile(r"^\*\*.+?\*\*")
BOLD_WEIGHTS = {"bold", "600", "700", "800", "900"}
TERM = re.compile(r"^\*\*(.+?)\*\*\s*\((.+?)\)\s*[—–-]\s*(.+)$", re.S)

GLOSSARY_SECTION = "Từ viết tắt"
FIGURE_SECTION = "Đọc hình"
QUESTION_SECTION = "Nhìn hình"  # "Nhìn hình thử trả lời" and "Nhìn hình trả lời"
SOURCES_SECTION = "Nguồn đối chiếu"
ANSWER_SUMMARY = "đáp án"


class BriefError(Exception):
    """The lesson cannot be turned into a brief."""


@dataclasses.dataclass
class Line:
    """One line of the lesson that goes on a slide, with the size of the job to fit it."""
    text: str
    words: int
    over_budget: bool


@dataclasses.dataclass
class Concept:
    label: str
    text: str
    label_derived: bool  # no bold lead in the lesson, so the label is the first words of the line
    colour: str


@dataclasses.dataclass
class Slide:
    number: int
    role: str
    background: str
    layout: str
    footer: str
    material: dict


@dataclasses.dataclass
class Brief:
    lesson: str
    number: str
    title: str
    canvas_name: str
    slide_count: int
    figure_alt: str
    concept_source: str
    colours: list
    slides: list
    warnings: list


@dataclasses.dataclass
class Parsed:
    title: str
    intro: list
    intro_bullets: list
    alt: str
    sections: dict
    details: list
    opening: tuple = ("", "")  # (hook, rest): the first paragraph cut at its bold lead, or at its first sentence


def clean(text: str) -> str:
    """Plain text of a Markdown fragment: links keep their label, a typed address becomes `[address]`, bold, italic and code
    marks go, spaces collapse."""
    text = ADDRESS.sub(ADDRESS_TOKEN, LINK.sub(r"\1", text))
    text = EMPHASIS.sub(r"\1", text.replace("**", "")).replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def line(text: str, budget: bool = True) -> Line:
    words = len(text.split())
    return Line(text, words, budget and words > WORD_BUDGET)


def blocks(text: str) -> tuple[list[str], list[str], str]:
    """(paragraphs, bullets, figure alt text) of a fragment. A bullet's wrapped lines belong to it."""
    paragraphs: list[str] = []
    bullets: list[str] = []
    alt = ""
    current: list[str] = []
    in_bullet = False

    def flush() -> None:
        if current:
            (bullets if in_bullet else paragraphs).append(" ".join(current))
            current.clear()

    in_fence = False
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence or TABLE_ROW.match(stripped):  # code and tables are not slide text; has_skipped_markup() tells the session
            flush()
            continue
        image = IMAGE.match(stripped)
        if not stripped:
            flush()
        elif image:
            flush()
            alt = alt or image.group(1)
        elif stripped.startswith("- ") or ORDERED.match(stripped):
            flush()
            in_bullet = True
            current.append(ORDERED.sub("", stripped) if ORDERED.match(stripped) else stripped[2:])
        elif raw.startswith(" ") and in_bullet and current:
            current.append(stripped)
        else:
            if in_bullet:
                flush()
            in_bullet = False
            current.append(stripped)
    flush()
    return paragraphs, bullets, alt


def has_skipped_markup(text: str) -> bool:
    """Does the fragment hold a code block or a table, which blocks() leaves out of the slide lines?"""
    return any(line.strip().startswith("```") or TABLE_ROW.match(line.strip()) for line in text.splitlines())


def split_opening(paragraph: str) -> tuple[str, str]:
    """The opening paragraph of a lesson is its hook (the bold first sentence) and the situation that follows it."""
    lead = LEAD.match(paragraph.strip())
    if lead and clean(lead.group(1)):
        return clean(lead.group(1)), clean(lead.group(2))
    sentences = SENTENCE_END.split(clean(paragraph), maxsplit=1)
    return sentences[0], (sentences[1] if len(sentences) > 1 else "")


def parse(text: str) -> Parsed:
    """Split a lesson.md into title, introduction, `##` sections and `<details>` blocks."""
    details = [(clean(summary), body.strip()) for summary, body in DETAILS.findall(text)]
    body = DETAILS.sub("\n", text)
    head = re.search(r"^# (.+)$", body, re.M)
    if not head:
        raise BriefError("the lesson has no `# ` title")
    parts = re.split(r"^## ", body[head.end():], flags=re.M)
    paragraphs, bullets, alt = blocks(parts[0])
    sections = {}
    for part in parts[1:]:
        name, _, rest = part.partition("\n")
        sections[clean(name)] = rest
    return Parsed(clean(head.group(1)), [clean(p) for p in paragraphs], bullets, clean(alt), sections, details,
                  split_opening(paragraphs[0]) if paragraphs else ("", ""))


def section(parsed: Parsed, prefix: str) -> str | None:
    return next((rest for name, rest in parsed.sections.items() if name.startswith(prefix)), None)


def split_concept(raw: str) -> tuple[str, str, bool]:
    lead = LEAD.match(raw.strip())
    if lead and clean(lead.group(1)).rstrip(":. "):
        return clean(lead.group(1)).rstrip(":. "), clean(lead.group(2)), False
    cleaned = clean(raw)
    return " ".join(cleaned.split()[:3]), cleaned, True


def group_sizes(count: int, slots: int) -> list[int]:
    """Contiguous groups as even as possible, the larger ones first: 6 concepts in 4 slots -> 2, 2, 1, 1."""
    base, extra = divmod(count, slots)
    return [base + (1 if index < extra else 0) for index in range(slots)]


def number_or_none(value: str | None) -> float | None:
    try:
        return float(str(value).rstrip("px"))
    except ValueError:
        return None


def wraps(last: tuple, line: tuple) -> bool:
    """Is `line` the next line of the heading whose last line is `last`? Each is (font size, x, y). A wrapped heading
    keeps its size and left edge and sits one line below; a group heading above the first card, or a badge number
    beside a heading, differs in size or position. Without positions the lines are taken to belong together."""
    (last_size, last_x, last_y), (size, x, y) = last, line
    if None in (last_x, last_y, x, y):
        return True
    return size == last_size and abs(x - last_x) < 1 and 0 < y - last_y <= size * 2


def figure_cards(svg: pathlib.Path) -> list[tuple[str, str, bool]]:
    """The text cards of a lesson's figure: a bold heading (it may wrap over lines) followed by its plain lines.

    The figure is the lesson for the lessons that keep their concepts out of the prose. Its biggest bold text is the
    figure's own title and the plain text before the first card is its subtitle, so both are skipped.
    """
    try:
        root = ET.parse(svg).getroot()
    except (OSError, ET.ParseError):
        return []
    items: list[tuple[bool, float, str, tuple]] = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "text":
            continue
        text = ADDRESS.sub(ADDRESS_TOKEN, " ".join("".join(element.itertext()).split()))
        style = element.get("style", "")
        weight = element.get("font-weight") or (re.search(r"font-weight:\s*(\w+)", style) or [None, ""])[1]
        size = element.get("font-size") or (re.search(r"font-size:\s*([\d.]+)", style) or [None, "0"])[1]
        try:
            number = float(str(size).rstrip("px"))
        except ValueError:
            number = 0.0
        if text:
            items.append((weight in BOLD_WEIGHTS, number, text, (number, number_or_none(element.get("x")),
                                                                  number_or_none(element.get("y")))))
    bold_sizes = {size for bold, size, _, _ in items if bold}
    title_size = max(bold_sizes) if len(bold_sizes) > 1 else None
    # Weight alone cannot tell a card's heading from a bold line inside the card (a callout). When the headings are
    # numbered, only a numbered bold line opens a card; any other bold line is a line of the card it is in.
    numbered = sum(1 for bold, _, text, _ in items if bold and ORDINAL.match(text)) >= CONCEPT_SLIDES.start
    cards: list[list] = []
    seen_card = title_size is None
    for bold, size, text, geometry in items:
        if not seen_card:
            seen_card = bold and size < title_size
            if not seen_card:
                continue
        opens = bold and (not numbered or bool(ORDINAL.match(text)))
        if bold and cards and not cards[-1][1] and not (numbered and opens) and wraps(cards[-1][2], geometry):
            cards[-1][0].append(text)  # a heading wrapped over lines
            cards[-1][2] = geometry
        elif opens:
            cards.append([[text], [], geometry])
        elif cards:
            cards[-1][1].append(text)
    return [(" ".join(heading).rstrip(":. "), " ".join(body), False) for heading, body, _ in cards if body]


def concept_source(parsed: Parsed, figure: str | None, svg: pathlib.Path) -> tuple[str, list[tuple[str, str, bool]], list[str]]:
    """Where the lesson keeps its concepts: (source, [(label, line, label_derived)], plain lines of the figure section).

    Lessons differ: 30 list them as bullets under `## Đọc hình`, 42 as paragraphs opening with a bold label there,
    a few as bullets before the first `##`, and the rest only in the figure.
    """
    paragraphs, bullets, _ = blocks(figure) if figure is not None else ([], [], "")
    lead = [p for p in paragraphs if BOLD_LEAD.match(p)]
    plain = [clean(p) for p in paragraphs if not BOLD_LEAD.match(p)]
    if bullets:
        return "bullets under `Đọc hình`", [split_concept(raw) for raw in bullets], plain
    if len(lead) >= CONCEPT_SLIDES.start:
        return "bold-label paragraphs under `Đọc hình`", [split_concept(raw) for raw in lead], plain
    if parsed.intro_bullets:
        return "bullets before the first section", [split_concept(raw) for raw in parsed.intro_bullets], plain
    cards = figure_cards(svg)
    if cards:
        return "text cards of the figure (the lesson's SVG)", cards, plain
    return "nowhere", [], plain


def terms(text: str | None) -> list[dict]:
    result = []
    for raw in blocks(text or "")[1]:
        match = TERM.match(raw.strip())
        if match:
            meaning = clean(match.group(3))
            short = re.split(r"[:;]", meaning, maxsplit=1)[0].strip()
            result.append({"abbreviation": clean(match.group(1)), "spelled_out": clean(match.group(2)),
                           "short_meaning": short, "words": len(short.split()), "over_budget": len(short.split()) > WORD_BUDGET,
                           "meaning": meaning})
    return result


def sources(text: str | None) -> list[str]:
    """The name of every source the section lists: each link label of each bullet (a bullet may hold several)."""
    names: list[str] = []
    for raw in blocks(text or "")[1]:
        labels = [label for label in (clean(label) for label in LINK.findall(raw)) if label]
        if not labels:  # a source named in words only: its text up to the first colon, when that is short enough
            head = clean(raw).split(":", 1)[0].strip()
            words = head.split()
            labels = [" ".join(words[:SOURCE_NAME_WORDS]) + (" …" if len(words) > SOURCE_NAME_WORDS else "")] if words else []
        names += labels
    return names


def backgrounds(count: int) -> list[str]:
    """Cover and closing are dark and the middle alternates from cream. An odd count alternates all the way; an even
    count has to repeat one background once, which is put just before the closing slide."""
    result = ["dark"] + ["cream" if index % 2 == 0 else "dark" for index in range(count - 2)] + ["dark"]
    if count > 2 and result[-2] == "dark":
        result[-2] = "cream"
    return result


def build(store: pathlib.Path, lesson_id: str) -> Brief:
    match = LESSON_ID.fullmatch(lesson_id)
    if not match:
        raise BriefError(f"{lesson_id!r} is not a lesson id like sd-01-027")
    path = store / "lessons" / lesson_id / "lesson.md"
    try:
        parsed = parse(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise BriefError(f"cannot read {path}: {error.strerror or error}") from error
    except UnicodeDecodeError as error:
        raise BriefError(f"cannot read {path}: not valid UTF-8 ({error.reason} at byte {error.start})") from error
    warnings: list[str] = []
    number = f"{int(match.group(2)):02d}"
    title = parsed.title  # the lesson's own H1, as README.md and the decks already built name it

    figure = section(parsed, FIGURE_SECTION)
    source, raw_concepts, figure_plain = concept_source(parsed, figure, store / "diagrams" / f"{lesson_id}-main.svg")
    if len(raw_concepts) < CONCEPT_SLIDES.start:
        warnings.append(f"only {len(raw_concepts)} concept line(s) found ({source}); the deck needs at least "
                        f"{CONCEPT_SLIDES.start} concept slides, so split the figure's description by hand")
    slots = min(max(len(raw_concepts), CONCEPT_SLIDES.start), CONCEPT_SLIDES.stop - 1)
    sizes = group_sizes(len(raw_concepts), slots)
    colours = [{"concept_slide": index + 1, "name": name, "on_cream": cream, "on_dark": dark}
               for index, (name, cream, dark) in enumerate(CONCEPT_COLOURS[:slots])]

    concept_slides: list[list[Concept]] = []
    cursor = 0
    for index, size in enumerate(sizes):
        concept_slides.append([Concept(label, text, derived, CONCEPT_COLOURS[index][0])
                               for label, text, derived in raw_concepts[cursor:cursor + size]])
        cursor += size

    count = FIXED_SLIDES + slots
    hook, opening_rest = parsed.opening
    if not hook:
        warnings.append("the lesson has no opening line for the cover's hook")
    from_cards = source.startswith("text cards")
    # When the concepts come from the figure's cards, the prose under `Đọc hình` is those same concepts explained: it is
    # not a situation line, and dumping it on slide 2 would repeat the concept slides.
    situation = [text for text in ([opening_rest] if opening_rest else []) + parsed.intro[1:]
                 + ([] if from_cards else figure_plain) if text and text != ADDRESS_TOKEN]
    if not situation and parsed.alt:
        # nothing follows the hook: the description of the figure (at most three sentences) is the situation
        situation = SENTENCE_END.split(parsed.alt)[:3]
        warnings.append("the lesson says nothing after its opening line, so the situation slide starts from the "
                        "figure's description")
    if from_cards and figure_plain:
        warnings.append(f"the {sum(len(text.split()) for text in figure_plain)} words of prose under `{FIGURE_SECTION}` "
                        "explain the figure's cards and are left off the situation slide; read them in lesson.md")

    question_section = section(parsed, QUESTION_SECTION)
    question = [clean(p) for p in blocks(question_section or "")[0]]
    answer = next((body for summary, body in parsed.details if ANSWER_SUMMARY in summary.lower()), "")
    deep = next((body for summary, body in parsed.details if ANSWER_SUMMARY not in summary.lower()), "")
    if not question or not answer:
        warnings.append("the lesson lacks a check question or its answer")
    known = (GLOSSARY_SECTION, FIGURE_SECTION, QUESTION_SECTION, SOURCES_SECTION)
    takeaways = [(name, [clean(p) for p in blocks(rest)[0]] + [clean(b) for b in blocks(rest)[1]])
                 for name, rest in parsed.sections.items() if name.startswith(TAKEAWAY_PREFIXES)]
    body_sections = [name for name in parsed.sections if not name.startswith(known + TAKEAWAY_PREFIXES)]
    if body_sections:
        warnings.append("sections of the lesson's body are not on the summary slide (read them in lesson.md): "
                        + "; ".join(body_sections))
    if not takeaways:
        # no `##` section of limits or takeaways: the summary recaps the lesson's own concept labels
        takeaways = [("recap of the concepts", [c.label for group in concept_slides for c in group])]
        warnings.append("the lesson has no limits/takeaway section: the summary slide only recaps the concepts; add what "
                        "the lesson says about limits from its figure and opening line")
    fed = [figure or "", question_section or "", answer, deep] + [
        parsed.sections[name] for name in parsed.sections if name.startswith(TAKEAWAY_PREFIXES)]
    if any(has_skipped_markup(text) for text in fed):
        warnings.append("a code block or table in the lesson is left out of the slide lines (read it in lesson.md and "
                        "draw it as a diagram if the slide needs it)")
    glossary = terms(section(parsed, GLOSSARY_SECTION))
    names = sources(section(parsed, SOURCES_SECTION))
    if not names:
        warnings.append("the lesson lists no sources")

    footer = "System Design 101 · Bài {} · {:02d}/{:02d}"
    backdrops = backgrounds(count)
    layouts = [LAYOUTS[(int(match.group(2)) + offset) % len(LAYOUTS)] for offset in range(count)]
    slides = [Slide(1, "cover", backdrops[0], "concept hub", "(no footer on the cover)", {
        "title": line(parsed.title, budget=False).__dict__, "hook": line(hook).__dict__,
        **({"question_candidate": line(question[0]).__dict__} if question else {}),
        "one_line_per_concept": [line(" / ".join(c.label for c in group)).__dict__ for group in concept_slides]})]
    slides.append(Slide(2, "situation and goal", backdrops[1], layouts[1], footer.format(number, 2, count), {
        "lines": [line(text).__dict__ for text in situation]}))
    for index, group in enumerate(concept_slides):
        position = 3 + index
        slides.append(Slide(position, f"concept {index + 1} of {slots}", backdrops[position - 1], layouts[position - 1],
                            footer.format(number, position, count), {
                                "colour": CONCEPT_COLOURS[index][0],
                                "concepts": [{"label": c.label, "label_derived": c.label_derived,
                                              "line": line(c.text).__dict__} for c in group]}))
    position = 3 + slots
    slides.append(Slide(position, "choice or summary", backdrops[position - 1], layouts[position - 1],
                        footer.format(number, position, count), {
                            "sections": [{"name": name, "lines": [line(text).__dict__ for text in texts]}
                                         for name, texts in takeaways]}))
    position += 1
    slides.append(Slide(position, "check question and answer", backdrops[position - 1], layouts[position - 1],
                        footer.format(number, position, count), {
                            "question": [line(text).__dict__ for text in question],
                            "answer": [line(clean(text)).__dict__ for text in blocks(answer)[0] + blocks(answer)[1]]}))
    position += 1
    slides.append(Slide(position, "deep dive", backdrops[position - 1], layouts[position - 1],
                        footer.format(number, position, count), {
                            "lines": [line(clean(text)).__dict__ for text in blocks(deep)[1] + blocks(deep)[0]]}))
    slides.append(Slide(count, "terms and sources", backdrops[count - 1], "two columns",
                        footer.format(number, count, count), {
                            "terms": glossary, "sources": names}))
    deck = [dataclasses.asdict(slide) for slide in slides]
    if ADDRESS_TOKEN in json.dumps([deck, parsed.alt], ensure_ascii=False):
        warnings.append(f"the lesson types an address; it shows as {ADDRESS_TOKEN} below. Draw such an example as its "
                        "parts (scheme, host, path ...) or by a label, never as one typed address")
    return Brief(lesson_id, number, title, f"System Design 101 · Bài {number} · {title} ({lesson_id})", count,
                 parsed.alt, source, colours, deck, warnings)


def escape_markup(text: str) -> str:
    """Lesson text with a tag-shaped `<p class="note">` in it is shown as text by a Markdown reader, not read as a tag."""
    return text.replace("<", "\\<")


def render(brief: Brief) -> str:
    def show(item: dict) -> str:
        flag = f"  [{item['words']} words: cut to {WORD_BUDGET} or fewer]" if item["over_budget"] else ""
        return f"{escape_markup(item['text'])}{flag}"

    out = [f"# Deck brief: {brief.lesson}", "",
           f"- Canvas name: `{brief.canvas_name}`",
           f"- Slides: {brief.slide_count} (the checker allows {SLIDE_COUNTS.start} to {SLIDE_COUNTS.stop - 1}); "
           f"canvas 1920x1080, category `slides`, no brand kit",
           f"- Figure of the lesson (use it to plan the diagrams): {escape_markup(brief.figure_alt) or '(none)'}",
           f"- Concepts are taken from: {brief.concept_source}",
           *([f"- The figure's own line breaks are lost in the card text below; open `diagrams/{brief.lesson}-main.svg` "
              "to read the sentences as they are"] if "figure" in brief.concept_source else []),
           "- Concept colours (same on every slide of the deck): " + ", ".join(
               f"concept slide {c['concept_slide']} {c['name']} {c['on_cream']} (on dark {c['on_dark']})"
               for c in brief.colours),
           f"- Budget: at most {WORD_BUDGET} words per bullet and 3 bullets per card; every line below is copied from "
           "`lesson.md`, so condense it, never add to it."]
    for warning in brief.warnings:
        out.append(f"- WARNING: {warning}")
    for slide in brief.slides:
        out += ["", f"## Slide {slide['number']} of {brief.slide_count}: {slide['role']}",
                f"background {slide['background']}, layout idea: {slide['layout']}, footer: {slide['footer']}"]
        material = slide["material"]
        for key, value in material.items():
            if isinstance(value, dict) and "text" in value:
                out.append(f"- {key}: {show(value)}")
            elif isinstance(value, str):
                out.append(f"- {key}: {value}")
            elif key == "concepts":
                for concept in value:
                    mark = " (label made from the first words: choose a better one)" if concept["label_derived"] else ""
                    out.append(f"- concept `{concept['label']}`{mark}: {show(concept['line'])}")
            elif key == "sections":
                for sec in value:
                    out.append(f"- section `{sec['name']}`:")
                    out += [f"  - {show(item)}" for item in sec["lines"]]
            elif key == "terms":
                out.append(f"- terms ({len(value)}):" if value else "- terms: (none)")
                out += [f"  - {t['abbreviation']} = {show({'text': t['short_meaning'], 'words': t['words'], 'over_budget': t['over_budget']})}"
                        for t in value]
            elif key == "sources":
                out.append("- sources, by name and never as an address: " + escape_markup("; ".join(value))
                           if value else "- sources: (none)")
            else:
                out.append(f"- {key}:")
                out += [f"  - {show(item)}" for item in value]
    out += ["", "## Before `finish`", "",
            "- every line fits the budget and nothing was added to what the lesson says;",
            "- nothing on a slide is smaller than 22 px and the bottom right corner is clear;",
            "- every slide but the cover has its footer text and one progress dot per slide, the current one red;",
            "- `canvas_screenshot` of every slide shows no cut-off or shrunk text.", ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the brief to build a lesson's Moda deck from.")
    parser.add_argument("lessons", nargs="+", metavar="ID", help="lesson ids such as sd-01-027")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--store", type=pathlib.Path, default=DEFAULT_STORE, help="the lesson store (default: %(default)s)")
    args = parser.parse_args(argv)
    briefs = []
    for lesson_id in args.lessons:
        try:
            briefs.append(build(args.store, lesson_id))
        except BriefError as error:
            print(f"sd101_slide_brief: {lesson_id}: {error}", file=sys.stderr)
            return 1
    if args.json:
        print(json.dumps([dataclasses.asdict(brief) for brief in briefs], ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(render(brief) for brief in briefs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
