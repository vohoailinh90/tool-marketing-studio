#!/usr/bin/env python3
"""Rank the System Design lessons by how closely each follows the source guide it is written from.

The lessons are written independently (see brainstorm/system-design-101-vi/DECISIONS.md, "Giấy phép nguồn"), but
each one maps to exactly one source guide and the curriculum follows the source's order. Whether a lesson only
replays its source's walk, or builds its own argument, is computable up to a point, so it is a script and not a
reviewer's impression (CLAUDE.md, "Deterministic work is not agent work").

The source is English and the lesson Vietnamese, so words cannot be compared. What survives translation is the
vocabulary of names, technical terms and numbers. For each lesson the script takes that vocabulary, in order of
first appearance, from the pinned source body and from the lesson's prose, and reports:

  coverage  share of the source's vocabulary that the lesson also uses
  order     how much of that shared vocabulary the lesson meets in the source's order (longest common subsequence)
  replay    coverage x order: how much of the source's walk the lesson replays
  novelty   share of the lesson's own vocabulary that the source does not have
  closeness replay x (1 - novelty): high means "replays the source and adds little"
  units     list items / bold leads / headings of the source against those of the lesson's reading section
  size      words of the lesson's prose per word of the source
  evidence  independent source hosts cited by the claims (hosts, not repositories: many pages on one host count once),
            and whether any claim, or the claims step, records a run or measurement (a clause that says it was not run
            does not count)

Vocabulary is matched on ASCII words, so a Vietnamese word with marks leaves only short fragments that are dropped; that is noise, not signal.
It is a ranking to point a reader at the lessons worth reading against their source, not a verdict: a lesson that
follows a short source closely can still be fine, and one that scores low can still copy a sentence. The source text
is fetched (never stored in the repository) at the commit and blob the lesson's metadata pins, and its git blob
SHA is checked first; only numbers are printed or written.

Usage:
    python3 scripts/sd101_source_distance.py                     # table of every lesson, closest first
    python3 scripts/sd101_source_distance.py --top 15 --json report.json
    python3 scripts/sd101_source_distance.py --offline --cache-dir DIR   # no network, cache only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from collections.abc import Sequence
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STORE = ROOT / "system-design-101" / "vi"
RAW_URL = "https://raw.githubusercontent.com/{repository}/{commit_sha}/{path}"
HEX40 = re.compile(r"[0-9a-f]{40}")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
SOURCE_PATH = re.compile(r"(?!.*(?:^|/)\.\.?(?:/|$))[A-Za-z0-9_.\-/]+")   # no "." or ".." part

# Sections of a lesson that are not its own prose: the glossary and the list of sources.
SKIPPED_SECTIONS = ("Từ viết tắt", "Nguồn đối chiếu")
READING_SECTION = "Đọc hình"
MIN_WORD = 4
ENGLISH_STOPWORDS = frozenset(
    """with that this from have they their there which would could about into than then them these those were been
    also other some such more most very when what where will your each many much only over after before being because
    while every still just like make made used uses using does doing both same next first second third called known
    here should must need needs want wants take takes give gives know knows well even less least ever never always""".split())
# A Vietnamese word is one syllable, and written without marks it still has a recognisable shape: an optional initial,
# a vowel group and an optional final. The ASCII filter alone cannot tell "theo" or "nhau" from an English word, so
# this shape is rejected as language, not as a name. A few real English words fit it too ("long", "ping", "tech");
# they are dropped from both sides alike, which costs a little coverage and nothing else.
INITIAL = r"(?:ngh|ng|nh|ph|th|tr|ch|kh|gh|gi|qu|[bcdghklmnprstvx])?"
VOWEL_WITHOUT_FINAL = r"(?:ieu|yeu|oai|oao|oay|oeo|uai|uay|uoi|uou|uya|ai|ao|au|ay|eo|eu|iu|oi|ui|uu|ia|ua|ya)"
VOWEL_WITH_FINAL = r"(?:uyen|uyet|uy|ie|uo|oa|oe|ue|ye|[aeiouy])(?:ng|nh|ch|[cmnpt])?"
VIETNAMESE_SYLLABLE = re.compile(f"{INITIAL}(?:{VOWEL_WITHOUT_FINAL}|{VOWEL_WITH_FINAL})")
STOPWORDS = ENGLISH_STOPWORDS

# A recorded run or measurement: the verbs the metadata uses for it, in Vietnamese and English. A match counts only when no
# negation comes shortly before it in the same clause, so "chưa chạy thử" (not run) is not evidence of a run.
RUN_PHRASE = re.compile(r"\b(chạy|đo|thử nghiệm|ran|measured|executed|observed|tested)\b", re.IGNORECASE)
NEGATION = re.compile(r"\b(chưa|không|khong|not|never|no|without)\b|n't", re.IGNORECASE)
NEGATION_WINDOW = 30
CLAUSE_BREAK = re.compile(r"[.;:\n()]")


def blob_sha(data: bytes) -> str:
    """The git blob id of a file's bytes, which is what source_snapshot.blob_sha pins."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def strip_html(text: str) -> str:
    """Comments and tags, so that <details> and <summary> are not read as words of the text."""
    return re.sub(r"<[^>]*>", " ", re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL))


def source_body(raw: str) -> str:
    """The guide without its front matter, its images, its image-source line and its markup."""
    body = re.sub(r"\A---\n.*?\n---\n", "", raw, count=1, flags=re.DOTALL)
    lines = [line for line in body.splitlines() if not re.match(r"\s*!\[", line) and not line.lower().startswith("image source")]
    return strip_html("\n".join(lines))


def source_units(body: str) -> int:
    """Top-level list items, paragraphs that open with a bold lead, and headings: the items a reader walks through."""
    count = 0
    for line in body.splitlines():
        if re.match(r"(\*|-|\d+\.)\s+\S", line) or re.match(r"\*\*[^*]+\*\*", line) or re.match(r"#{1,4}\s+\S", line):
            count += 1
    return count


def sections(markdown: str) -> dict[str, str]:
    """Split a lesson at its '## ' headings; the text before the first one is stored under ''."""
    found: dict[str, list[str]] = {"": []}
    current = ""
    for line in markdown.splitlines():
        match = re.match(r"##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1)
            found[current] = []
        else:
            found[current].append(line)
    return {title: "\n".join(lines) for title, lines in found.items()}


def lesson_prose(markdown: str) -> str:
    """What the lesson itself says: no glossary, no source list, no link destinations or image sources."""
    kept = [text for title, text in sections(markdown).items() if title not in SKIPPED_SECTIONS]
    prose = "\n".join(kept)
    prose = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", prose)
    prose = re.sub(r"\]\([^)]*\)", "]", prose)
    return strip_html(re.sub(r"https?://\S+", " ", prose))


def lesson_units(markdown: str) -> int:
    """Numbered items, bullets and bold leads of the reading section (the whole prose when it has none)."""
    parts = sections(markdown)
    text = parts.get(READING_SECTION)
    if text is None:
        text = lesson_prose(markdown)
    return sum(1 for line in text.splitlines()
               if re.match(r"(\d+\.|[-*])\s+\S", line) or re.match(r"\*\*[^*]+\*\*", line))


def signal_tokens(text: str) -> list[str]:
    """Names, technical terms and numbers, lower-cased, in order of first appearance.

    The text is split into whole Unicode words first, and a word counts only when all of it is ASCII letters, at least
    MIN_WORD long and not a stop word. A Vietnamese word has a mark somewhere in it, so it is dropped whole instead of
    leaving an ASCII fragment such as "chuy" from "chuyển". A number counts with its digits only."""
    seen: set[str] = set()
    ordered: list[str] = []
    for match in re.finditer(r"\d[\d.,]*\d|\w+(?:[_-]\w+)*", unicodedata.normalize("NFC", text)):
        token = match.group(0)
        if token[0].isdigit() and re.fullmatch(r"[\d.,]+", token):
            token = re.sub(r"\D", "", token)
            if len(token) >= 2 and token not in seen:
                seen.add(token)
                ordered.append(token)
            continue
        for piece in re.split(r"[_-]", token.lower()):
            if (len(piece) >= MIN_WORD and piece.isalpha() and piece.isascii() and piece not in STOPWORDS
                    and not VIETNAMESE_SYLLABLE.fullmatch(piece) and piece not in seen):
                seen.add(piece)
                ordered.append(piece)
    return ordered


def lcs_length(first: Sequence[str], second: Sequence[str]) -> int:
    previous = [0] * (len(second) + 1)
    for item in first:
        current = [0]
        for column, other in enumerate(second, 1):
            current.append(previous[column - 1] + 1 if item == other else max(previous[column], current[-1]))
        previous = current
    return previous[-1]


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))


def distance(source_raw: str, lesson_markdown: str) -> dict[str, float | int | None]:
    """The numbers for one lesson against its source (see the module docstring)."""
    body = source_body(source_raw)
    prose = lesson_prose(lesson_markdown)
    source_seq, lesson_seq = signal_tokens(body), signal_tokens(prose)
    shared = set(source_seq) & set(lesson_seq)
    coverage = len(shared) / len(source_seq) if source_seq else 0.0
    # Order is judged on the shared vocabulary only, so a lesson is not punished for words the source lacks.
    in_source = [token for token in source_seq if token in shared]
    in_lesson = [token for token in lesson_seq if token in shared]
    order = lcs_length(in_source, in_lesson) / len(in_source) if in_source else 0.0
    novelty = len(set(lesson_seq) - set(source_seq)) / len(set(lesson_seq)) if lesson_seq else 0.0
    replay = coverage * order
    n_source, n_lesson = source_units(body), lesson_units(lesson_markdown)
    mirror = min(n_source, n_lesson) / max(n_source, n_lesson) if min(n_source, n_lesson) >= 2 else None
    return {"coverage": coverage, "order": order, "replay": replay, "novelty": novelty,
            "closeness": replay * (1 - novelty), "source_units": n_source, "lesson_units": n_lesson,
            "unit_mirror": mirror, "size_ratio": word_count(prose) / max(word_count(body), 1),
            "source_tokens": len(source_seq), "lesson_tokens": len(lesson_seq)}


def claim_urls(metadata: dict) -> list[str]:
    urls: list[str] = []
    for claim in metadata.get("claims", []):
        if isinstance(claim, dict):
            urls.append(claim.get("source") or "")
            urls.extend(claim.get("sources") or [])
    return [url for url in urls if url]


def independent_hosts(metadata: dict) -> list[str]:
    """Hosts of the claim sources, leaving out the pinned source repository and bytebytego.com themselves."""
    repository = (metadata.get("source_snapshot") or {}).get("repository", "")
    own = [repository.lower(), "bytebytego"] if repository else ["bytebytego"]
    return sorted({urlparse(url).netloc for url in claim_urls(metadata) if not any(mark in url.lower() for mark in own)} - {""})


def recorded_run(text: str) -> bool:
    """True when a clause of the text says something was run or measured, and does not say it was not."""
    for clause in CLAUSE_BREAK.split(text):
        for match in RUN_PHRASE.finditer(clause):
            if not NEGATION.search(clause[max(0, match.start() - NEGATION_WINDOW):match.start()]):
                return True
    return False


def own_evidence(metadata: dict) -> bool:
    """True when a claim or the claims step records that something was run or measured."""
    texts = [str(claim.get("verified_by", "")) for claim in metadata.get("claims", []) if isinstance(claim, dict)]
    step = (metadata.get("verification") or {}).get("claims") or {}
    texts.extend(str(step.get(key, "")) for key in ("evidence", "scope"))
    return any(recorded_run(text) for text in texts)


def fetch_source(snapshot: dict, cache_dir: pathlib.Path, offline: bool) -> str:
    """The pinned source body, from the cache or the network; its git blob SHA must equal the pinned one."""
    pinned = snapshot["blob_sha"]
    if not (isinstance(pinned, str) and HEX40.fullmatch(pinned)):
        raise ValueError(f"blob_sha {pinned!r} is not a 40-hex git object id")
    cached = cache_dir / f"{pinned}.md"
    if cached.is_file():
        data = cached.read_bytes()
    elif offline:
        raise FileNotFoundError(f"{pinned} is not in the cache and --offline was given")
    else:
        for key, pattern in (("repository", REPOSITORY), ("commit_sha", HEX40), ("path", SOURCE_PATH)):
            if not (isinstance(snapshot[key], str) and pattern.fullmatch(snapshot[key])):
                raise ValueError(f"source_snapshot.{key} {snapshot[key]!r} cannot be turned into a download address")
        url = RAW_URL.format(**{key: snapshot[key] for key in ("repository", "commit_sha", "path")})
        with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 - a fixed https host and pinned path
            data = response.read()
        cache_dir.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(data)
    if blob_sha(data) != pinned:
        cached.unlink(missing_ok=True)
        raise ValueError(f"blob sha of {snapshot['path']} is {blob_sha(data)}, but the lesson pins {pinned}")
    return data.decode("utf-8")


def survey(store: pathlib.Path, cache_dir: pathlib.Path, offline: bool) -> tuple[list[dict], list[str]]:
    """One row per lesson that has a lesson.md and a metadata file, and the lessons that could not be measured."""
    rows: list[dict] = []
    problems: list[str] = []
    for lesson in sorted((store / "lessons").glob("sd-*/lesson.md")):
        lesson_id = lesson.parent.name
        meta_path = store / "metadata" / f"{lesson_id}.json"
        if not meta_path.is_file():
            continue
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            source = fetch_source(metadata["source_snapshot"], cache_dir, offline)
            row = {"id": lesson_id, "title_vi": metadata.get("title_vi"),
                   **distance(source, lesson.read_text(encoding="utf-8"))}
            row.update({"independent_hosts": len(independent_hosts(metadata)), "own_evidence": own_evidence(metadata)})
        except (OSError, ValueError, KeyError, TypeError, AttributeError, urllib.error.URLError) as error:
            problems.append(f"{lesson_id}: {type(error).__name__}: {error}")
            continue
        rows.append(row)
    rows.sort(key=lambda row: row["closeness"], reverse=True)
    return rows, problems


def table(rows: list[dict]) -> str:
    head = f"{'#':>3} {'id':<10} {'close':>5} {'replay':>6} {'order':>5} {'novel':>5} {'units':>7} {'size':>5} {'hosts':>5} run  title"
    lines = [head]
    for rank, row in enumerate(rows, 1):
        units = f"{row['source_units']}/{row['lesson_units']}"
        lines.append(f"{rank:>3} {row['id']:<10} {row['closeness']:>5.2f} {row['replay']:>6.2f} {row['order']:>5.2f} "
                     f"{row['novelty']:>5.2f} {units:>7} {row['size_ratio']:>5.1f} {row['independent_hosts']:>5} "
                     f"{'yes' if row['own_evidence'] else ' no'}  {str(row['title_vi'])[:44]}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rank lessons by how closely they follow their source guide.")
    parser.add_argument("--store", type=pathlib.Path, default=DEFAULT_STORE)
    parser.add_argument("--cache-dir", type=pathlib.Path, default=pathlib.Path.home() / ".cache" / "sd101-source-distance",
                        help="where fetched source bodies are kept; never inside the repository")
    parser.add_argument("--offline", action="store_true", help="use the cache only")
    parser.add_argument("--top", type=int, default=0, help="print only the closest N lessons")
    parser.add_argument("--json", type=pathlib.Path, help="also write the numbers as JSON")
    args = parser.parse_args(argv)
    if args.cache_dir.resolve().is_relative_to(ROOT):
        parser.error("--cache-dir must be outside the repository: source text is not committed")
    rows, problems = survey(args.store, args.cache_dir, args.offline)
    print(table(rows[: args.top] if args.top else rows))
    for problem in problems:
        print(f"could not measure {problem}", file=sys.stderr)
    if args.json:
        args.json.write_text(json.dumps({"lessons": rows, "unmeasured": problems}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
