#!/usr/bin/env python3
"""Prove that a lesson post carries every idea of the lesson it was made from.

A course lesson (vohoailinh90/Agentic-coding-course, course/<lang>/lessons/<id>.md)
is split into atomic blocks: every paragraph, list item (nested items too),
table row, quote, sub-heading, code block and diagram inside its `section:`
markers. A coverage manifest maps each block to the place in the post that
carries it -- a slide or the caption -- and quotes the words it shows there.
"Did the post keep the lesson?" then becomes computable (see *Deterministic work
is not agent work* in CLAUDE.md):

  - every block of the lesson appears in the manifest exactly once, with the
    lesson's own text (so a block cannot be dropped or quietly reworded) --
    checked against the lesson itself at the commit the manifest pins;
  - every block names a slide that exists, or the caption -- never the first
    comment, which readers can miss, and never the link;
  - every block's `evidence` -- one quote or a list of quotes -- is found word
    for word in one text field the slide's layout actually draws (or in the
    caption); the distinct words the quotes cover, with no word counted twice
    and none shared with another block, show at least 30% of the block's
    words, so three words cannot stand in for a paragraph; a code block must
    appear whole and exactly (only whitespace may differ);
  - the manifest is bound to its lesson and its post: coverage/<id>.yaml
    checks posts/<lang>/<id>.yaml against course/<lang>/lessons/<id>.md;
  - the lesson's `social.hook` and `social.question` count as blocks too;
  - a diagram block points at the image slide showing that diagram -- or, when
    the picture is too small to read on a phone, at a slide or the caption that
    rebuilds it in the studio's own layouts: its evidence then quotes the
    diagram's own labels (read from the SVG at the pinned commit) and must
    show at least 60% of the diagram's words; an image slide always has to
    show that diagram's own picture;
  - the post has at most 10 slides, and every post of a course campaign has a
    manifest.

Whether a paraphrase is faithful stays a human judgement; this script only
makes sure nothing is missing and every claim of coverage is visible.

    python3 scripts/lesson_coverage.py extract LESSON.md --lesson ID --commit SHA > coverage.yaml
    python3 scripts/lesson_coverage.py check FILE... --course-dir PATH/TO/Agentic-coding-course
    python3 scripts/lesson_coverage.py check --all --course-dir PATH   # every course campaign (CI)

`extract` prints a manifest skeleton (every block, `dest` and `evidence` empty)
for the author to fill. `check` validates manifests against their posts and,
with `--course-dir`, re-extracts each lesson from that clone at the pinned
commit (`git show COMMIT:PATH`). Without `--course-dir` the blocks a manifest
lists are taken on trust, which is only good for a quick local look: CI always
passes it.

Exit status: 0 every manifest passes, 1 a manifest fails, 2 bad input.
"""

from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only where PyYAML is absent
    print("PyYAML is required. Install it with: python -m pip install -r requirements.txt", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
# Campaigns made from course lessons: every post in them must have a manifest.
COURSE_CAMPAIGNS = ("agentic-coding-course",)
MAX_SLIDES = 10
# The quotes for a block must show at least this share of its words, and at
# least MIN_EVIDENCE_WORDS (or the whole block when it is shorter): three words
# cannot stand in for a paragraph. A code block is compared exactly instead.
MIN_EVIDENCE_SHARE = 0.3
MIN_EVIDENCE_WORDS = 3
# A diagram rebuilt in the post's own layouts (its picture is too small to read on a
# phone) must show at least this share of the diagram's words: the labels are the
# knowledge, and a rebuild keeps most of them. Not all: a diagram has 75 words on average, and
# the lesson's prose, which each carry their own blocks, repeats much of what it says.
MIN_DIAGRAM_SHARE = 0.6
# Front-matter fields of a lesson that a post must carry too.
SOCIAL_FIELDS = ("hook", "question")

SECTION = re.compile(r"^<!--\s*section:\s*([a-z0-9-]+)\s*-->\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{2,6})\s+(.*)$")
IMAGE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)\s*$")
LIST_ITEM = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
QUOTE = re.compile(r"^\s*>\s?(.*)$")
RULE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
# A line made only of tags (<details>, </details>, <summary>…</summary>) is
# layout; a line that merely starts with a tag (<kbd>Ctrl</kbd> + C …) is text.
TAG = r"</?[a-zA-Z][^>]*>"
HTML_ONLY = re.compile(rf"^\s*(?:{TAG}\s*)+$|^\s*<summary>.*</summary>\s*$")
LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
EMPHASIS = re.compile(r"(\*\*|__|\*|_|`)")
WORD = re.compile(r"\w+")
DEST = re.compile(r"^(?:slide:(\d+)|caption)$")


class InputError(Exception):
    """A file cannot be read or does not have the expected shape."""


def plain(text: str) -> str:
    """Text without Markdown links, emphasis or inline tags, keeping its case and single spacing."""
    text = re.sub(TAG, "", LINK.sub(r"\1", text))
    return " ".join(EMPHASIS.sub("", text).split())


def normalize(text: str) -> str:
    """Text as a reader sees it, case-folded, for matching quotes."""
    return plain(text).casefold()


def tokens(text: str) -> list[str]:
    return WORD.findall(normalize(text))


def words(text: str) -> int:
    return len(tokens(text))


def split_front_matter(markdown: str) -> tuple[dict, list[str]]:
    """The lesson's front matter (parsed) and its lines after it."""
    lines = markdown.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                try:
                    front = yaml.safe_load("\n".join(lines[1:index])) or {}
                except yaml.YAMLError as exc:
                    raise InputError(f"front matter is not valid YAML: {exc}") from exc
                return (front if isinstance(front, dict) else {}), lines[index + 1:]
        raise InputError("front matter is not closed")
    return {}, lines


def extract(markdown: str) -> list[dict[str, str]]:
    """Every atomic block inside the lesson's sections, in order.

    A block is a paragraph, a list item (a nested item is a block of its own;
    an indented plain line continues the item above it), a table row (the rule
    row is not), a quote (its lines joined, the `>` dropped), a sub-heading, a
    code block (its lines without the fences) or a diagram. A section's own `##`
    heading is its label, horizontal rules and tag-only lines are layout, and
    lines before the first section (title, language bar) are not blocks. The
    front matter's `social.hook` and `social.question` come first, as blocks
    of the pseudo-section `social`.
    """
    blocks: list[dict[str, str]] = []
    section: str | None = None
    counters: dict[str, int] = {}
    pending: list[str] = []
    pending_kind = ""

    def add(kind: str, text: str) -> None:
        assert section is not None
        counters[section] = counters.get(section, 0) + 1
        blocks.append({"key": f"{section}#{counters[section]:02d}", "kind": kind, "source": text})

    def flush() -> None:
        nonlocal pending, pending_kind
        if pending and section is not None:
            text = "\n".join(pending) if pending_kind == "code" else plain(" ".join(pending))
            if text.strip():
                add(pending_kind, text)
        pending, pending_kind = [], ""

    front, lines = split_front_matter(markdown)
    social = front.get("social") if isinstance(front.get("social"), dict) else {}
    for field in SOCIAL_FIELDS:
        if social.get(field):
            section = "social"
            add(field, plain(str(social[field])))
    section = None
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        marker = SECTION.match(line.strip())
        if marker:
            flush()
            section = marker.group(1)
            continue
        if section is None:
            continue
        if FENCE.match(line):
            flush()
            code: list[str] = []
            while index < len(lines) and not FENCE.match(lines[index]):
                code.append(lines[index])
                index += 1
            if index >= len(lines):
                raise InputError(f"a code fence opened in section {section!r} is never closed")
            index += 1  # the closing fence
            pending, pending_kind = code, "code"
            flush()
            continue
        stripped = line.strip()
        if not stripped or RULE.match(stripped) or HTML_ONLY.match(stripped):
            flush()
            continue
        heading = HEADING.match(stripped)
        if heading:
            flush()
            if len(heading.group(1)) > 2:
                add("heading", plain(heading.group(2)))
            continue
        image = IMAGE.match(stripped)
        if image:
            flush()
            add("diagram", Path(image.group(1)).stem)
            continue
        if TABLE_ROW.match(line):
            flush()
            if not TABLE_RULE.match(stripped):
                cells = [plain(c) for c in stripped.strip("|").split("|")]
                add("row", " · ".join(c for c in cells if c))
            continue
        quote = QUOTE.match(line)
        if quote:
            if pending_kind != "quote":
                flush()
                pending_kind = "quote"
            pending.append(quote.group(1))
            continue
        item = LIST_ITEM.match(line)
        if item:
            flush()
            pending, pending_kind = [item.group(2)], "item"
            continue
        if pending_kind == "item" and line.startswith((" ", "\t")):
            pending.append(stripped)
            continue
        if pending_kind != "para":
            flush()
            pending_kind = "para"
        pending.append(stripped)
    flush()
    return blocks


def _texts(value: Any) -> list[str]:
    """Strings a list field shows: plain strings, or the `text` of {text: ...} entries."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [str(value["text"])] if value.get("text") else []
    if isinstance(value, list):
        return [t for v in value for t in _texts(v)]
    return []


def rendered(slide: Any) -> list[str]:
    """The text fields a slide's layout draws, one string per field -- mirrors mkt/layouts.py.

    Fields a layout ignores (a stat's `value` beside before/after, a quote's
    `role` without an author, unknown keys) are not text a reader sees, so they
    cannot carry evidence.
    """
    if not isinstance(slide, dict):
        return []
    s = slide
    get = lambda *keys: [str(s[k]) for k in keys if s.get(k)]  # noqa: E731
    layout = s.get("layout")
    head = get("eyebrow", "title")
    note = get("note")
    if layout == "cover":
        return get("eyebrow", "title", "subtitle", "badge")
    if layout in ("pains", "checklist"):
        return head + _texts(s.get("items")) + note
    if layout == "chat":
        messages = [m for m in s.get("messages") or [] if isinstance(m, dict)]
        return (head + get("group") + [str(m["from"]) for m in messages if m.get("from") and not m.get("me")]
                + [str(m["text"]) for m in messages if m.get("text")] + note)
    if layout == "flow":
        steps = [t for t in s.get("steps") or [] if isinstance(t, dict)]
        total = sum(int(t["minutes"]) for t in steps if isinstance(t.get("minutes"), int))
        return head + _texts(steps) + (get("total_label") if total else []) + note
    if layout == "stat":
        figure = get("before", "after") if s.get("before") and s.get("after") else get("value")
        return get("eyebrow") + figure + get("label", "caption")
    if layout == "compare":
        sides = [s.get(side) for side in ("before", "after")]
        return head + [t for side in sides if isinstance(side, dict)
                       for t in (([str(side["label"])] if side.get("label") else []) + _texts(side.get("items")))] + note
    if layout == "table":
        return head + _texts(s.get("columns")) + [t for row in s.get("rows") or [] for t in _texts(row)] + note
    if layout == "features":
        items = [i for i in s.get("items") or [] if isinstance(i, dict)]
        return head + [str(i[k]) for i in items for k in ("title", "text") if i.get(k)] + note
    if layout == "quote":
        return get("text") + (get("author", "role") if s.get("author") else [])
    if layout == "poll":
        return get("eyebrow", "question") + _texts(s.get("options")) + get("hint")
    if layout == "cta":
        # `hint` or `scan` shows depending on whether the post has a link (QR code); neither is counted.
        return head + get("text", "button", "keyword")
    if layout == "email":
        return head + get("subject", "from", "infobar") + _texts(s.get("buttons")) + get("body") + note
    if layout == "timeline":
        items = [i for i in s.get("items") or [] if isinstance(i, dict)]
        return head + [str(i[k]) for i in items for k in ("when", "text") if i.get(k)] + note
    if layout == "image":
        return head + get("caption") + note
    return []


def find_span(quote: list[str], field: list[str], taken: set[int]) -> range | None:
    """Where `quote` (as words) first appears in `field` without touching words already taken."""
    n = len(quote)
    for start in range(len(field) - n + 1):
        if field[start:start + n] == quote and not taken.intersection(range(start, start + n)):
            return range(start, start + n)
    for start in range(len(field) - n + 1):
        if field[start:start + n] == quote:
            return range(start, start + n)
    return None


def find_label_span(quote: list[str], labels: list[list[str]],
                    covered: set[tuple[int, int]]) -> set[tuple[int, int]] | None:
    """Where `quote` (as words) appears inside one diagram label, as (label, word) positions.

    An occurrence none of whose words an earlier quote covered comes first, so
    two quotes of one phrase that the diagram says twice cover both places.
    """
    n = len(quote)
    first = None
    for number, label in enumerate(labels):
        for start in range(len(label) - n + 1):
            if label[start:start + n] == quote:
                span = {(number, i) for i in range(start, start + n)}
                if not span & covered:
                    return span
                first = first or span
    return first


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


def file_from_git(course_dir: Path, commit: str, path: str) -> str:
    result = subprocess.run(["git", "-C", str(course_dir), "show", f"{commit}:{path}"],
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise InputError(f"cannot read {path} at {commit} in {course_dir}: {result.stderr.strip()}")
    return result.stdout


def diagram_labels(svg: str) -> list[str]:
    """The labels a diagram shows: each <text> element as one string, in document order.

    A text with no letter (a step badge, a plus or equals sign, an emoji) is
    layout, not wording. The SVG comes from the pinned commit of the course.
    """
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        raise InputError(f"a diagram is not valid SVG: {exc}") from exc
    labels = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "text":
            continue
        label = " ".join(" ".join(element.itertext()).split())
        if re.search(r"[^\W\d_]", label):
            labels.append(label)
    return labels


def required_words(kind: str, source: str) -> int:
    total = words(source)
    return min(total, max(MIN_EVIDENCE_WORDS, math.ceil(total * MIN_EVIDENCE_SHARE)))


def check(manifest_path: Path, course_dir: Path | None = None) -> list[str]:
    """Every problem with one manifest; an empty list means it passes."""
    manifest = load_yaml(manifest_path)
    if not isinstance(manifest, dict):
        raise InputError(f"{manifest_path}: not a mapping")
    problems: list[str] = []
    source = manifest.get("source") or {}
    for field in ("repo", "commit", "path"):
        if not source.get(field):
            problems.append(f"source.{field} is missing")
    if source.get("commit") and not re.fullmatch(r"[0-9a-f]{40}", str(source["commit"])):
        problems.append("source.commit must be a full 40-character commit SHA")

    # A manifest is bound to its lesson and its post by its own file name: it
    # cannot point at a shorter lesson or at another, complete post.
    lesson_id = manifest_path.stem
    lang = str(manifest.get("lang") or "")
    if manifest.get("lesson") != lesson_id:
        problems.append(f"lesson must be {lesson_id!r}, the manifest's file name")
    if not re.fullmatch(r"[a-z]{2}", lang):
        raise InputError(f"{manifest_path}: `lang` must be a two-letter language code")
    expected_path = f"course/{lang}/lessons/{lesson_id}.md"
    if source.get("path") and source["path"] != expected_path:
        problems.append(f"source.path must be {expected_path}")
    post_path = (manifest_path.parent.parent / "posts" / lang / f"{lesson_id}.yaml").resolve()
    if manifest.get("post") and (manifest_path.parent / str(manifest["post"])).resolve() != post_path:
        problems.append(f"post must be ../posts/{lang}/{lesson_id}.yaml")
    post = load_yaml(post_path)
    if not isinstance(post, dict):
        raise InputError(f"{post_path}: not a mapping")
    slides = post.get("slides") or []
    if len(slides) > MAX_SLIDES:
        problems.append(f"the post has {len(slides)} slides; at most {MAX_SLIDES}")
    caption = ((post.get("platforms") or {}).get("facebook") or {}).get("caption") or ""

    blocks = manifest.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        problems.append("`blocks` is empty")
        blocks = []

    # The lesson itself decides which blocks exist and what they say.
    truth: dict[str, dict[str, str]] | None = None
    if course_dir is not None and source.get("commit"):
        try:
            truth = {b["key"]: b for b in extract(file_from_git(course_dir, str(source["commit"]),
                                                                expected_path))}
        except InputError as exc:
            problems.append(str(exc))

    seen: set[str] = set()
    # Words already claimed, per destination field and claim space ("block" for the lesson's prose,
    # "diagram" for rebuilt diagrams): (dest, field index, space) -> word index -> block key.
    claimed: dict[tuple[str, int], dict[int, str]] = {}
    for entry in blocks:
        if not isinstance(entry, dict) or not entry.get("key"):
            problems.append(f"a block has no key: {entry!r}")
            continue
        key = str(entry["key"])
        if key in seen:
            problems.append(f"{key}: listed twice")
        seen.add(key)
        block = {"kind": str(entry.get("kind") or ""), "source": str(entry.get("source") or "")}
        if truth is not None:
            real = truth.get(key)
            if real is None:
                problems.append(f"{key}: not a block of the lesson")
                continue
            if real["kind"] != block["kind"] or real["source"] != block["source"]:
                problems.append(f"{key}: kind or source text differs from the lesson")
            block = real
        dest = str(entry.get("dest") or "")
        match = DEST.match(dest)
        if not match:
            problems.append(f"{key}: dest must be slide:N or caption, not {dest!r}"
                            + (" (the first comment can be missed; carry knowledge in the caption)"
                               if "comment" in dest else ""))
            continue
        if match.group(1):
            number = int(match.group(1))
            dest = f"slide:{number}"  # slide:01 and slide:1 are one slide
            if not 1 <= number <= len(slides):
                problems.append(f"{key}: {dest} does not exist (the post has {len(slides)} slides)")
                continue
            target = slides[number - 1]
        else:
            target = caption
        evidence = entry.get("evidence")
        quotes = [str(q) for q in (evidence if isinstance(evidence, list) else [evidence]) if q]
        # What a block must show: its own words, except a rebuilt diagram, which must show
        # the diagram's labels (and keeps its claims apart from the lesson's prose blocks).
        space, block_words, need = "block", words(block["source"]), None
        label_words: list[list[str]] | None = None  # a rebuilt diagram's labels, as words
        covered: set[tuple[int, int]] = set()  # label words some quote has shown
        if block["kind"] == "diagram":
            if isinstance(target, dict) and target.get("layout") == "image":
                # An image slide must show this diagram's own picture; a rebuild uses a text layout or the caption.
                if Path(str(target.get("src", ""))).stem != block["source"]:
                    problems.append(f"{key}: diagram {block['source']!r} is not the image on {dest}")
                continue
            space = "diagram"
            if course_dir is not None and source.get("commit"):
                try:
                    labels = diagram_labels(file_from_git(course_dir, str(source["commit"]),
                                                          f"course/{lang}/diagrams/{block['source']}.svg"))
                except InputError as exc:
                    problems.append(f"{key}: {exc}")
                    continue
                label_words = [tokens(label) for label in labels]
                block_words = sum(len(label) for label in label_words)
                if not block_words:
                    problems.append(f"{key}: diagram {block['source']!r} has no words to rebuild; show the picture")
                    continue
                need = math.ceil(block_words * MIN_DIAGRAM_SHARE)
            else:
                need = MIN_EVIDENCE_WORDS  # without the course the diagram's words are unknown
        texts = rendered(target) if match.group(1) else [caption]
        if block["kind"] == "code":
            # Code is shown whole and exactly: only runs of whitespace may differ.
            code = " ".join(block["source"].split())
            if not code or not any(code in " ".join(text.split()) for text in texts):
                problems.append(f"{key}: the code block is not shown whole and exactly on {dest}")
            continue
        fields = [tokens(text) for text in texts]
        mine: set[tuple[int, int]] = set()
        for quote in quotes:
            words_in_quote = tokens(quote)
            if len(words_in_quote) < min(MIN_EVIDENCE_WORDS, max(block_words, 1)):
                problems.append(f"{key}: quote {quote!r} is too short to prove anything")
                continue
            for number_of_field, field in enumerate(fields):
                owners = claimed.setdefault((dest, number_of_field, space), {})
                span = find_span(words_in_quote, field, {i for i, k in owners.items() if k != key})
                if span is not None:
                    break
            else:
                problems.append(f"{key}: quote {quote!r} is not in one text field {dest} shows")
                continue
            others = {owners[i] for i in span if owners.get(i, key) != key}
            if others:
                problems.append(f"{key}: quote {quote!r} uses words that already prove {', '.join(sorted(others))}")
                continue
            if label_words is not None:
                # A rebuilt diagram is proven by its own wording: the quote must be a phrase of one label.
                label_span = find_label_span(words_in_quote, label_words, covered)
                if label_span is None:
                    problems.append(f"{key}: quote {quote!r} is not wording of the diagram {block['source']!r}")
                    continue
                covered |= label_span
            for i in span:
                owners[i] = key
                mine.add((number_of_field, i))
        # Overlapping quotes count each shown word once. A rebuilt diagram counts the diagram's words the quotes
        # cover, but never more than the words the slide shows: a label the diagram repeats is not credited
        # again for one drawn copy.
        shown = min(len(covered), len(mine)) if label_words is not None else len(mine)
        if need is None:
            need = required_words(block["kind"], block["source"])
        if shown < need:
            problems.append(f"{key}: the quotes show {shown} of the {need} words needed "
                            f"({block_words} in the {'diagram' if space == 'diagram' else 'block'}) on {dest}")

    if truth is not None:
        for key in sorted(set(truth) - seen):
            problems.append(f"{key}: in the lesson but not in the manifest ({truth[key]['source'][:60]!r})")
    return problems


def course_manifests(root: Path) -> tuple[list[Path], list[str]]:
    """Every manifest of the course campaigns, and every post that has none."""
    manifests: list[Path] = []
    missing: list[str] = []
    for name in COURSE_CAMPAIGNS:
        campaign = root / "campaigns" / name
        for post in sorted(campaign.glob("posts/*/*.yaml")):
            manifest = campaign / "coverage" / post.name
            if manifest.is_file():
                manifests.append(manifest)
            else:
                missing.append(f"{post.relative_to(root)}: no coverage manifest at {manifest.relative_to(root)}")
    return manifests, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    ext = sub.add_parser("extract", help="print a manifest skeleton for one lesson")
    ext.add_argument("lesson", type=Path)
    ext.add_argument("--lesson", dest="lesson_id", required=True, help="the lesson id, e.g. agent-parts-and-loop")
    ext.add_argument("--commit", required=True, help="the course commit the lesson was read at (40 hex)")
    ext.add_argument("--lang", default="vi")
    ext.add_argument("--repo", default="vohoailinh90/Agentic-coding-course")
    chk = sub.add_parser("check", help="validate manifests against their posts")
    chk.add_argument("manifests", type=Path, nargs="*")
    chk.add_argument("--all", action="store_true",
                     help=f"every post of the course campaigns ({', '.join(COURSE_CAMPAIGNS)}) and its manifest")
    chk.add_argument("--course-dir", type=Path, help="a clone of the course, to re-extract each lesson")
    chk.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        if args.command == "extract":
            blocks = extract(args.lesson.read_text(encoding="utf-8"))
            skeleton = {
                "lesson": args.lesson_id, "lang": args.lang,
                "source": {"repo": args.repo, "commit": args.commit,
                           "path": f"course/{args.lang}/lessons/{args.lesson_id}.md"},
                "post": f"../posts/{args.lang}/{args.lesson_id}.yaml",
                "blocks": [{**b, "dest": "", "evidence": ""} for b in blocks],
            }
            yaml.safe_dump(skeleton, sys.stdout, allow_unicode=True, sort_keys=False, width=1000)
            return 0
        manifests = list(args.manifests)
        failed = False
        if args.all:
            found, missing = course_manifests(args.root)
            manifests += found
            for problem in missing:
                failed = True
                print(f"FAIL {problem}")
        if not manifests and not args.all:
            parser.error("name a manifest or pass --all")
        if args.course_dir is None:
            print("note: no --course-dir, so the blocks each manifest lists are taken on trust", file=sys.stderr)
        for manifest in manifests:
            problems = check(manifest, args.course_dir)
            if problems:
                failed = True
                print(f"{manifest}: FAIL")
                for problem in problems:
                    print(f"  - {problem}")
            else:
                print(f"{manifest}: ok")
        return 1 if failed else 0
    except (InputError, OSError) as exc:
        print(f"lesson_coverage: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
