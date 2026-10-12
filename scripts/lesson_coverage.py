#!/usr/bin/env python3
"""Prove that a lesson post carries every idea of the lesson it was made from.

A course lesson (vohoailinh90/Agentic-coding-course, course/<lang>/lessons/<id>.md)
is split into atomic blocks: every paragraph, list item, sub-heading, code block
and diagram inside its `section:` markers. A coverage manifest maps each block
to the place in the post that carries it -- a slide or the caption -- and quotes
the words it uses there. "Did the post keep the lesson?" then becomes computable
(see *Deterministic work is not agent work* in CLAUDE.md):

  - every block of the lesson appears in the manifest exactly once, with the
    lesson's own text (so a block cannot be dropped or quietly reworded);
  - every block names a slide that exists, or the caption -- never the first
    comment, which readers can miss, and never the link;
  - every block's `evidence` is found word for word in that slide or caption
    (so a mapping cannot claim coverage the post does not show);
  - a diagram block points at an image slide showing that diagram;
  - the post has at most 10 slides.

Whether a paraphrase is faithful stays a human judgement; this script only
makes sure nothing is missing and every claim of coverage is visible.

    python3 scripts/lesson_coverage.py extract LESSON.md --lesson ID --commit SHA > coverage.yaml
    python3 scripts/lesson_coverage.py check campaigns/<c>/coverage/*.yaml
    python3 scripts/lesson_coverage.py check --all       # every campaigns/*/coverage/*.yaml (CI)
    python3 scripts/lesson_coverage.py check FILE --course-dir PATH/TO/Agentic-coding-course

`extract` prints a manifest skeleton (every block, `dest` and `evidence` empty)
for the author to fill. `check` validates manifests against their posts; with
`--course-dir` it also re-extracts the lesson from that clone at the commit the
manifest names (`git show COMMIT:PATH`) and requires the manifest's blocks to
match it exactly. Without it, the blocks the manifest lists are taken as given.

Exit status: 0 every manifest passes, 1 a manifest fails, 2 bad input.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only where PyYAML is absent
    print("PyYAML is required. Install it with: python -m pip install -r requirements.txt", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
MAX_SLIDES = 10
# Shorter evidence than this many words proves little ("AI", "B"), unless the
# block itself is that short (a quiz option such as "A) LLM").
MIN_EVIDENCE_WORDS = 3

SECTION = re.compile(r"^<!--\s*section:\s*([a-z0-9-]+)\s*-->\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{2,6})\s+(.*)$")
IMAGE = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)\s*$")
LIST_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s+(.*)$")
HTML_ONLY = re.compile(r"^\s*</?[a-zA-Z][^>]*>.*$")
LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
EMPHASIS = re.compile(r"(\*\*|__|\*|_|`)")
DEST = re.compile(r"^(?:slide:(\d+)|caption)$")


class InputError(Exception):
    """A file cannot be read or does not have the expected shape."""


def normalize(text: str) -> str:
    """Text as a reader sees it: no Markdown links or emphasis, one space, case-folded."""
    text = LINK.sub(r"\1", text)
    text = EMPHASIS.sub("", text)
    return " ".join(text.split()).casefold()


def plain(text: str) -> str:
    """Text without Markdown links or emphasis, keeping its case and single spacing."""
    return " ".join(EMPHASIS.sub("", LINK.sub(r"\1", text)).split())


def body_of(markdown: str) -> list[str]:
    """The lesson's lines after its front matter."""
    lines = markdown.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return lines[index + 1:]
        raise InputError("front matter is not closed")
    return lines


def extract(markdown: str) -> list[dict[str, str]]:
    """Every atomic block inside the lesson's sections, in order.

    A block is a paragraph, a list item (with its continuation lines), a
    sub-heading, a code block or a diagram. A section's own `##` heading is its
    label, not content. Lines before the first section (title, language bar)
    and HTML-only lines (`<details>`, `<summary>…</summary>`) are not blocks.
    """
    blocks: list[dict[str, str]] = []
    section = None
    counters: dict[str, int] = {}
    pending: list[str] = []
    pending_kind = ""

    def flush() -> None:
        nonlocal pending, pending_kind
        if pending and section is not None:
            # A code block's text is its lines without the fences.
            if pending_kind == "code":
                inner = pending[1:-1] if len(pending) > 1 and FENCE.match(pending[-1]) else pending[1:]
                text = "\n".join(inner)
            else:
                text = plain(" ".join(pending))
            if text.strip():
                add(pending_kind, text)
        pending, pending_kind = [], ""

    def add(kind: str, text: str) -> None:
        counters[section] = counters.get(section, 0) + 1
        blocks.append({"key": f"{section}#{counters[section]:02d}", "kind": kind, "source": text})

    lines = body_of(markdown)
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
            code = [line]
            while index < len(lines):
                code.append(lines[index])
                index += 1
                if FENCE.match(code[-1]):
                    break
            pending, pending_kind = code, "code"
            flush()
            continue
        stripped = line.strip()
        if not stripped:
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
        if HTML_ONLY.match(stripped):
            flush()
            continue
        item = LIST_ITEM.match(stripped)
        if item and not line.startswith((" ", "\t")):
            flush()
            pending, pending_kind = [item.group(1)], "item"
            continue
        if pending and pending_kind == "item" and line.startswith((" ", "\t")):
            pending.append(stripped)
            continue
        if pending_kind != "para":
            flush()
            pending_kind = "para"
        pending.append(stripped)
    flush()
    return blocks


def strings(value: Any) -> list[str]:
    """Every string inside a slide or a text field, in order."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in strings(v)]
    return []


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


def lesson_from_git(course_dir: Path, commit: str, path: str) -> str:
    result = subprocess.run(["git", "-C", str(course_dir), "show", f"{commit}:{path}"],
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise InputError(f"cannot read {path} at {commit} in {course_dir}: {result.stderr.strip()}")
    return result.stdout


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

    post_rel = manifest.get("post")
    if not post_rel:
        raise InputError(f"{manifest_path}: `post` is missing")
    post_path = (manifest_path.parent / post_rel).resolve()
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

    seen: set[str] = set()
    for entry in blocks:
        if not isinstance(entry, dict) or not entry.get("key"):
            problems.append(f"a block has no key: {entry!r}")
            continue
        key = str(entry["key"])
        if key in seen:
            problems.append(f"{key}: listed twice")
        seen.add(key)
        dest = str(entry.get("dest") or "")
        match = DEST.match(dest)
        if not match:
            problems.append(f"{key}: dest must be slide:N or caption, not {dest!r}"
                            + (" (the first comment can be missed; carry knowledge in the caption)"
                               if "comment" in dest else ""))
            continue
        if match.group(1):
            number = int(match.group(1))
            if not 1 <= number <= len(slides):
                problems.append(f"{key}: {dest} does not exist (the post has {len(slides)} slides)")
                continue
            target = slides[number - 1]
        else:
            target = caption
        if entry.get("kind") == "diagram":
            src = target.get("src", "") if isinstance(target, dict) else ""
            if not (isinstance(target, dict) and target.get("layout") == "image"
                    and Path(str(src)).stem == str(entry.get("source"))):
                problems.append(f"{key}: diagram {entry.get('source')!r} is not the image on {dest}")
            continue
        evidence = normalize(str(entry.get("evidence") or ""))
        source_words = len(normalize(str(entry.get("source") or "")).split())
        if len(evidence.split()) < min(MIN_EVIDENCE_WORDS, max(source_words, 1)):
            problems.append(f"{key}: evidence must quote at least {MIN_EVIDENCE_WORDS} words as they appear on {dest}")
            continue
        haystack = normalize(" ".join(strings(target)))
        if evidence not in haystack:
            problems.append(f"{key}: evidence {entry.get('evidence')!r} is not on {dest}")

    if course_dir is not None and source.get("commit") and source.get("path"):
        try:
            lesson = extract(lesson_from_git(course_dir, str(source.get("commit")), str(source.get("path"))))
        except InputError as exc:
            problems.append(str(exc))
        else:
            listed = {str(e.get("key")): e for e in blocks if isinstance(e, dict)}
            for block in lesson:
                entry = listed.get(block["key"])
                if entry is None:
                    problems.append(f"{block['key']}: in the lesson but not in the manifest ({block['source'][:60]!r})")
                elif entry.get("kind") != block["kind"] or entry.get("source") != block["source"]:
                    problems.append(f"{block['key']}: kind or source text differs from the lesson")
            for key in sorted(set(listed) - {b["key"] for b in lesson}):
                problems.append(f"{key}: not a block of the lesson")
    return problems


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
    chk.add_argument("--all", action="store_true", help="every campaigns/*/coverage/*.yaml in this repository")
    chk.add_argument("--course-dir", type=Path, help="a clone of the course, to re-extract each lesson")
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
        if args.all:
            manifests += sorted((ROOT / "campaigns").glob("*/coverage/*.yaml"))
        if not manifests and not args.all:
            parser.error("name a manifest or pass --all")
        failed = False
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
