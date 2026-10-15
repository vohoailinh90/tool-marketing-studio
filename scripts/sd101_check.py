#!/usr/bin/env python3
"""Check the Vietnamese System Design store against the rules in its DECISIONS.md.

Per `deterministic_work` in agent-routing/policy.yaml, "does this metadata match the
schema, does every lesson id exist in the source map, does a diagram exist, does the
progress record agree with what is on disk" are computable, so they are a script and a
CI check rather than something a reviewer re-derives by eye for each of ~400 lessons.
It was written in Agentic-coding-course after three lessons had each been checked by
hand with the same ad hoc commands, and moved here with the store.

The store, `system-design-101/vi/`, holds:
  README.md, PROGRESS.md, MIGRATION.md   prose; README.md is the index
  progress.json                          what is written, what is next
  lessons/<id>/lesson.md, lesson.yaml    the lesson; lesson.yaml only points at its metadata
  lessons/<id>.md                        optional one-line pointer to lessons/<id>/lesson.md
  metadata/<id>.json                     the single record of a lesson's status and evidence
  diagrams/<id>-main.svg                 the lesson's figure, drawn for it

What is checked, per lesson id:
  - lessons/<id>/ holds exactly lesson.md and lesson.yaml; lesson.yaml has only id (the directory
    name) and metadata_ref (../../metadata/<id>.json), so it cannot carry a second copy of the status
  - metadata/<id>.json parses (a key named twice is an error) and has the keys DECISIONS.md lists, no
    others; id equals the file name and is in the source map; title_vi equals the source map's;
    language is vi; content_status is draft | review | done, and done needs the technical review and
    the mobile check to have happened
  - source_ref is a source-map id and source_snapshot (repository, commit_sha, path, blob_sha, and the
    URL when it gives one) says exactly what that source-map entry does
  - each verification step is pending or happened (read, checked), with a real checked_on date once it
    happened; a mobile check records widths including 320 and no overflow; user_testing is not_performed
    or performed (a screenshot is not user testing, so nothing infers one from the other)
  - claims are mappings with a claim_vi and an http(s) source URL (or sources, a list of them), and a
    claim marked checked has at least one; prerequisites and related name source-map ids other than the
    lesson itself; image_evidence, when present, is {url, sha256, retrieved_on} with real values
  - the diagram is diagrams/<id>-main.svg and exists; every file in diagrams/ is such a figure for a
    written lesson, and a self-contained drawing: it parses as XML with an <svg> root, has a non-empty
    <title> or <desc>, uses only plain drawing elements (no <image>, <foreignObject>, <script>, <a>,
    animation, CSS @keyframes/animation/transition) and no processing instruction (<?xml-stylesheet?>) or
    DOCTYPE, links to nothing but its own #fragments (href, url(), @import), and never mentions the
    source image host, so a renamed PNG or an SVG that wraps or loads a raster is refused too
  - lesson.md: no code fence (``` or ~~~) is left open, raw HTML is limited to a short list of tags
    (details, summary, br, a, img, sub, sup, kbd), <details> tags nest properly (<details open> too),
    every relative link and image source (inline, reference-style, <a href>, <img src>, <img srcset>)
    resolves, every image has alt text and is an .svg file directly inside diagrams/, the lesson's own
    figure is one of them, it links the pinned source snapshot (as a real Markdown or HTML link, not text
    in a code block or a comment; a #fragment on it is fine), it mentions no lesson id that has no lesson
    directory, and it never contains assets.bytebytego.com, the host of every source image, in any form:
    ![]() , ![x][ref], <img>, <picture>, a bare URL
  - abbreviations: every abbreviation a beginner could trip on (LLM, DNS, SSE: two or more capital letters,
    and the mixed-case terms in MIXED_CASE_TERMS such as gRPC and IPv4) that lesson.md or its figure's text uses is explained in a "## Từ viết tắt" section, the first "##" of the
    lesson, one bullet each: - **LLM** (Large Language Model) — meaning: a plain-words explanation. The
    parenthesis spells the abbreviation out in Latin letters, so its initials give exactly the abbreviation
    (little words may be left out; camelCase and all-caps runs count: HyperText, SYNchronize); keywords, HTTP methods and file names that only
    look like abbreviations are in NOT_ACRONYMS or in `code`. The section may be left out when none is used.
And once for the store: it holds only the entries above (an image dropped beside the README is refused like
one in a lesson); README.md, PROGRESS.md and MIGRATION.md embed no image, use only the allowed raw HTML tags
(so no HTML table can hide a status), and every relative link in them resolves; README.md links every
lesson directory (as a real link, not a path in a comment or a code block) in source-map order and has no
status word (draft, review, done) in a table cell, however formatted or decorated (status lives only in
metadata/); progress.json's written_ids are the lessons on disk in source-map order, next_id is the first
source-map id not yet written, and its totals are the source map's.

This guards against honest mistakes while ~400 lessons are written; it is not a security
boundary. Markup crafted to slip past a rule on purpose is out of scope.

Not checked, because it is not computable here: whether a claim is true, whether a
figure reads well, the effective text size on a phone (needs a browser), and whether
a figure is drawn for the lesson or traced from the source image (a reviewer's call).

Usage:
    python3 scripts/sd101_check.py
    python3 scripts/sd101_check.py --store system-design-101/vi --source-map path.json
Exit status is 1 when any problem is found.
"""

from __future__ import annotations

import argparse
import datetime
import ipaddress
import itertools
import json
import pathlib
import posixpath
import re
import sys
import unicodedata
import xml.etree.ElementTree as ElementTree
import xml.parsers.expat as expat
from collections.abc import Iterable
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

import yaml
from markdown_it import MarkdownIt

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STORE = ROOT / "system-design-101" / "vi"
DEFAULT_SOURCE_MAP = ROOT / "brainstorm" / "system-design-101-vi" / "source-map.json"

LESSON_YAML_KEYS = {"id", "metadata_ref"}
METADATA_REQUIRED = {"id", "title_vi", "language", "kind", "content_status", "source_ref", "source_snapshot", "diagram",
                     "prerequisites", "related", "verification", "claims"}
METADATA_OPTIONAL = {"design_notes_vi", "editorial_note_vi", "source_only_trivia", "source_deviations", "prior_reviews",
                     "migration", "image_evidence"}
SNAPSHOT_REQUIRED = {"repository", "commit_sha", "path", "blob_sha"}
SNAPSHOT_OPTIONAL = {"snapshot_url", "blob_identity_status", "note", "retrieved_body_sha256", "retrieved_body_bytes"}
MIGRATION_KEYS = {"source_repository", "source_commit_sha", "destination_repository", "imported_on"}
CONTENT_STATUS = {"draft", "review", "done"}
# Each verification step: the state it starts in, and the state that says it happened. A step that happened
# carries the date it was checked on. DECISIONS.md records them separately, so one never stands in for another.
VERIFICATION_STEPS = {
    "source_body": ("pending", "read"),
    "claims": ("pending", "checked"),
    "technical_review": ("pending", "checked"),
    "mobile": ("pending", "checked"),
    "user_testing": ("not_performed", "performed"),
}
DONE_NEEDS = ("technical_review", "mobile")
MOBILE_WIDTH = 320
RELATED_KEYS = {"lesson_id", "relation", "reason_vi"}
IMAGE_EVIDENCE_KEYS = {"url", "sha256", "retrieved_on"}

LESSON_ID = re.compile(r"\bsd-\d{2}-\d{3}\b")
SHA256 = re.compile(r"[0-9a-fA-F]{64}")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
BLOCKQUOTE_PREFIX = re.compile(r"^(?:\s*>)+")
HOSTNAME = re.compile(r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.?")
STATUS_WORD = re.compile(r"(?<![^\W_])(?:draft|review|done)(?![^\W_])", re.IGNORECASE)
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
SOURCE_IMAGE_HOST = "assets.bytebytego.com"
LESSON_FILES = {"lesson.md", "lesson.yaml"}
STORE_ENTRIES = {"README.md", "PROGRESS.md", "MIGRATION.md", "progress.json", "diagrams", "lessons", "metadata"}
STORE_PAGES = ("README.md", "PROGRESS.md", "MIGRATION.md")
PROGRESS_REQUIRED = {"language", "total_occurrences", "total_source_documents", "written_ids", "reviewed_ids", "next_id"}
PROGRESS_ID_LISTS = ("reviewed_ids", "active_batch_ids", "prior_repository_reviewed_ids")
# DECISIONS.md keeps all 15 groups and 404 ids of the source, in its order; ids are never removed or reused.
# Changing the roster means changing this line and that decision together.
EXPECTED_GROUPS = (("sd-01", 50), ("sd-02", 32), ("sd-03", 8), ("sd-04", 47), ("sd-05", 5), ("sd-06", 29),
                   ("sd-07", 20), ("sd-08", 24), ("sd-09", 20), ("sd-10", 28), ("sd-11", 49), ("sd-12", 18),
                   ("sd-13", 27), ("sd-14", 35), ("sd-15", 12))
SOURCE_ENTRY_KEYS = {"id", "title_vi", "title_source", "source_url", "source_path", "source_body_reviewed",
                     "source_blob_sha", "source_snapshot_url"}
SOURCE_MAP_KEYS = {"schema_version", "language", "note", "source_repository", "source_readme_blob_sha", "observed_on",
                   "source_commit_sha", "source_tree_sha", "categories"}
SOURCE_REPOSITORY = "ByteByteGoHq/system-design-101"
GROUP_KEYS = {"id", "title_vi", "title_source", "lessons"}
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
COMMIT = re.compile(r"[0-9a-f]{40}")
LESSON_LINK = re.compile(r"lessons/(sd-\d{2}-\d{3})/lesson\.md")
ALLOWED_HTML = {"details", "summary", "br", "a", "img", "sub", "sup", "kbd"}
RASTER_ELEMENTS = {"image", "feimage", "img"}
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
# The elements of a plain drawing. Anything else (foreignObject and the HTML inside it, script, a, animation,
# image) is refused rather than hunted one by one: each is a way to carry or load something that is not drawn.
SVG_ELEMENTS = {
    "svg", "g", "defs", "symbol", "use", "title", "desc", "style",
    "path", "rect", "circle", "ellipse", "line", "polyline", "polygon",
    "text", "tspan", "textpath", "marker", "pattern", "mask", "clippath", "lineargradient", "radialgradient", "stop",
    "filter", "feblend", "fecolormatrix", "fecomposite", "fedropshadow", "fegaussianblur", "feflood", "feoffset",
    "femerge", "femergenode",
}
ANIMATION = re.compile(r"@keyframes|\banimation(?:-[a-z-]+)?\s*:|\btransition(?:-[a-z-]+)?\s*:", re.IGNORECASE)
URL_CALL = re.compile(r"url\(\s*['\"]?\s*([^)'\"\s]*)", re.IGNORECASE)

GLOSSARY_HEADING = "Từ viết tắt"
SOURCES_HEADING = "Nguồn đối chiếu"
# Two or more capital letters standing alone: LLM, DNS, HTTP/2 (-> HTTP), APIs (-> API). Digits written straight before
# the capitals belong to the abbreviation (2FA, 3DES, 2PC), so a quantity is written with a space ("10 GB", not 10GB).
# Not MAX_SIZE or a Vietnamese capital word with a mark on it, which are not read as abbreviations.
# A few terms carry their abbreviation in mixed case (gRPC, IPv4), which the capital-letter rule cannot see; they are
# listed here, so add a new one when a lesson introduces it. Either kind may end in a version number or a plural
# (OAuth2, vCPUs, MiBs, gRPCs, DHCPv4, TLSv1), which is read as the term itself.
# Unit symbols whose letters are not initials (MiB is "mebi" + byte): the full form is the unit's name.
UNIT_SYMBOLS = {"KiB": "Kibibyte", "MiB": "Mebibyte", "GiB": "Gibibyte", "TiB": "Tebibyte"}
# Names whose letters are not (all) initials: the full form is what they stand for (HPACK is "Header Compression for
# HTTP/2"; SLSA is "Supply-chain Levels for Software Artifacts", where "Supply-chain" is one word but two hyphen parts).
IRREGULAR_FORMS = {"HPACK": "Header Compression for HTTP/2", "SLSA": "Supply-chain Levels for Software Artifacts",
                   "W3C": "World Wide Web Consortium", "SELinux": "Security-Enhanced Linux", "WebAuthn": "Web Authentication",
                   "OpenID": "Open IDentity", "DevOps": "Development and Operations",
                   "DevSecOps": "Development, Security and Operations", "GitOps": "Git Operations", "NoOps": "No Operations",
                   "UTC": "Coordinated Universal Time", "EdDSA": "Edwards-curve Digital Signature Algorithm",
                   "NetBIOS": "Network Basic Input/Output System"}
# Names made from the initials of what they stand for, with lowercase or digits inside, so that no run of capitals
# shows them. A name that merely has capitals (JavaScript, GitHub, PostgreSQL) is not an abbreviation.
MIXED_CASE_TERMS = ("gRPC", "IPv4", "IPv6", "OAuth", "mTLS", "NoSQL", "vCPU", "IaC", "MoE", "PaaS", "IaaS", "SaaS", "FaaS", "BaaS",
                    "W3C", "SELinux", "WebAuthn", "OpenID", "DevOps", "DevSecOps", "GitOps", "NoOps", "EdDSA", "NetBIOS",
                    *UNIT_SYMBOLS)
ABBREVIATION = re.compile(r"(?<!\w)(?:(" + "|".join(MIXED_CASE_TERMS) + r")|(\d*[A-Z]{2,}))(?:v?\d+)?s?(?!\w)")
# Product names with an abbreviation inside them, which no run of capitals standing alone shows (OpenAI, MySQL, macOS):
# whoever reads the name meets the abbreviation, so the lesson explains it (AI, SQL, OS) like any other. The name maps to
# the abbreviation it carries; add a new one when a lesson introduces such a name. A possessive, a plural or a version
# number may follow (OpenAI's, MySQL8).
EMBEDDED_ABBREVIATIONS = {"ChatGPT": "GPT", "CommonJS": "JS", "FastAPI": "API", "HAProxy": "HA", "InfluxDB": "DB",
                          "InstructGPT": "GPT", "JinaAI": "AI", "LLMWare": "LLM", "MetalLB": "LB", "MySQL": "SQL",
                          "OOMKilled": "OOM", "OpenAI": "AI", "OpenSSH": "SSH", "PostgreSQL": "SQL", "PyJWT": "JWT",
                          "SQLite": "SQL", "TimescaleDB": "DB", "macOS": "OS"}
# The same terms and names set in capitals (OAUTH 2.0 in a heading), which read as the term they are.
UPPER_FORMS = {**{term.upper(): term for term in MIXED_CASE_TERMS},
               **{name.upper(): abbreviation for name, abbreviation in EMBEDDED_ABBREVIATIONS.items()}}
UPPER_FORM = re.compile(r"(?<!\w)(" + "|".join(UPPER_FORMS) + r")(?:V?\d+)?S?(?!\w)")
EMBEDDED_NAME = re.compile(r"(?<!\w)(" + "|".join(EMBEDDED_ABBREVIATIONS) + r")(?:v?\d+)?(?:[\u2019']?s)?(?!\w)")
GLOSSARY_BULLET = re.compile(r"^- \*\*(?P<abbreviation>(?=[A-Za-z0-9]*[A-Z])[A-Za-z0-9][A-Za-z0-9]+)\*\* "
                             r"\((?P<full>[^()]+)\) — (?P<meaning>\S.*)$")
MIN_MEANING_WORDS = 3
# An address typed into the text is a link destination, not prose: https://example.com/API/TLS, wss://host/API and
# git+ssh://host/TLS.git name no abbreviation. Any scheme counts; only "://" marks an address (a colon alone is prose).
URL = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://[^\s<>]+")
# Capital words that are not abbreviations: HTTP methods, SQL keywords, Dockerfile instructions, kubectl column titles,
# log levels and a few file or status names. They need no
# entry in the glossary. In lesson.md a `code span` is skipped too, so a new one can usually stay out of this list.
NOT_ACRONYMS = frozenset({
    "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "CONNECT", "TRACE",
    "SELECT", "FROM", "WHERE", "JOIN", "INNER", "LEFT", "RIGHT", "FULL", "OUTER", "CROSS", "ON", "USING", "AND", "OR",
    "NOT", "IS", "NULL", "IN", "AS", "GROUP", "ORDER", "BY", "HAVING", "LIMIT", "UNION", "INSERT", "UPDATE", "CREATE",
    "DROP", "TABLE", "VALUES", "SET",
    "OK", "README", "TODO",
    "COPY", "RUN", "EXPOSE", "STOPSIGNAL", "GOAWAY", "READY", "RESTARTS", "STATUS", "END", "ERROR",
    "KILL",  # SIGnal KILL: an ordinary word set in capitals to show the letters of SIGKILL
    "NGINX",  # a product name set in capitals (said "engine x"), not the initials of anything
})


# Ordinary words that read as an abbreviation when a figure label is set in capitals: Vietnamese ones without their accents
# (TIN is "news", RA is "out", HAY is "or"). A label word the glossary of some lesson explains is taken for that abbreviation
# (label_acronyms), which would make every unrelated figure that says TIN ask for a TIN entry the day another lesson defines
# TIN; a word here is never taken from the store. Add one when the checker reports a label-only abbreviation that is a plain word.
PLAIN_LABEL_WORDS = frozenset({
    "AN", "BA", "CHO", "HAI", "HAY", "KHI", "KHO", "NHANH", "NHU", "QUY", "RA", "SAO", "TAY", "THANH", "THEO", "TIN", "TRANG",
    "TRUY", "COOKIE", "POD",
})


@dataclass(frozen=True)
class Problem:
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.where}: {self.message}"


def object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    """json.loads keeps the last of two equal keys; a JSON file that names a key twice is ambiguous evidence."""
    seen: set[str] = set()
    for key, _value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key {key!r}")
        seen.add(key)
    return dict(pairs)


def read_json(path: pathlib.Path) -> tuple[object, str | None]:
    """A JSON file's value, or (None, why it cannot be read)."""
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=object_without_duplicate_keys), None
    except (OSError, ValueError, RecursionError) as error:  # JSONDecodeError and UnicodeDecodeError are ValueErrors
        return None, f"cannot be read: {error}"


def read_text(path: pathlib.Path) -> tuple[str | None, str | None]:
    """A text file's content, or (None, why it cannot be read): not UTF-8, or the filesystem refuses."""
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "is not valid UTF-8 text"
    except OSError as error:
        return None, f"cannot be read: {error}"


def repository_path(value: object) -> bool:
    """A path inside the repository that a URL reads as written: relative, with no empty, . or .. part (so no
    leading or trailing / either), and nothing a URL would split on or drop (# ? \\ whitespace)."""
    return (isinstance(value, str) and not any(part in ("", ".", "..") for part in value.split("/"))
            and not any(char.isspace() or not char.isprintable() or char in "#?\\" for char in value))


def text_value(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def entry_problems(entry: dict) -> list[str]:
    """What is wrong with one source-map entry: missing or unknown keys, and values of the wrong kind.

    The map records facts about the source only (DECISIONS.md), so progress fields are unknown keys here.
    """
    found: list[str] = []
    missing = sorted(SOURCE_ENTRY_KEYS - set(entry))
    unknown = sorted(set(entry) - SOURCE_ENTRY_KEYS - {"same_source_as"})
    if missing:
        found.append(f"is missing {', '.join(missing)}")
    if unknown:
        found.append(f"has unknown keys {', '.join(unknown)}; the map records facts about the source only")
    if entry.get("title_vi") is not None and not text_value(entry.get("title_vi")):
        found.append("title_vi must be null (not yet titled) or a non-empty string")
    if "title_source" in entry and not text_value(entry["title_source"]):
        found.append("title_source must be a non-empty string")
    if "source_path" in entry and not repository_path(entry["source_path"]):
        found.append("source_path must be a normalised path inside the repository (no leading /, no . or .. part)")
    if "source_url" in entry and not valid_url(entry["source_url"]):
        found.append("source_url must be an http(s) URL")
    if "source_body_reviewed" in entry and not isinstance(entry["source_body_reviewed"], bool):
        found.append("source_body_reviewed must be true or false")
    if "source_blob_sha" in entry and not (isinstance(entry["source_blob_sha"], str)
                                           and COMMIT.fullmatch(entry["source_blob_sha"])):
        found.append("source_blob_sha must be a 40-hex Git blob id")
    return found


def same_source_problems(entries: dict[str, dict]) -> list[str]:
    """Entries that share a source file must say so, both ways: same_source_as lists the other ids."""
    found: list[str] = []
    by_path: dict[str, list[str]] = {}
    for lesson_id, entry in entries.items():
        others = entry.get("same_source_as")
        if others is not None:
            if not isinstance(others, list) or not others or not all(isinstance(other, str) for other in others):
                found.append(f"{lesson_id}: same_source_as must be a non-empty list of ids")
                continue
            for other in others:
                partner = entries.get(other)
                if other == lesson_id or partner is None:
                    found.append(f"{lesson_id}: same_source_as names {other}, which is not another entry")
                elif lesson_id not in (partner.get("same_source_as") if isinstance(partner.get("same_source_as"), list) else []):
                    found.append(f"{lesson_id}: same_source_as names {other}, which does not name {lesson_id} back")
                elif partner.get("source_path") != entry.get("source_path"):
                    found.append(f"{lesson_id}: same_source_as names {other}, which has another source_path")
        if isinstance(entry.get("source_path"), str):
            by_path.setdefault(entry["source_path"], []).append(lesson_id)
    for group in by_path.values():
        for lesson_id in group:
            declared = entries[lesson_id].get("same_source_as")
            declared = set(declared) if isinstance(declared, list) else set()
            if not set(group) - {lesson_id} <= declared:
                found.append(f"{lesson_id}: shares its source_path with {', '.join(sorted(set(group) - {lesson_id}))} "
                             "but does not list them in same_source_as")
    return found


def top_level_problems(data: dict) -> list[str]:
    """The records around the groups that DECISIONS.md relies on: schema version, language, the pinned source."""
    found: list[str] = []
    if set(data) != SOURCE_MAP_KEYS:
        missing, unknown = sorted(SOURCE_MAP_KEYS - set(data)), sorted(set(data) - SOURCE_MAP_KEYS)
        found.append("has the wrong top-level keys" + (f"; missing {', '.join(missing)}" if missing else "")
                     + (f"; unknown {', '.join(unknown)}" if unknown else ""))
    if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
        found.append("schema_version must be 1")
    if data.get("language") != "vi":
        found.append("language must be 'vi'")
    if data.get("source_repository") != SOURCE_REPOSITORY:
        found.append(f"source_repository must be {SOURCE_REPOSITORY}")
    for key in ("source_commit_sha", "source_tree_sha", "source_readme_blob_sha"):
        value = data.get(key)
        if not (isinstance(value, str) and COMMIT.fullmatch(value)):
            found.append(f"{key} must be a 40-hex Git object id")
    if not valid_date(data.get("observed_on")):
        found.append("observed_on must be a YYYY-MM-DD date")
    if not text_value(data.get("note")):
        found.append("note must be a non-empty string")
    return found


def load_source_map(path: pathlib.Path, pin_roster: bool = False) -> tuple[dict[str, dict], tuple[str, str] | None,
                                                                          list[Problem]]:
    """The source map's lessons by id (in source order), its pinned (repository, commit) or None, and what is
    wrong with the file (if anything).

    Every entry must have exactly the source facts DECISIONS.md records (no progress fields), and its
    source_snapshot_url must be the blob URL of its source_path at the map's own pinned commit, so a moving URL
    (/blob/main/...) cannot slip in. Entries that share a source file must name each other in same_source_as.
    With pin_roster the map must also keep the 15 groups (by id and size) and 404 ids of DECISIONS.md, each
    group numbered 001, 002, ... in order.
    """
    data, error = read_json(path)
    if error:
        return {}, None, [Problem("source map", error)]
    categories = data.get("categories") if isinstance(data, dict) else None
    if not isinstance(categories, list):
        return {}, None, [Problem("source map", "has no 'categories' list")]
    repository, commit = data.get("source_repository"), data.get("source_commit_sha")
    top_level = top_level_problems(data) if pin_roster else []
    pinned = (isinstance(repository, str) and REPOSITORY.fullmatch(repository) is not None
              and isinstance(commit, str) and COMMIT.fullmatch(commit) is not None)
    entries: dict[str, dict] = {}
    problems: list[Problem] = [Problem("source map", reason) for reason in top_level]
    if not pinned:
        problems.append(Problem("source map", "needs a source_repository (owner/name) and a 40-hex source_commit_sha"))
    groups: list[tuple[object, int]] = []
    for position, category in enumerate(categories):
        lessons = category.get("lessons") if isinstance(category, dict) else None
        if not isinstance(lessons, list):
            problems.append(Problem("source map", f"category {position} has no 'lessons' list"))
            continue
        groups.append((category.get("id"), len(lessons)))
        if pin_roster and (set(category) != GROUP_KEYS or not text_value(category.get("title_vi"))
                           or not text_value(category.get("title_source"))):
            problems.append(Problem("source map", f"group {category.get('id')} needs exactly {', '.join(sorted(GROUP_KEYS))} "
                                                  "with a title_vi and a title_source"))
        for number, lesson in enumerate(lessons, 1):
            lesson_id = lesson.get("id") if isinstance(lesson, dict) else None
            if not isinstance(lesson_id, str):
                problems.append(Problem("source map", f"a lesson entry in category {position} has no string 'id'"))
                continue
            if lesson_id in entries:
                problems.append(Problem("source map", f"{lesson_id} is listed twice"))
                continue
            entries[lesson_id] = lesson
            problems.extend(Problem("source map", f"{lesson_id} {reason}") for reason in entry_problems(lesson))
            if pin_roster and lesson_id != f"{category.get('id')}-{number:03d}":
                problems.append(Problem("source map", f"{lesson_id} should be {category.get('id')}-{number:03d}: "
                                                      "ids run 001, 002, ... within their group"))
            source_path = lesson.get("source_path")
            if pinned and (not isinstance(source_path, str) or not source_path
                           or lesson.get("source_snapshot_url") != f"https://github.com/{repository}/blob/{commit}/{source_path}"):
                problems.append(Problem("source map", f"{lesson_id}: source_snapshot_url is not "
                                                      f"https://github.com/{repository}/blob/{commit}/<source_path>"))
    problems.extend(Problem("source map", reason) for reason in same_source_problems(entries))
    if pin_roster and tuple(groups) != EXPECTED_GROUPS:
        first = next(f"{got} instead of {want}" for got, want in itertools.zip_longest(groups, EXPECTED_GROUPS)
                     if got != want)
        problems.append(Problem("source map", f"does not keep the {len(EXPECTED_GROUPS)} groups and "
                                              f"{sum(size for _, size in EXPECTED_GROUPS)} ids of DECISIONS.md in "
                                              f"order (first difference: {first})"))
    return entries, (repository, commit) if pinned else None, problems


def srcset_urls(value: str) -> list[str]:
    """The URLs of an <img srcset> value: each candidate is a URL, then optional descriptors, comma separated."""
    urls: list[str] = []
    position = 0
    while True:
        match = re.compile(r"[\s,]*(\S+)").match(value, position)
        if match is None:
            return urls
        url, position = match.group(1), match.end()
        if url.endswith(","):
            url = url.rstrip(",")
        else:
            comma = value.find(",", position)
            position = len(value) if comma == -1 else comma + 1
        urls.append(url)


class StrictLoader(yaml.SafeLoader):
    """A safe YAML loader that refuses a mapping naming the same key twice (safe_load keeps the last one)."""

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            seen = set()
            for key_node, _value in node.value:
                if key_node.tag == "tag:yaml.org,2002:merge":  # `<<: *anchor`; an explicit key may override it
                    continue
                key = self.construct_object(key_node, deep=True)
                try:
                    duplicate = key in seen
                except TypeError:  # an unhashable key; the base class reports it
                    continue
                if duplicate:
                    raise yaml.constructor.ConstructorError("while constructing a mapping", node.start_mark,
                                                            f"found duplicate key {key!r}", key_node.start_mark)
                seen.add(key)
        return super().construct_mapping(node, deep=deep)


class HtmlScan(HTMLParser):
    """Facts about the HTML tags in a piece of HTML: which tags, each <a href>, each <img src> and srcset URL,
    <img> without alt text, <details> nesting.

    Comments and attribute text are not tags, so a quoted "href=..." or a commented-out tag counts for nothing.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: set[str] = set()
        self.hrefs: list[str] = []
        self.srcs: list[str] = []
        self.images_without_alt = 0
        self.details_depth = 0
        self.stray_details_close = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        if tag == "a":
            self.hrefs.extend(value for name, value in attrs if name == "href" and value)
        elif tag == "img":
            sources = [value for name, value in attrs if name == "src" and value]
            for name, value in attrs:
                if name == "srcset" and value:
                    sources.extend(srcset_urls(value))
            self.srcs.extend(sources or [""])
            if not any(name == "alt" and value and value.strip() for name, value in attrs):
                self.images_without_alt += 1
        elif tag == "details":
            self.details_depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """A self-closing tag is a start tag: in HTML <details/> still opens a details element."""
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        self.tags.add(tag)
        if tag == "details":
            if self.details_depth:
                self.details_depth -= 1
            else:
                self.stray_details_close = True


def markdown_tokens(text: str) -> list:
    """Every token Markdown (CommonMark plus GFM tables) produces for text, inline children included."""
    tokens: list = []
    for token in MarkdownIt("commonmark").enable("table").parse(text):
        tokens.append(token)
        tokens.extend(token.children or [])
    return tokens


def html_scan(text: str) -> HtmlScan:
    """Scan only the HTML Markdown would render: not code blocks, code spans or comments."""
    scan = HtmlScan()
    for token in markdown_tokens(text):
        if token.type in ("html_inline", "html_block"):
            scan.feed(token.content)
    return scan


def has_unclosed_fence(text: str) -> bool:
    """True when a code fence (``` or ~~~, any length) is still open at the end of the file."""
    lines = text.split("\n")
    for token in markdown_tokens(text):
        if token.type == "fence" and token.map:
            last = token.map[1] - 1
            closing = BLOCKQUOTE_PREFIX.sub("", lines[last]).strip() if token.map[0] < last < len(lines) else ""
            if not (set(closing) == {token.markup[0]} and len(closing) >= len(token.markup)):
                return True
    return False


def link_sequence(text: str) -> list[str]:
    """Destinations of the links Markdown would render, in the order a reader meets them:
    [x](url), [x][ref] and <a href>.

    A URL in a code block, an HTML comment or plain prose is not a link, so it is not returned.
    """
    found: list[str] = []
    for token in markdown_tokens(text):
        if token.type == "link_open":
            found.append(token.attrGet("href") or "")
        elif token.type in ("html_inline", "html_block"):
            scan = HtmlScan()
            scan.feed(token.content)
            found.extend(scan.hrefs)
    return found


def link_destinations(text: str) -> set[str]:
    """The distinct destinations of the links Markdown would render."""
    return set(link_sequence(text))


def image_sources(text: str) -> set[str]:
    """Sources of the images Markdown would render: ![x](src), ![x][ref] and <img src>."""
    found = {token.attrGet("src") or "" for token in markdown_tokens(text) if token.type == "image"}
    return found | set(html_scan(text).srcs)


def images_without_alt(text: str) -> int:
    """How many images Markdown would render have no alt text: ![](src) and <img> with no alt, or a blank one."""
    markdown = sum(1 for token in markdown_tokens(text) if token.type == "image" and not token.content.strip())
    return markdown + html_scan(text).images_without_alt


def table_cells(text: str) -> list[str]:
    """The text shown in every cell of every table Markdown would render, with or without outer pipes.

    It is read from the inline tokens, so link syntax, emphasis marks, HTML tags and entities are gone.
    """
    tokens = markdown_tokens(text)
    return ["".join(child.content for child in following.children or []
                    if child.type in ("text", "code_inline"))
            for token, following in zip(tokens, tokens[1:])
            if token.type in ("th_open", "td_open") and following.type == "inline"]


def relative_target(destination: str) -> str | None:
    """The path part of a relative link destination; None for an anchor, a URL or a mail link."""
    if destination.startswith("//") or SCHEME.match(destination):
        return None
    return unquote(destination.split("#")[0].split("?")[0]) or None


def repository_root(store: pathlib.Path) -> pathlib.Path:
    """How far a relative link may reach: the checkout when the store sits inside it, else the store itself."""
    resolved = store.resolve()
    return ROOT if resolved == ROOT or ROOT in resolved.parents else resolved


def resolved_inside(base: pathlib.Path, target: str, boundary: pathlib.Path) -> pathlib.Path | None:
    """What a relative link target names under boundary, or None when it names nothing there.

    A root-relative target (/x) is not relative to the file: on GitHub it points outside the repository, and
    joined to base it would silently become a path on the machine running the check. A relative target that
    climbs out of the boundary (../../../etc/passwd), or leaves it through a symlink, points elsewhere on
    GitHub too. A name the filesystem rejects (too long, embedded NUL) simply does not exist.
    """
    if target.startswith("/"):
        return None
    try:
        resolved = (base / target).resolve()
        return resolved if (resolved == boundary or boundary in resolved.parents) and resolved.exists() else None
    except (OSError, ValueError, RuntimeError):
        return None


def resolves(base: pathlib.Path, target: str, boundary: pathlib.Path) -> bool:
    return resolved_inside(base, target, boundary) is not None


def valid_host(host: str | None) -> bool:
    """A DNS name (ASCII labels, as in a copied address bar) or an IP address; not empty, not '.' or '-a'."""
    if not host:
        return False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return HOSTNAME.fullmatch(host) is not None
    return True


def valid_url(url: object) -> bool:
    """An http(s) URL with a real host and a readable port, no whitespace or control characters."""
    if not isinstance(url, str) or any(char.isspace() or not char.isprintable() for char in url):
        return False
    try:
        parsed = urlparse(url)
        parsed.port
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and valid_host(parsed.hostname)


def one_of(value: object, vocabulary: set[str] | tuple[str, ...]) -> bool:
    """True when value is a string in the vocabulary; a list or mapping from JSON is simply not."""
    return isinstance(value, str) and value in vocabulary


def valid_date(when: object) -> bool:
    """A real calendar date written YYYY-MM-DD (a timestamp is not a date)."""
    if not isinstance(when, str) or ISO_DATE.fullmatch(when) is None:
        return False
    try:
        datetime.date.fromisoformat(when)
    except ValueError:
        return False
    return True


def valid_image_evidence(item: object) -> bool:
    """An entry has an http(s) url with a host, a 64-hex sha256 and a real date."""
    if not isinstance(item, dict) or set(item) != IMAGE_EVIDENCE_KEYS:
        return False
    digest = item["sha256"]
    return (valid_url(item["url"]) and isinstance(digest, str) and SHA256.fullmatch(digest) is not None
            and valid_date(item["retrieved_on"]))


def local_name(name: str) -> str:
    """The lower-case local part of an XML name: '{namespace}feImage' -> 'feimage'."""
    return name.rsplit("}", 1)[-1].lower()


def reaches_outside(value: str) -> bool:
    """True when a CSS or attribute value has an @import or a url() that is not a #fragment of the drawing."""
    return "@import" in value.lower() or any(not target.startswith("#") for target in URL_CALL.findall(value))


def namespace_of(tag: str) -> str:
    """The namespace of an ElementTree tag such as '{http://www.w3.org/2000/svg}rect'; '' when it has none."""
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def prolog_features(raw: bytes) -> list[str]:
    """What an XML document carries besides its elements that can pull in something else: processing
    instructions (<?xml-stylesheet ...?>) and a DOCTYPE (an external DTD, entities). The XML declaration is neither."""
    found: list[str] = []
    parser = expat.ParserCreate()
    parser.ProcessingInstructionHandler = lambda target, data: found.append(f"a processing instruction (<?{target} ...?>)")
    parser.StartDoctypeDeclHandler = lambda name, system_id, public_id, has_internal: found.append("a DOCTYPE declaration")
    parser.Parse(raw, True)  # ElementTree has already read this file, so it is well-formed
    return found


def svg_problem(path: pathlib.Path) -> str | None:
    """Why a file named *.svg is not a self-contained drawing made for the lesson, or None."""
    try:
        root = ElementTree.parse(path).getroot()
    except (ElementTree.ParseError, OSError, LookupError):
        return "is not well-formed XML, so it is not an SVG"
    if root.tag.rsplit("}", 1)[-1] != "svg":
        return "does not have an <svg> root element"
    if SOURCE_IMAGE_HOST in path.read_text(encoding="utf-8", errors="replace").lower():
        return f"contains {SOURCE_IMAGE_HOST}; figures must not use source images"
    if found := prolog_features(path.read_bytes()):
        return f"has {found[0]}, which can load a stylesheet, a DTD or another file; remove it"
    described = False
    for element in root.iter():
        name = local_name(element.tag)
        if name in RASTER_ELEMENTS:
            return f"embeds a picture with <{name}>"
        if name not in SVG_ELEMENTS or namespace_of(element.tag) not in ("", SVG_NAMESPACE):
            return f"uses <{name}>, which is not an element of a plain SVG drawing"
        described = described or (name in ("title", "desc") and bool((element.text or "").strip()))
        values = list(element.attrib.items())
        if name == "style":
            values.append(("style", element.text or ""))
        for attribute, value in values:
            if local_name(attribute) == "href" and not value.strip().startswith("#"):
                return f"links to {value.strip()!r}, outside the drawing"
            if reaches_outside(value):
                return "refers to something outside the drawing with url() or @import"
            if ANIMATION.search(value):
                return "uses a CSS animation or transition, but a figure is static"
    if not described:
        return "has no text description: give it a non-empty <title> or <desc>"
    return None


def check_lesson_yaml(lesson_id: str, meta: object) -> list[Problem]:
    """lesson.yaml only points at the lesson's metadata; a status or evidence here would be a second copy."""
    if not isinstance(meta, dict):
        return [Problem(lesson_id, "lesson.yaml is not a mapping")]
    problems: list[Problem] = []
    if set(meta) != LESSON_YAML_KEYS:
        problems.append(Problem(lesson_id, f"lesson.yaml keys are {sorted(map(str, meta))}, expected "
                                           f"{sorted(LESSON_YAML_KEYS)}; the status lives only in metadata/{lesson_id}.json"))
    if meta.get("id") != lesson_id:
        problems.append(Problem(lesson_id, f"lesson.yaml id is {meta.get('id')!r}, expected the directory name"))
    if meta.get("metadata_ref") != f"../../metadata/{lesson_id}.json":
        problems.append(Problem(lesson_id, f"lesson.yaml metadata_ref must be ../../metadata/{lesson_id}.json"))
    return problems


def partners_of(entry: dict | None) -> list:
    """The ids an entry says it shares its source file with ([] when it says nothing, or not a list)."""
    partners = (entry or {}).get("same_source_as")
    return partners if isinstance(partners, list) else []


def snapshot_problems(lesson_id: str, snapshot: object, source_ref: object, entries: dict[str, dict],
                      pin: tuple[str, str] | None) -> list[str]:
    """source_ref names the source-map entry the lesson was written from (its own, or one it shares a file with),
    and source_snapshot says exactly what that entry does: repository, commit, path, blob and URL."""
    found: list[str] = []
    entry = entries.get(source_ref) if isinstance(source_ref, str) else None
    if entry is None:
        found.append(f"source_ref {source_ref!r} is not in the source map")
    elif source_ref != lesson_id and source_ref not in partners_of(entries.get(lesson_id)):
        found.append(f"source_ref {source_ref!r} is neither the lesson itself nor an entry it shares a source with")
    if not isinstance(snapshot, dict):
        return found + ["source_snapshot must be an object"]
    missing, unknown = sorted(SNAPSHOT_REQUIRED - set(snapshot)), sorted(set(snapshot) - SNAPSHOT_REQUIRED - SNAPSHOT_OPTIONAL)
    if missing:
        found.append(f"source_snapshot is missing {', '.join(missing)}")
    if unknown:
        found.append(f"source_snapshot has unknown keys {', '.join(unknown)}")
    if entry is not None:
        expected = {"path": entry.get("source_path"), "blob_sha": entry.get("source_blob_sha"),
                    "snapshot_url": entry.get("source_snapshot_url")}
        if pin is not None:
            expected.update({"repository": pin[0], "commit_sha": pin[1]})
        found.extend(f"source_snapshot {key} is {snapshot[key]!r}, but the source map has {value!r}"
                     for key, value in expected.items() if key in snapshot and snapshot[key] != value)
    digest = snapshot.get("retrieved_body_sha256")
    if digest is not None and not (isinstance(digest, str) and SHA256.fullmatch(digest)):
        found.append("source_snapshot retrieved_body_sha256 must be 64 hex characters")
    size = snapshot.get("retrieved_body_bytes")
    if size is not None and (not isinstance(size, int) or isinstance(size, bool) or size <= 0):
        found.append("source_snapshot retrieved_body_bytes must be a positive integer")
    found.extend(f"source_snapshot {key} must be a non-empty string" for key in ("blob_identity_status", "note")
                 if key in snapshot and not text_value(snapshot[key]))
    return found


def mobile_problems(step: dict) -> list[str]:
    """A mobile check that happened records the widths it covered (320 at least) and finding no overflow."""
    found: list[str] = []
    widths = step.get("widths_px")
    if not (isinstance(widths, list) and MOBILE_WIDTH in widths
            and all(isinstance(width, int) and not isinstance(width, bool) and width > 0 for width in widths)):
        found.append(f"mobile widths_px must be a list of widths that includes {MOBILE_WIDTH}")
    if step.get("whole_lesson_no_horizontal_overflow") is not True:
        found.append("mobile whole_lesson_no_horizontal_overflow must be true")
    if step.get("text_outside_viewbox") is not False:
        found.append("mobile text_outside_viewbox must be false")
    if step.get("overflow", False) is not False:
        found.append("mobile overflow must be false")
    if not text_value(step.get("evidence")):
        found.append("mobile needs evidence text saying how it was checked")
    return found


def verification_problems(verification: object) -> tuple[list[str], dict[str, bool]]:
    """What is wrong with the verification record, and which steps happened (so content_status can be judged)."""
    happened = {name: False for name in VERIFICATION_STEPS}
    if not isinstance(verification, dict) or set(verification) != set(VERIFICATION_STEPS):
        return [f"verification must have exactly {', '.join(VERIFICATION_STEPS)}"], happened
    found: list[str] = []
    for name, (initial, completed) in VERIFICATION_STEPS.items():
        step = verification[name]
        status = step.get("status") if isinstance(step, dict) else None
        if not one_of(status, (initial, completed)):
            found.append(f"verification {name} status {status!r} is not {initial} or {completed}")
            continue
        happened[name] = status == completed
        if happened[name] and not valid_date(step.get("checked_on")):
            found.append(f"verification {name} is {completed} but has no real checked_on date")
        if name == "mobile" and happened[name]:
            found.extend(mobile_problems(step))
    return found, happened


def claim_problems(claims: object, checked: bool) -> list[str]:
    """Each claim is a statement with the URL(s) it rests on; a claims step that happened needs at least one."""
    if not isinstance(claims, list):
        return ["claims must be a list"]
    found = ["claims is empty, but the claims step is marked checked"] if checked and not claims else []
    for position, claim in enumerate(claims, 1):
        if not isinstance(claim, dict):
            found.append(f"claim {position} is not an object")
            continue
        if not text_value(claim.get("claim_vi")):
            found.append(f"claim {position} needs a claim_vi")
        urls = ([claim["source"]] if "source" in claim else []) + (claim["sources"] if isinstance(claim.get("sources"), list) else [])
        if not urls or ("sources" in claim and not isinstance(claim["sources"], list)) or not all(valid_url(url) for url in urls):
            found.append(f"claim {position} needs an http(s) source URL (source, or sources as a list)")
        if "id" in claim and not text_value(claim["id"]):
            found.append(f"claim {position} id must be a non-empty string")
    return found


def lesson_reference_problems(meta: dict, lesson_id: str, entries: dict[str, dict]) -> list[str]:
    """prerequisites and related name other source-map ids (not necessarily written yet, not the lesson itself)."""
    found: list[str] = []
    named: list[object] = []
    prerequisites, related = meta.get("prerequisites"), meta.get("related")
    if not isinstance(prerequisites, list):
        found.append("prerequisites must be a list of lesson ids")
    else:
        named.extend(prerequisites)
    if not isinstance(related, list):
        found.append("related must be a list")
    else:
        for item in related:
            if not isinstance(item, dict) or set(item) != RELATED_KEYS or not text_value(item.get("relation")) \
                    or not text_value(item.get("reason_vi")):
                found.append(f"each related entry needs exactly {', '.join(sorted(RELATED_KEYS))}")
            else:
                named.append(item["lesson_id"])
    found.extend(f"{value!r} in prerequisites or related is not another id of the source map" for value in named
                 if not isinstance(value, str) or value == lesson_id or value not in entries)
    return found


def migration_problems(migration: object) -> list[str]:
    """Where an imported lesson came from: both repositories, the source commit and the date it was imported."""
    if not isinstance(migration, dict) or set(migration) != MIGRATION_KEYS:
        return [f"migration must have exactly {', '.join(sorted(MIGRATION_KEYS))}"]
    found: list[str] = []
    for key in ("source_repository", "destination_repository"):
        if not (isinstance(migration[key], str) and REPOSITORY.fullmatch(migration[key])):
            found.append(f"migration {key} must be owner/name")
    if not (isinstance(migration["source_commit_sha"], str) and COMMIT.fullmatch(migration["source_commit_sha"])):
        found.append("migration source_commit_sha must be a 40-hex commit")
    if not valid_date(migration["imported_on"]):
        found.append("migration imported_on must be a YYYY-MM-DD date")
    return found


def check_metadata(lesson_id: str, meta: object, entries: dict[str, dict], pin: tuple[str, str] | None) -> list[Problem]:
    where = f"metadata/{lesson_id}.json"
    if not isinstance(meta, dict):
        return [Problem(where, "is not a JSON object")]
    reasons: list[str] = []
    missing, unknown = sorted(METADATA_REQUIRED - set(meta)), sorted(set(meta) - METADATA_REQUIRED - METADATA_OPTIONAL)
    if missing:
        reasons.append(f"is missing {', '.join(missing)}")
    if unknown:
        reasons.append(f"has unknown keys {', '.join(unknown)}")
    if meta.get("id") != lesson_id:
        reasons.append(f"id is {meta.get('id')!r}, expected the file name")
    entry = entries.get(lesson_id)
    if entry is None:
        reasons.append("id is not in the source map")
    title = meta.get("title_vi")
    if not text_value(title):
        reasons.append("title_vi must be a non-empty string")
    elif entry is not None and title != entry.get("title_vi"):
        reasons.append("title_vi differs from the source map")
    if meta.get("language") != "vi":
        reasons.append("language must be 'vi'")
    if not text_value(meta.get("kind")):
        reasons.append("kind must be a non-empty string")
    if meta.get("diagram") != f"../diagrams/{lesson_id}-main.svg":
        reasons.append(f"diagram must be ../diagrams/{lesson_id}-main.svg")

    reasons.extend(snapshot_problems(lesson_id, meta.get("source_snapshot"), meta.get("source_ref"), entries, pin))
    reasons.extend(lesson_reference_problems(meta, lesson_id, entries))
    steps, happened = verification_problems(meta.get("verification"))
    reasons.extend(steps)
    status = meta.get("content_status")
    if not one_of(status, CONTENT_STATUS):
        reasons.append(f"content_status {status!r} is not one of {sorted(CONTENT_STATUS)}")
    elif status == "done" and not all(happened[name] for name in DONE_NEEDS):
        reasons.append(f"done needs {' and '.join(DONE_NEEDS)} to have happened")
    reasons.extend(claim_problems(meta.get("claims"), happened["claims"]))

    for key in ("design_notes_vi", "editorial_note_vi"):
        if key in meta and not text_value(meta[key]):
            reasons.append(f"{key} must be a non-empty string")
    for key in ("source_only_trivia", "prior_reviews"):
        if key in meta and not (isinstance(meta[key], list) and all(isinstance(item, dict) for item in meta[key])):
            reasons.append(f"{key} must be a list of objects")
    if "source_deviations" in meta and not (isinstance(meta["source_deviations"], list)
                                            and all(text_value(item) for item in meta["source_deviations"])):
        reasons.append("source_deviations must be a list of non-empty strings")
    if "migration" in meta:
        reasons.extend(migration_problems(meta["migration"]))
    if "image_evidence" in meta and not (isinstance(meta["image_evidence"], list)
                                         and all(valid_image_evidence(item) for item in meta["image_evidence"])):
        reasons.append("image_evidence must be a list of entries with an http(s) url, a 64-hex sha256 and a retrieved_on date")
    return [Problem(where, reason) for reason in reasons]


def check_page(name: str, text: str, base: pathlib.Path, boundary: pathlib.Path) -> list[Problem]:
    """What every prose page of the store shares: no figures, only the allowed raw HTML, links that land."""
    problems = [Problem(name, f"uses <{tag}>; raw HTML is limited to {', '.join(sorted(ALLOWED_HTML))}")
                for tag in sorted(html_scan(text).tags - ALLOWED_HTML)]
    problems.extend(Problem(name, f"embeds the image {source!r}; the pages of the store have no figures")
                    for source in sorted(image_sources(text)))
    problems.extend(Problem(name, f"relative link {destination!r} does not resolve")
                    for destination in sorted(link_destinations(text))
                    if (target := relative_target(destination)) and not resolves(base, target, boundary))
    if SOURCE_IMAGE_HOST in text.lower():
        problems.append(Problem(name, f"contains {SOURCE_IMAGE_HOST}; the store must not use source images"))
    return problems


def check_markdown(lesson_id: str, text: str, lesson_dir: pathlib.Path, entries: dict[str, dict],
                   lesson_ids: set[str], boundary: pathlib.Path, diagrams_dir: pathlib.Path) -> list[Problem]:
    problems: list[Problem] = []
    if has_unclosed_fence(text):
        problems.append(Problem(lesson_id, "lesson.md has an unclosed code fence"))
    scan = html_scan(text)
    if scan.stray_details_close or scan.details_depth:
        problems.append(Problem(lesson_id, "lesson.md has unbalanced <details> tags"))
    for tag in sorted(scan.tags - ALLOWED_HTML):
        problems.append(Problem(lesson_id, f"lesson.md uses <{tag}>; raw HTML is limited to "
                                           f"{', '.join(sorted(ALLOWED_HTML))}"))
    sources = image_sources(text)
    for destination in sorted(link_destinations(text) | sources):
        target = relative_target(destination)
        if target is not None and not resolves(lesson_dir, target, boundary):
            problems.append(Problem(lesson_id, f"relative link {destination!r} does not resolve"))
    shown: set[pathlib.Path | None] = set()
    for source in sorted(sources):
        target = relative_target(source)
        figure = resolved_inside(lesson_dir, target, boundary) if target is not None else None
        shown.add(figure)
        if figure is None or figure.suffix != ".svg" or figure.parent != diagrams_dir.resolve():
            problems.append(Problem(lesson_id, f"image {source!r} must be an .svg figure directly inside diagrams/"))
    if (diagrams_dir / f"{lesson_id}-main.svg").resolve() not in shown:
        problems.append(Problem(lesson_id, f"lesson.md does not show its figure diagrams/{lesson_id}-main.svg"))
    if images_without_alt(text):
        problems.append(Problem(lesson_id, "lesson.md has an image without alt text"))
    if lesson_id in entries:
        snapshot = entries[lesson_id].get("source_snapshot_url")
        if not isinstance(snapshot, str) or not snapshot.strip():
            problems.append(Problem(lesson_id, "the source map has no source_snapshot_url for this lesson"))
        elif snapshot not in {destination.split("#")[0] for destination in link_destinations(text)}:
            problems.append(Problem(lesson_id, "lesson.md does not link the pinned source snapshot"))
    for mentioned in sorted(set(LESSON_ID.findall(text))):
        if mentioned not in lesson_ids:
            problems.append(Problem(lesson_id, f"mentions {mentioned}, which has no lesson directory"))
    if SOURCE_IMAGE_HOST in text.lower():
        problems.append(Problem(lesson_id, f"contains {SOURCE_IMAGE_HOST}; lessons must not use source images"))
    return problems


class HtmlText(HTMLParser):
    """What a reader (or a screen reader) takes from a piece of HTML: its text and the alt text of its images, not
    its tags, attributes or comments."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.pieces: list[str] = []

    def handle_data(self, data: str) -> None:
        self.pieces.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            self.pieces.extend(value for name, value in attrs if name == "alt" and value)


def html_text(html: str) -> str:
    parser = HtmlText()
    parser.feed(html)
    parser.close()
    return URL.sub(" ", " ".join(parser.pieces))  # a typed address is no more prose in HTML than in Markdown


def abbreviations_in(text: str, capitals: bool = True) -> set[str]:
    """The abbreviations a piece of text uses: capital-letter runs, MIXED_CASE_TERMS and the abbreviation inside each
    name of EMBEDDED_ABBREVIATIONS, minus the words in NOT_ACRONYMS. With capitals=False only the mixed-case terms and
    names count: in a heading set in capitals a Vietnamese word cannot be told from an abbreviation, but gRPC, IPv4 and
    OpenAI can."""
    found = {UPPER_FORMS[match.group(1)] for match in UPPER_FORM.finditer(text)}
    text = UPPER_FORM.sub(" ", text)  # a term in capitals is the term, not a capital run of its own
    found |= {match.group(1) or (match.group(2) if capitals else "") for match in ABBREVIATION.finditer(text)}
    found |= {EMBEDDED_ABBREVIATIONS[match.group(1)] for match in EMBEDDED_NAME.finditer(text)}
    return found - {""} - NOT_ACRONYMS


def label_acronyms(headings: list[str] | tuple[str, ...], known: frozenset[str] = frozenset()) -> set[str]:
    """The abbreviations in figure labels set in capitals. There a word of capital letters cannot be told from an
    abbreviation (the Vietnamese TIN and HAI, the English COOKIE), so the abbreviation in it is read only when it cannot
    be a word: it has no vowel (JWT, DNS, LB), or some glossary of the store explains it (`known`) and it is not one of
    the PLAIN_LABEL_WORDS. A word that is not capital letters alone cannot be a Vietnamese or English word: a plural (APIs,
    LLMs) or a digit (2FA, 3DES, POP3) shows that it is an abbreviation, and one with an accent is Vietnamese, never an
    abbreviation."""
    found: set[str] = set()
    for word in re.findall(r"\w+", unicodedata.normalize("NFC", "\n".join(headings))):  # NFD would split KHÔNG at the accent
        if word.isascii():
            ambiguous = word.isalpha() and word.isupper()
            found |= {name for name in abbreviations_in(word)
                      if not ambiguous or ((name in known or word in known) and word not in PLAIN_LABEL_WORDS)
                      or not set(name) & VOWELS}
    return found


def store_vocabulary(lessons_dir: pathlib.Path, lesson_ids: Iterable[str]) -> frozenset[str]:
    """Every abbreviation the glossary of some lesson explains: what a word in a capitals-only label is known by."""
    known: set[str] = set()
    for lesson_id in lesson_ids:
        markdown = lessons_dir / lesson_id / "lesson.md"
        text = read_text(markdown)[0] if markdown.is_file() else None
        if text is not None and (glossary_lines := lesson_prose(text)[2]) is not None:
            known |= {abbreviation for abbreviation, _, _ in glossary_entries(glossary_lines)[0]}
    return frozenset(known)


def figure_strings(path: pathlib.Path) -> tuple[list[str], list[str]]:
    """What a reader (or a screen reader) takes from a figure: its <title>, <desc> and <text> strings, as (prose,
    headings).

    A string with no lower-case word is a heading set in capitals (ĐƠN HÀNG CÓ TIN MỚI, HAI MÁY · MỘT IPv4), in which
    a Vietnamese word such as TIN cannot be told from an abbreviation: only the mixed-case terms of a heading are read.
    A figure that cannot be parsed is reported elsewhere.
    """
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, LookupError, ElementTree.ParseError):
        return [], []
    prose: list[str] = []
    headings: list[str] = []
    for element in root.iter():
        if local_name(element.tag) in ("title", "desc", "text"):
            string = URL.sub(" ", " ".join(element.itertext()))  # <tspan>LLM</tspan><tspan>máy</tspan> is two words, not LLMmáy
            (prose if any(word.islower() and len(word) > 1 for word in re.findall(r"[^\W\d_]+", string)) else headings).append(string)
    return prose, headings


def lesson_prose(text: str) -> tuple[list[str], list[str], str | None, list[str], str]:
    """The visible words of a lesson, by section: (prose outside the glossary and the sources, prose inside the
    glossary with each bullet's lead-in removed, the glossary's lines or None, every "##" title in order, the
    text above the glossary heading, "" when there is no glossary).

    Code blocks, `code spans`, link destinations and the sources section are not prose a beginner has to decode.
    """
    tokens = markdown_tokens(text)  # a block token is followed by its inline children, which no branch below reads
    lines = text.split("\n")
    titles: list[str] = []
    starts: list[int] = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2" and token.map:
            titles.append(tokens[index + 1].content.strip())
            starts.append(token.map[0])
    glossary_lines = None
    above = ""
    if GLOSSARY_HEADING in titles:
        first = starts[titles.index(GLOSSARY_HEADING)]
        end = next((start for start in starts if start > first), len(lines))
        glossary_lines = lines[first + 1:end]
        above = "\n".join(lines[:first])
    body: list[str] = []
    glossary: list[str] = []
    section = ""
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2":
            section = tokens[index + 1].content.strip()
        elif token.type == "html_block" and section != SOURCES_HEADING:
            piece = html_text(token.content)
            (glossary if section == GLOSSARY_HEADING else body).append(piece)
        elif token.type == "inline" and section != SOURCES_HEADING:
            pieces = []
            in_autolink = False
            for child in token.children or []:
                if child.markup == "autolink" and child.type in ("link_open", "link_close"):
                    in_autolink = child.type == "link_open"  # <https://...> shows its destination as the link text
                    pieces.append(" ")
                elif in_autolink:
                    continue
                elif child.type == "text":
                    pieces.append(URL.sub(" ", child.content))
                elif child.type == "image":
                    pieces.append(" " + URL.sub(" ", child.content) + " ")
                elif child.type in ("softbreak", "hardbreak"):
                    pieces.append(" ")  # a wrapped line must not glue its last word to the next line's first
                elif child.type == "html_inline":
                    pieces.append(" " + html_text(child.content) + " ")
            piece = "".join(pieces)
            if section == GLOSSARY_HEADING:
                piece = piece.split("—", 1)[-1]  # the lead-in names what the bullet explains; the entry's full form is read apart
            (glossary if section == GLOSSARY_HEADING else body).append(piece)
    return body, glossary, glossary_lines, titles, above


def glossary_entries(lines: list[str]) -> tuple[list[tuple[str, str, str]], list[str]]:
    """The (abbreviation, full form, meaning) of each "- **X** (Full Form) — meaning" bullet, and the bullets that are
    not in that form. A bullet may run onto following lines until a blank line or the next bullet."""
    bullets: list[str] = []
    for line in lines:
        if line.startswith("- "):
            bullets.append(line.rstrip())
        elif line.strip() and bullets and not line.startswith(("#", "```", "~~~")):
            bullets[-1] += " " + line.strip()
        elif not line.strip():
            bullets.append("")  # a blank line ends the bullet it follows
    entries: list[tuple[str, str, str]] = []
    malformed: list[str] = []
    for bullet in bullets:
        if not bullet.startswith("- "):
            continue
        match = GLOSSARY_BULLET.match(bullet)
        if match:
            entries.append((match["abbreviation"], match["full"].strip(), match["meaning"].strip()))
        else:
            malformed.append(bullet)
    return entries, malformed


# Little words a full form may leave out of its abbreviation: "Request for Comments" gives RFC, "Network Address and
# Port Translation" NAPT and "HMAC-based Key Derivation Function" HKDF.
VOWELS = frozenset("AEIOUY")  # a word in capitals with none of them is no Vietnamese or English word
FILLER_WORDS = frozenset({"a", "an", "and", "based", "for", "in", "of", "on", "or", "the", "to", "with"})
# The digits of an abbreviation stand for number words: "Two-Factor Authentication" gives 2FA, "Triple Data Encryption
# Standard" 3DES. Only the words of the abbreviation's own number may be left out of its full form.
NUMBER_WORDS = {"1": ("one", "first", "single"), "2": ("two", "second", "double", "dual"), "3": ("three", "third", "triple"),
                "4": ("four", "fourth", "quad"), "5": ("five", "fifth"), "6": ("six", "sixth"), "7": ("seven", "seventh"),
                "8": ("eight", "eighth"), "9": ("nine", "ninth"), "10": ("ten", "tenth")}
# Every other number word. The full form of an abbreviation that begins with digits may hold no number word but its own:
# "Four Authentication" is not 2FA although F and A are its letters.
ALL_NUMBER_WORDS = frozenset(word for words in NUMBER_WORDS.values() for word in words) | frozenset((
    "zero eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy "
    "eighty ninety hundred thousand million billion eleventh twelfth thirteenth fourteenth fifteenth sixteenth seventeenth "
    "eighteenth nineteenth twentieth twice thrice half").split())


def spells(abbreviation: str, full_form: str) -> bool:
    """True when the initials of the full form's words are exactly the abbreviation's letters, in order: no word is
    left out, but the little words in FILLER_WORDS may be. The abbreviation written again does not spell itself.

    One initial per word and per camelCase hump (HyperText, JavaScript, REpresentational); an all-caps word gives its
    whole run or its first letter ("CSS Object Model" is CSSOM, "HTTP Strict Transport Security" is HSTS; a hidden
    run works the same: "SYNchronize"); a word that is the abbreviation itself gives its first letter (a recursive
    name: "gRPC Remote Procedure Calls"); digits are not letters, so the full form may leave a number out, but one it
    writes must be the abbreviation's own ("version 4" for IPv4, never "version 6"; an abbreviation with no digits takes
    none: "Application Programming Interface 6" is not API), and so are the number words that may
    be left out (NUMBER_WORDS: "Two-Factor" for 2FA, never "Triple"; where the digits come first the full form holds no
    other number word at all: "Four Authentication" is not 2FA although F and A are its letters, while a name such as
    "Double Data Rate" is fine for DDR4). A number the full form does write, as digits or as one of those words, stands
    where the abbreviation puts its digits: "Factor Two Authentication" and "Factor Authentication 2" are not 2FA, and
    "4 Internet Protocol version" is not IPv4; accents are dropped (cơ sở dữ liệu is CSDL).
    """
    if (UNIT_SYMBOLS | IRREGULAR_FORMS).get(abbreviation) == full_form.strip():
        return True
    numbers = re.findall(r"\d+", abbreviation)
    digits = re.findall(r"\d+", full_form)
    if digits and digits != numbers:
        return False  # "Internet Protocol version 6" is not IPv4, and no number is an API's: a number written is the abbreviation's own
    parts = ["#" if part.isdigit() else part.upper() for part in re.findall(r"[A-Za-z]|\d+", abbreviation)]
    groups = [index for index, part in enumerate(parts) if part == "#"]  # where the abbreviation puts its numbers
    if len(groups) > 8:
        return False
    number_words = {word for number in re.findall(r"\d+", abbreviation) for word in NUMBER_WORDS.get(number, ())}
    plain = unicodedata.normalize("NFD", full_form.replace("đ", "d").replace("Đ", "D"))
    plain = "".join(char for char in plain if not unicodedata.combining(char))
    leading = re.match(r"\d+", abbreviation)
    if leading:
        foreign = ALL_NUMBER_WORDS - set(NUMBER_WORDS.get(leading.group(), ()))
        if foreign & {word.lower() for word in re.findall(r"[A-Za-z]+", plain)}:
            return False  # the leading digits are a number word of their own: "Four Authentication" is not 2FA
    pattern = ""
    written = 0  # the numbers the full form writes: each stands as "#" where it is written
    for word in re.findall(r"[A-Za-z]+|\d+", plain):
        if word.isdigit():
            pattern += "#"
            written += 1
            continue
        if word == abbreviation:
            pattern += word[0].upper()
            continue
        for hump in re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z]*|[a-z]+", word):
            if hump.isupper() and len(hump) > 1:
                pattern += f"(?:{hump}|{hump[0]})"
            elif hump == word and hump.lower() in number_words:
                pattern += "#"
                written += 1
            elif hump == word and hump.lower() in FILLER_WORDS:
                pattern += f"(?:{hump[0].upper()})?"
            else:
                pattern += hump[0].upper()
    # The abbreviation keeps the numbers the full form writes, in the place it writes them, and drops the rest.
    return any(re.fullmatch(pattern, "".join(part for index, part in enumerate(parts) if part != "#" or index in kept))
               for kept in itertools.combinations(groups, written))


def figure_above(text: str, above: str, lesson_id: str) -> bool:
    """True when the lesson's own figure comes before the glossary heading. A Markdown image is looked for in the whole
    document, by the line it is on, because ![x][fig] takes its source from a definition that may come later (often at
    the end); a raw <img> needs no definition and is looked for in the text above the heading."""
    suffix = f"diagrams/{lesson_id}-main.svg"

    def is_figure(source: str) -> bool:  # the path the image check resolves: no #fragment, no ?query, percent-decoded
        return posixpath.normpath(relative_target(source) or "").endswith(suffix)

    if any(is_figure(source) for source in image_sources(above)):
        return True
    heading_line = above.count("\n") + 1
    return any(token.map and token.map[0] < heading_line
               and any(child.type == "image" and is_figure(child.attrGet("src") or "") for child in token.children or [])
               for token in markdown_tokens(text) if token.type == "inline")


def check_abbreviations(lesson_id: str, text: str, figure: list[str], headings: list[str] | tuple[str, ...] = (),
                        known: frozenset[str] = frozenset()) -> list[Problem]:
    """Every abbreviation the lesson or its figure uses is explained, in full, in the lesson's own glossary."""
    body, glossary, glossary_lines, titles, above = lesson_prose(text)
    used = abbreviations_in("\n".join(body + glossary + figure))
    labels = label_acronyms(headings, known)
    mixed = abbreviations_in("\n".join(headings), capitals=False)
    # a word with a vowel that only a figure label set in capitals gives, and only because another lesson explains it
    label_only = {name for name in labels - used - mixed if set(name) & VOWELS}
    used |= mixed | labels
    label_hint = " (it stands in a figure label set in capitals; if it is an ordinary word there, add it to PLAIN_LABEL_WORDS in scripts/sd101_check.py)"
    problems: list[Problem] = []
    template = f'"- **LLM** (Large Language Model) — meaning in plain words" under "## {GLOSSARY_HEADING}"'
    if glossary_lines is None:
        if used:
            problems.append(Problem(lesson_id, f"uses the abbreviation(s) {', '.join(sorted(used))} but has no "
                                               f'"## {GLOSSARY_HEADING}" section; add one bullet each, like {template}'
                                               + (f"; {', '.join(sorted(label_only))}{label_hint}" if label_only else "")))
        return problems
    if titles[0] != GLOSSARY_HEADING:
        problems.append(Problem(lesson_id, f'"## {GLOSSARY_HEADING}" must be the first "##" section, right after the '
                                           f"figure, but comes after {titles[0]!r}"))
    elif not figure_above(text, above, lesson_id):
        problems.append(Problem(lesson_id, f'"## {GLOSSARY_HEADING}" must come after the figure '
                                           f"diagrams/{lesson_id}-main.svg, not before it"))
    entries, malformed = glossary_entries(glossary_lines)
    problems.extend(Problem(lesson_id, f"glossary bullet {bullet[:70]!r} is not in the form {template}")
                    for bullet in malformed)
    inside: dict[str, str] = {}  # an abbreviation a full form holds (HMAC in HKDF's) -> the entry it stands in
    for abbreviation, full_form, _ in entries:
        for name in sorted(abbreviations_in(full_form)):
            inside.setdefault(name, abbreviation)
    elsewhere = set(used)
    used |= set(inside)
    seen: set[str] = set()
    for abbreviation, full_form, meaning in entries:
        if abbreviation in seen:
            problems.append(Problem(lesson_id, f"glossary explains {abbreviation} twice"))
        seen.add(abbreviation)
        if not spells(abbreviation, full_form):
            problems.append(Problem(lesson_id, f"glossary spells {abbreviation} out as {full_form!r}, whose initials "
                                               f"do not give exactly {abbreviation}; write the full form in Latin letters, with a capital "
                                               "where a word hides an initial (REpresentational, SYNchronize)"))
        if len(meaning.split()) < MIN_MEANING_WORDS:
            problems.append(Problem(lesson_id, f"glossary entry {abbreviation} has no explanation after the dash"))
    if not entries and not malformed:
        problems.append(Problem(lesson_id, f'"## {GLOSSARY_HEADING}" has no bullets'))
    problems.extend(Problem(lesson_id, f"uses the abbreviation {abbreviation} but the glossary does not explain it"
                                       + (f" (it stands in the full form of {inside[abbreviation]})"
                                          if abbreviation in inside and abbreviation not in elsewhere else "")
                                       + (label_hint if abbreviation in label_only and abbreviation not in inside else ""))
                    for abbreviation in sorted(used - seen))
    return problems


def check_readme(text: str, lesson_ids: set[str], entries: dict[str, dict]) -> list[Problem]:
    destinations = {destination: relative_target(destination) for destination in link_sequence(text)}
    linked = {posixpath.normpath(target) for target in destinations.values() if target}
    listed: list[str] = []
    for target in destinations.values():
        match = LESSON_LINK.fullmatch(posixpath.normpath(target)) if target else None
        if match and match.group(1) in lesson_ids and match.group(1) not in listed:
            listed.append(match.group(1))
    in_source_order = [lesson_id for lesson_id in entries if lesson_id in listed]
    problems = [Problem("README.md", f"does not link lessons/{lesson_id}/lesson.md")
                for lesson_id in sorted(lesson_ids) if f"lessons/{lesson_id}/lesson.md" not in linked]
    if listed != in_source_order:
        problems.append(Problem("README.md", "lists the lessons out of source order; the source map order is "
                                             + ", ".join(in_source_order)))
    if any(STATUS_WORD.search(cell) for cell in table_cells(text)):
        problems.append(Problem("README.md", "repeats a lesson status; it lives only in metadata/<id>.json"))
    return problems


def id_list_problems(name: str, value: object, written: list[str]) -> list[str]:
    if not isinstance(value, list):
        return [f"{name} must be a list of lesson ids"]
    return [f"{name} names {item}, which is not a written lesson" for item in value if item not in written]


def check_progress(path: pathlib.Path, entries: dict[str, dict], written: list[str]) -> list[Problem]:
    """progress.json coordinates the work; what it says about the store must agree with the store itself."""
    if not path.is_file():
        return [Problem("progress.json", "is missing")]
    data, error = read_json(path)
    if error:
        return [Problem("progress.json", error)]
    if not isinstance(data, dict):
        return [Problem("progress.json", "is not a JSON object")]
    reasons: list[str] = []
    if missing := sorted(PROGRESS_REQUIRED - set(data)):
        reasons.append(f"is missing {', '.join(missing)}")
    if data.get("language") != "vi":
        reasons.append("language must be 'vi'")
    if entries:
        for key, count in (("total_occurrences", len(entries)),
                           ("total_source_documents", len({e["source_path"] for e in entries.values() if isinstance(e.get("source_path"), str)}))):
            if data.get(key) != count or isinstance(data.get(key), bool):
                reasons.append(f"{key} is {data.get(key)!r}, but the source map has {count}")
    if "written_ids" in data and data["written_ids"] != written:
        reasons.append(f"written_ids is {data['written_ids']!r}, but the lessons on disk are {written!r} "
                       "(in source-map order)")
    for name in PROGRESS_ID_LISTS:
        if name in data:
            reasons.extend(id_list_problems(name, data[name], written))
    if entries and "next_id" in data:
        following = next((lesson_id for lesson_id in entries if lesson_id not in written), None)
        if data["next_id"] != following:
            reasons.append(f"next_id is {data['next_id']!r}, but the first source-map id not yet written is {following!r}")
    if "updated_on" in data and not valid_date(data["updated_on"]):
        reasons.append("updated_on must be a YYYY-MM-DD date")
    return [Problem("progress.json", reason) for reason in reasons]


def check_store(store: pathlib.Path, source_map: pathlib.Path, pin_roster: bool = False) -> list[Problem]:
    entries, pin, problems = load_source_map(source_map, pin_roster)
    boundary = repository_root(store)
    lessons_dir, metadata_dir, diagrams_dir = store / "lessons", store / "metadata", store / "diagrams"

    def listing(directory: pathlib.Path) -> list[pathlib.Path]:
        return sorted(directory.iterdir()) if directory.is_dir() else []

    lesson_ids = {path.name for path in listing(lessons_dir) if path.is_dir() and not path.is_symlink()}
    for path in listing(store):
        if path.name not in STORE_ENTRIES:
            problems.append(Problem(path.name, "is not allowed in the store, which holds only "
                                               f"{', '.join(sorted(STORE_ENTRIES))}"))
        elif path.is_symlink():
            problems.append(Problem(path.name, "is a symbolic link; the store holds real files and directories only"))
    for path in listing(lessons_dir):
        stem = path.stem
        if path.is_symlink() or not (path.is_dir() or (path.suffix == ".md" and stem in lesson_ids)):
            problems.append(Problem("lessons", f"{path.name} is not a lesson directory, or a .md pointer to one"))
        elif path.is_file():
            try:
                pointer_text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as error:
                problems.append(Problem("lessons", f"{path.name} cannot be read: {error}"))
                continue
            if f"{stem}/lesson.md" not in {posixpath.normpath(relative_target(d) or "") for d in link_destinations(pointer_text)}:
                problems.append(Problem("lessons", f"{path.name} is a pointer that does not link {stem}/lesson.md"))
    for path in listing(metadata_dir):
        if path.is_symlink() or not path.is_file() or path.suffix != ".json" or path.stem not in lesson_ids:
            problems.append(Problem("metadata", f"{path.name} is not the metadata of a lesson directory"))
    for path in listing(diagrams_dir):
        if path.is_symlink() or not path.is_file() or not path.name.endswith("-main.svg") \
                or path.name[:-len("-main.svg")] not in lesson_ids:
            problems.append(Problem("diagrams", f"{path.name} is not the <id>-main.svg figure of a lesson directory"))
        elif reason := svg_problem(path):
            problems.append(Problem("diagrams", f"{path.name} {reason}"))
    known = store_vocabulary(lessons_dir, lesson_ids)
    for lesson_id in sorted(lesson_ids):
        lesson_dir = lessons_dir / lesson_id
        markdown, pointer = lesson_dir / "lesson.md", lesson_dir / "lesson.yaml"
        for path in sorted(lesson_dir.iterdir()):
            if path.is_symlink():
                problems.append(Problem(lesson_id, f"{path.name} is a symbolic link; a lesson directory holds real files only"))
            elif path.name not in LESSON_FILES:
                problems.append(Problem(lesson_id, f"{path.name} is not allowed; a lesson directory holds only "
                                                   "lesson.md and lesson.yaml (figures live in diagrams/)"))
        for required in (markdown, pointer):
            if not required.is_file():
                problems.append(Problem(lesson_id, f"{required.name} is missing"))
        if pointer.is_file():
            try:
                parsed = yaml.load(pointer.read_text(encoding="utf-8"), Loader=StrictLoader)  # noqa: S506
            except (yaml.YAMLError, ValueError, OSError, RecursionError) as error:
                problems.append(Problem(lesson_id, f"lesson.yaml does not parse: {error}"))
            else:
                problems.extend(check_lesson_yaml(lesson_id, parsed))
        metadata_file = metadata_dir / f"{lesson_id}.json"
        if not metadata_file.is_file():
            problems.append(Problem(lesson_id, f"metadata/{lesson_id}.json is missing"))
        else:
            parsed, error = read_json(metadata_file)
            problems.extend([Problem(f"metadata/{lesson_id}.json", error)] if error
                            else check_metadata(lesson_id, parsed, entries, pin))
        if not (diagrams_dir / f"{lesson_id}-main.svg").is_file():
            problems.append(Problem(lesson_id, f"diagrams/{lesson_id}-main.svg is missing"))
        if markdown.is_file():
            text, why = read_text(markdown)
            if why:
                problems.append(Problem(lesson_id, f"lesson.md {why}"))
            else:
                problems.extend(check_markdown(lesson_id, text, lesson_dir, entries, lesson_ids, boundary, diagrams_dir))
                problems.extend(check_abbreviations(lesson_id, text, *figure_strings(diagrams_dir / f"{lesson_id}-main.svg"), known=known))
    for name in STORE_PAGES:
        page = store / name
        if not page.is_file():
            if name == "README.md":
                problems.append(Problem(name, "is missing"))
            elif page.exists():
                problems.append(Problem(name, "is not a file"))
            continue
        text, why = read_text(page)
        if why:
            problems.append(Problem(name, why))
            continue
        problems.extend(check_page(name, text, store, boundary))
        if name == "README.md":
            problems.extend(check_readme(text, lesson_ids, entries))
    written = [lesson_id for lesson_id in entries if lesson_id in lesson_ids]
    problems.extend(check_progress(store / "progress.json", entries, written))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--store", type=pathlib.Path, default=DEFAULT_STORE)
    parser.add_argument("--source-map", type=pathlib.Path, default=DEFAULT_SOURCE_MAP)
    arguments = parser.parse_args(argv)
    pin_roster = arguments.source_map.resolve() == DEFAULT_SOURCE_MAP.resolve()
    problems = check_store(arguments.store, arguments.source_map, pin_roster)
    for problem in problems:
        print(problem)
    lessons_dir = arguments.store / "lessons"
    count = sum(1 for path in lessons_dir.iterdir() if path.is_dir()) if lessons_dir.is_dir() else 0
    print(f"sd101_check: {count} lesson(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
