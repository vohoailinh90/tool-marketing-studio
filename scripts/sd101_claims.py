#!/usr/bin/env python3
"""Claim registry for the System Design lessons: which session is writing which lesson.

Several Claude sessions write lessons of `system-design-101/vi/` at the same time, each in its own
container and on its own branch. `progress.json` names one `next_id`, so two sessions that start together
both take it. This registry, `system-design-101/vi/claims.jsonl`, is the one place that says, for every one
of the 404 source-map positions, whether it is free (`todo`), being written (`doing`, with the branch that
holds it) or handed over (`written`). A session reads it before it starts, claims before it writes, and
marks the lesson written when it is done. It is a script, not a convention, per `deterministic_work` in
agent-routing/policy.yaml.

The file is JSON Lines: a header line, then one line per lesson in source-map order, so two sessions that
claim different lessons merge without a conflict and two that claim the same one always conflict. Its
`written` is not metadata's `content_status: done`: it says a lesson was written and handed over, and
whether it was reviewed stays in `metadata/<id>.json`.

A claim only helps if the other sessions can see it, and sessions share nothing but the remote. So every
command that decides something fetches all branches of the remote first and reads the registry on each:

  origin/main            every entry counts
  any other branch B     only the entries whose owner is B (a copy inherited from main is not B's claim)
  this working tree      the entries it owns, and every written lesson

When the remote cannot be read, `claim` and `verify` stop (exit 2) instead of guessing; `--offline` says
you accept that. A `doing` claim whose heartbeat is older than the header's `lease_hours` is stale: it no
longer blocks anyone, but it is taken over only on purpose (`claim --take-stale`), and the taker's entry
records `taken_from` so the old owner cannot win it back by touching its heartbeat.

Two claims written within seconds of each other, each before the other was pushed, can both exist. That is
the one race a registry without a compare-and-swap cannot close, so it is narrowed and then caught:
`claim --publish` commits and pushes the claim and verifies it in one step, `verify`, `touch` and `finish`
repeat the check, `sd101_check.py` fails a branch whose registry is not consistent with its lessons, and
two branches that wrote the same lesson conflict at merge. The cost of losing the race is wasted work, not
a duplicate lesson on main.

Usage:
    python3 scripts/sd101_claims.py status                 # counts per group, who is doing what
    python3 scripts/sd101_claims.py next --group sd-14     # lessons nobody has taken
    python3 scripts/sd101_claims.py claim --next 3 --publish
    python3 scripts/sd101_claims.py claim sd-14-016 sd-14-017 --publish
    python3 scripts/sd101_claims.py verify                 # still the winner of every claim of mine?
    python3 scripts/sd101_claims.py touch --publish        # renew the heartbeat of my claims
    python3 scripts/sd101_claims.py finish sd-14-016 --pr 80   # commit it together with the lesson
    python3 scripts/sd101_claims.py release sd-14-017 --publish
    python3 scripts/sd101_claims.py sync                   # create the file, or add new source-map ids
Exit status: 0 done, 1 refused (or a claim lost), 2 the repository, the remote or the file could not be read.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STORE = ROOT / "system-design-101" / "vi"
DEFAULT_SOURCE_MAP = ROOT / "brainstorm" / "system-design-101-vi" / "source-map.json"
REGISTRY_NAME = "claims.jsonl"
SCHEMA_VERSION = 1
DEFAULT_LEASE_HOURS = 72
MAX_LEASE_HOURS = 720
STATUSES = ("todo", "doing", "written")
KEY_ORDER = ("id", "status", "title", "owner", "session", "taken_from", "claimed_at", "heartbeat_at", "done_at", "pr")
HEADER_KEYS = ("schema_version", "lease_hours", "source_repository", "source_commit_sha")
FIELDS_BY_STATUS = {
    "todo": set(),
    "doing": {"owner", "session", "taken_from", "claimed_at", "heartbeat_at"},
    "written": {"owner", "session", "done_at", "pr"},
}
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
LESSON_ID = re.compile(r"sd-\d{2}-\d{3}")
PUSH_BACKOFF_SECONDS = (2, 4, 8, 16)
GIT_TIMEOUT_SECONDS = 120


class ClaimsError(Exception):
    """The repository, the remote or the registry could not be read (exit status 2)."""


# --------------------------------------------------------------------------------------------- time

def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def stamp(moment: datetime.datetime) -> str:
    return moment.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_stamp(value: object) -> datetime.datetime | None:
    if not isinstance(value, str) or not STAMP.fullmatch(value):
        return None
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


# --------------------------------------------------------------------------------- the file's format

def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    seen: dict[str, object] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"the key {key!r} appears twice")
        seen[key] = value
    return seen


def render_line(record: dict, order: tuple[str, ...]) -> str:
    unknown = sorted(set(record) - set(order))
    if unknown:
        raise ValueError(f"unknown key(s) {', '.join(unknown)}")
    return json.dumps({key: record[key] for key in order if key in record}, ensure_ascii=False)


def render(header: dict, lessons: dict[str, dict]) -> str:
    """The canonical text of the registry: one line per record, so git merges and conflicts per lesson."""
    return "\n".join([render_line(header, HEADER_KEYS), *(render_line(lessons[key], KEY_ORDER) for key in lessons)]) + "\n"


def parse(text: str) -> tuple[dict, dict[str, dict], list[str]]:
    """The header, the lesson records by id and the reasons the text is not a registry."""
    problems: list[str] = []
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    records: list[tuple[int, dict]] = []
    for number, line in enumerate(lines, start=1):
        try:
            record = json.loads(line, object_pairs_hook=_no_duplicate_keys)
        except (ValueError, RecursionError) as error:
            problems.append(f"line {number} is not a JSON object: {error}")
            continue
        if not isinstance(record, dict):
            problems.append(f"line {number} is not a JSON object")
            continue
        records.append((number, record))
    header: dict = {}
    if records and records[0][0] == 1:
        header = records.pop(0)[1]
    elif lines:
        problems.append("line 1 (the header) is missing")
    lessons: dict[str, dict] = {}
    for number, record in records:
        lesson_id = record.get("id")
        if not isinstance(lesson_id, str):
            problems.append(f"line {number} has no id")
        elif lesson_id in lessons:
            problems.append(f"line {number}: {lesson_id} appears twice")
        else:
            lessons[lesson_id] = record
    return header, lessons, problems


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def entry_problems(entry: dict) -> list[str]:
    """What is wrong with one lesson record, apart from how it relates to other lessons or to the disk."""
    status = entry.get("status")
    if status not in STATUSES:
        return [f"status must be one of {', '.join(STATUSES)}"]
    problems = [f"{key} is not allowed when the status is {status}"
                for key in entry if key not in {"id", "status", "title"} | FIELDS_BY_STATUS[status]]
    if status == "doing":
        problems += [f"{key} is required when the status is doing" for key in ("owner", "claimed_at", "heartbeat_at")
                     if key not in entry]
    for key in ("owner", "session", "taken_from"):
        if key in entry and not _text(entry[key]):
            problems.append(f"{key} must be text")
    for key in ("claimed_at", "heartbeat_at", "done_at"):
        if key in entry and parse_stamp(entry[key]) is None:
            problems.append(f"{key} must be a UTC time like 2026-10-15T08:30:00Z")
    claimed, beat = parse_stamp(entry.get("claimed_at")), parse_stamp(entry.get("heartbeat_at"))
    if claimed and beat and beat < claimed:
        problems.append("heartbeat_at is before claimed_at")
    if "pr" in entry and (not isinstance(entry["pr"], int) or isinstance(entry["pr"], bool) or entry["pr"] < 1):
        problems.append("pr must be a pull request number")
    return problems


def registry_problems(text: str, expected: list[tuple[str, str]], pin_commit: str | None,
                      on_disk: set[str]) -> list[str]:
    """Every reason `text` is not the registry of `expected` (source-map id, title) pairs for the lessons `on_disk`."""
    header, lessons, problems = parse(text)
    if header.get("schema_version") != SCHEMA_VERSION or isinstance(header.get("schema_version"), bool):
        problems.append(f"the header's schema_version must be {SCHEMA_VERSION}")
    lease = header.get("lease_hours")
    if not isinstance(lease, int) or isinstance(lease, bool) or not 1 <= lease <= MAX_LEASE_HOURS:
        problems.append(f"the header's lease_hours must be a whole number from 1 to {MAX_LEASE_HOURS}")
    if pin_commit is not None and header.get("source_commit_sha") != pin_commit:
        problems.append(f"the header's source_commit_sha is {header.get('source_commit_sha')!r}, "
                        f"but the source map pins {pin_commit}")
    if set(header) - set(HEADER_KEYS):
        problems.append(f"the header has unknown key(s) {', '.join(sorted(set(header) - set(HEADER_KEYS)))}")
    ids = [lesson_id for lesson_id, _ in expected]
    if missing := [lesson_id for lesson_id in ids if lesson_id not in lessons]:
        problems.append(f"lacks {len(missing)} source-map lesson(s), e.g. {missing[0]} (run sd101_claims.py sync)")
    if extra := [lesson_id for lesson_id in lessons if lesson_id not in set(ids)]:
        problems.append(f"lists {len(extra)} id(s) the source map does not have, e.g. {extra[0]}")
    if not missing and not extra and list(lessons) != ids:
        problems.append("lists the lessons out of source-map order (run sd101_claims.py fmt)")
    titles = dict(expected)
    for lesson_id, entry in lessons.items():
        if lesson_id in titles and entry.get("title") != titles[lesson_id]:
            problems.append(f"{lesson_id}: title is {entry.get('title')!r}, but the source map has {titles[lesson_id]!r}")
        problems += [f"{lesson_id}: {reason}" for reason in entry_problems(entry)]
        status = entry.get("status")
        if status == "written" and lesson_id not in on_disk:
            problems.append(f"{lesson_id}: is written, but lessons/{lesson_id}/ does not exist")
        elif status == "todo" and lesson_id in on_disk:
            problems.append(f"{lesson_id}: lessons/{lesson_id}/ exists, but the registry says todo "
                            "(claim it, then finish it)")
    if not problems:
        try:
            if render(header, lessons) != text:
                problems.append("is not in canonical form (run sd101_claims.py fmt)")
        except ValueError as error:
            problems.append(str(error))
    return problems


# ------------------------------------------------------------------------------------- the source map

@dataclass(frozen=True)
class Source:
    lessons: tuple[tuple[str, str], ...]            # (id, title_source) in source order
    groups: dict[str, str]                          # sd-NN -> title_source
    partners: dict[str, tuple[str, ...]]            # id -> ids that share its source file
    repository: str
    commit_sha: str


def load_source(path: pathlib.Path) -> Source:
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)
        lessons, groups, partners = [], {}, {}
        for category in data["categories"]:
            groups[category["id"]] = category.get("title_source") or category["id"]
            for entry in category["lessons"]:
                lessons.append((entry["id"], entry.get("title_source") or entry["id"]))
                if entry.get("same_source_as"):
                    partners[entry["id"]] = tuple(entry["same_source_as"])
        return Source(tuple(lessons), groups, partners, str(data.get("source_repository", "")),
                      str(data.get("source_commit_sha", "")))
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as error:
        raise ClaimsError(f"cannot read the source map {path}: {error}") from error


# ------------------------------------------------------------------------------------------------ git

def git(root: pathlib.Path, *args: str, check: bool = True, data: bytes | None = None) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(["git", *args], cwd=root, input=data, capture_output=True, timeout=GIT_TIMEOUT_SECONDS,
                                check=False)
    except (OSError, subprocess.SubprocessError) as error:
        raise ClaimsError(f"git {' '.join(args[:2])} could not run: {error}") from error
    if check and result.returncode != 0:
        raise ClaimsError(f"git {' '.join(args[:2])} failed: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result


def git_text(root: pathlib.Path, *args: str) -> str:
    return git(root, *args).stdout.decode("utf-8", "replace").strip()


def current_branch(root: pathlib.Path) -> str | None:
    result = git(root, "symbolic-ref", "--short", "-q", "HEAD", check=False)
    return result.stdout.decode().strip() or None


def default_branch(root: pathlib.Path, remote: str) -> str:
    head = git(root, "symbolic-ref", "--short", "-q", f"refs/remotes/{remote}/HEAD", check=False).stdout.decode().strip()
    if head.startswith(f"{remote}/"):
        return head[len(remote) + 1:]
    for candidate in ("main", "master"):
        if git(root, "rev-parse", "--verify", "-q", f"refs/remotes/{remote}/{candidate}", check=False).returncode == 0:
            return candidate
    return "main"


def fetch_remote(root: pathlib.Path, remote: str) -> None:
    """Every branch of the remote, so another session's claim is visible; stale tracking refs are pruned."""
    git(root, "fetch", "--quiet", "--prune", remote, f"+refs/heads/*:refs/remotes/{remote}/*")


def remote_registries(root: pathlib.Path, remote: str, relative: str) -> tuple[dict[str, str], list[str]]:
    """branch -> registry text for every remote branch that has one, and the branches whose file is missing."""
    names = [name for name in git_text(root, "for-each-ref", "--format=%(refname:lstrip=3)",
                                       f"refs/remotes/{remote}").splitlines() if name and name != "HEAD"]
    if not names:
        return {}, []
    request = "".join(f"refs/remotes/{remote}/{name}:{relative}\n" for name in names).encode()
    output = git(root, "cat-file", "--batch", data=request).stdout
    found: dict[str, str] = {}
    position = 0
    for name in names:
        end = output.index(b"\n", position)
        fields = output[position:end].split(b" ")
        position = end + 1
        if len(fields) == 3 and fields[1] == b"blob":
            size = int(fields[2])
            found[name] = output[position:position + size].decode("utf-8", "replace")
            position += size + 1
    return found, [name for name in names if name not in found]


# -------------------------------------------------------------------------------------------- the world

@dataclass(frozen=True)
class Holding:
    lesson_id: str
    status: str                       # doing | written
    owner: str | None
    claimed_at: str | None
    heartbeat_at: str | None
    taken_from: str | None
    where: str

    def who(self) -> str:
        return self.owner or "an earlier import"


def _holding(entry: dict, where: str) -> Holding | None:
    if entry.get("status") not in ("doing", "written") or not isinstance(entry.get("id"), str):
        return None
    pick = lambda key: entry[key] if isinstance(entry.get(key), str) else None  # noqa: E731
    return Holding(entry["id"], entry["status"], pick("owner"), pick("claimed_at"), pick("heartbeat_at"),
                   pick("taken_from"), where)


def is_stale(holding: Holding, now: datetime.datetime, lease_hours: int) -> bool:
    beat = parse_stamp(holding.heartbeat_at) or parse_stamp(holding.claimed_at)
    return beat is None or now - beat > datetime.timedelta(hours=lease_hours)


def beats(first: Holding, second: Holding) -> bool:
    """Which of two live claims on one lesson wins: a takeover, else the earlier claim, else the smaller owner."""
    if first.taken_from and first.taken_from == second.owner:
        return True
    if second.taken_from and second.taken_from == first.owner:
        return False
    return (first.claimed_at or "", first.owner or "") < (second.claimed_at or "", second.owner or "")


def gather(local: dict[str, dict], remote: dict[str, str], base: str, me: str, offline: bool,
           everything: bool = False) -> tuple[dict[str, list[Holding]], list[str]]:
    """Every claim and every written lesson that any view shows, per lesson, and the views that could not be read."""
    found: dict[str, list[Holding]] = {}
    unreadable: list[str] = []

    def add(entry: dict, where: str) -> None:
        if (holding := _holding(entry, where)) is not None:
            found.setdefault(holding.lesson_id, []).append(holding)

    for entry in local.values():
        if offline or everything or entry.get("owner") == me or entry.get("status") == "written":
            add(entry, "this working tree")
    for branch, text in remote.items():
        _, lessons, problems = parse(text)
        if problems:
            unreadable.append(branch)
        for entry in lessons.values():
            if branch == base or entry.get("owner") == branch:
                add(entry, f"origin/{branch}")
    return found, unreadable


def refusal(lesson_id: str, found: dict[str, list[Holding]], source: Source, me: str, now: datetime.datetime,
            lease: int, take_stale: bool, allow_same_source: bool) -> tuple[str | None, str | None]:
    """Why `me` may not claim the lesson (None when it may), and the stale owner the claim would take it from."""
    taken: Holding | None = None
    for holding in found.get(lesson_id, []):
        if holding.owner == me and holding.status == "doing":
            continue
        if holding.status == "written":
            return f"already written by {holding.who()} ({holding.where})", None
        if not is_stale(holding, now, lease):
            return f"claimed by {holding.owner} since {holding.claimed_at} ({holding.where})", None
        if not take_stale:
            return (f"claimed by {holding.owner}, but its last heartbeat was {holding.heartbeat_at or holding.claimed_at} "
                    f"({holding.where}), more than {lease} hours ago; if that session is gone, claim with --take-stale"), None
        if taken is None or (holding.claimed_at or "") > (taken.claimed_at or ""):
            taken = holding
    if not allow_same_source:
        for partner in source.partners.get(lesson_id, ()):
            for holding in found.get(partner, []):
                if holding.status == "doing" and holding.owner != me and not is_stale(holding, now, lease):
                    return (f"shares its source file with {partner}, which {holding.owner} is writing "
                            f"({holding.where}); ask that session to cover both, or pass --allow-same-source"), None
    return None, taken.owner if taken else None


def lost_reason(mine: Holding, found: dict[str, list[Holding]], me: str, now: datetime.datetime, lease: int) -> str | None:
    """Why `me` does not hold `mine` any more, or None when it is the winner."""
    for other in found.get(mine.lesson_id, []):
        if other.owner == me and other.status == "doing":
            continue
        if other.status == "written":
            if other.owner == me:
                continue
            return f"already written by {other.who()} ({other.where})"
        if not is_stale(other, now, lease) and beats(other, mine):
            return f"lost to {other.owner}, who claimed it at {other.claimed_at} ({other.where})"
    return None


# --------------------------------------------------------------------------------------------- context

@dataclass
class Context:
    root: pathlib.Path
    store: pathlib.Path
    source: Source
    me: str
    session: str | None
    remote: str
    offline: bool
    now: datetime.datetime
    branch: str | None = None
    owner_given: bool = False

    @property
    def path(self) -> pathlib.Path:
        return self.store / REGISTRY_NAME

    @property
    def relative(self) -> str:
        return self.path.resolve().relative_to(self.root.resolve()).as_posix()

    def on_disk(self) -> set[str]:
        lessons = self.store / "lessons"
        return {path.name for path in lessons.iterdir() if path.is_dir()} if lessons.is_dir() else set()


def new_header(source: Source, lease: int = DEFAULT_LEASE_HOURS) -> dict:
    return {"schema_version": SCHEMA_VERSION, "lease_hours": lease, "source_repository": source.repository,
            "source_commit_sha": source.commit_sha}


def load_registry(context: Context) -> tuple[dict, dict[str, dict]]:
    try:
        text = context.path.read_text(encoding="utf-8")
    except OSError as error:
        raise ClaimsError(f"cannot read {context.path}: {error} (run sd101_claims.py sync to create it)") from error
    header, lessons, problems = parse(text)
    if problems:
        raise ClaimsError(f"{context.path.name} is not readable: {problems[0]}")
    return header, lessons


def write_registry(context: Context, header: dict, lessons: dict[str, dict]) -> None:
    ordered = {lesson_id: lessons[lesson_id] for lesson_id, _ in context.source.lessons if lesson_id in lessons}
    ordered.update({key: value for key, value in lessons.items() if key not in ordered})
    temporary = context.path.with_name(context.path.name + ".tmp")
    context.path.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(render(header, ordered), encoding="utf-8")
    os.replace(temporary, context.path)


def lease_of(header: dict) -> int:
    lease = header.get("lease_hours")
    return lease if isinstance(lease, int) and not isinstance(lease, bool) and lease > 0 else DEFAULT_LEASE_HOURS


def world_of(context: Context, local: dict[str, dict], everything: bool = False) -> tuple[dict[str, list[Holding]], list[str]]:
    """What every session can see, after reading the remote (a failure to read it is an error unless offline)."""
    remote: dict[str, str] = {}
    base = "main"
    if not context.offline:
        try:
            fetch_remote(context.root, context.remote)
            base = default_branch(context.root, context.remote)
            remote, _ = remote_registries(context.root, context.remote, context.relative)
        except ClaimsError as error:
            raise ClaimsError(f"cannot read the other sessions' claims from {context.remote}: {error}; "
                              "nothing was decided (pass --offline only if you accept that risk)") from error
    return gather(local, remote, base, context.me, context.offline, everything)


# ------------------------------------------------------------------------------------------- commands

def effective_status(lesson_id: str, found: dict[str, list[Holding]], now: datetime.datetime, lease: int) -> str:
    holdings = found.get(lesson_id, [])
    if any(h.status == "written" for h in holdings):
        return "written"
    live = [h for h in holdings if not is_stale(h, now, lease)]
    if live:
        return "doing"
    return "stale" if holdings else "todo"


def cmd_sync(context: Context, _: argparse.Namespace) -> int:
    on_disk = context.on_disk()
    if context.path.is_file():
        header, lessons = load_registry(context)
    else:
        header, lessons = new_header(context.source), {}
    added = 0
    for lesson_id, title in context.source.lessons:
        if lesson_id not in lessons:
            lessons[lesson_id] = {"id": lesson_id, "status": "written" if lesson_id in on_disk else "todo", "title": title}
            added += 1
    known = {lesson_id for lesson_id, _ in context.source.lessons}
    extra = [lesson_id for lesson_id in lessons if lesson_id not in known]
    write_registry(context, header, lessons)
    print(f"sync: {context.relative} has {len(lessons)} lesson(s), {added} added")
    if extra:
        print(f"sync: {len(extra)} id(s) are not in the source map and were kept: {', '.join(extra[:5])}", file=sys.stderr)
    return 0


def cmd_fmt(context: Context, _: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    write_registry(context, header, lessons)
    print(f"fmt: {context.relative} rewritten in canonical form")
    return 0


def cmd_status(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    lease = lease_of(header)
    found, unreadable = world_of(context, lessons, everything=True)
    states = {lesson_id: effective_status(lesson_id, found, context.now, lease) for lesson_id, _ in context.source.lessons}
    counts = {name: list(states.values()).count(name) for name in ("written", "doing", "stale", "todo")}
    print(f"System Design 101 (vi): {len(states)} lessons, source {context.source.commit_sha[:7]}")
    print(f"written {counts['written']} | doing {counts['doing']} | stale {counts['stale']} | todo {counts['todo']}")
    print(f"{'group':<7}{'written':>8}{'doing':>7}{'stale':>7}{'todo':>6}  title")
    for group, title in context.source.groups.items():
        mine = [state for lesson_id, state in states.items() if lesson_id.startswith(group + "-")]
        print(f"{group:<7}{mine.count('written'):>8}{mine.count('doing'):>7}{mine.count('stale'):>7}{mine.count('todo'):>6}  {title}")
    active = [(lesson_id, h) for lesson_id, _ in context.source.lessons for h in found.get(lesson_id, []) if h.status == "doing"]
    if active:
        print("\nBeing written:")
    for lesson_id, h in active:
        age = context.now - (parse_stamp(h.heartbeat_at) or context.now)
        flag = " STALE" if is_stale(h, context.now, lease) else ""
        print(f"  {lesson_id}  {h.owner}  claimed {h.claimed_at}, heartbeat {int(age.total_seconds() // 3600)}h ago "
              f"({h.where}){flag}")
    free = free_lessons(context, found, lease, args.group, 5)
    print("\nNext free: " + (", ".join(free) if free else "none"))
    if unreadable:
        print(f"warning: the registry on {len(unreadable)} branch(es) could not be read: {', '.join(unreadable[:3])}",
              file=sys.stderr)
    return 0


def free_lessons(context: Context, found: dict[str, list[Holding]], lease: int, group: str | None, count: int,
                 take_stale: bool = False, allow_same_source: bool = False) -> list[str]:
    chosen: list[str] = []
    for lesson_id, _ in context.source.lessons:
        if len(chosen) >= count:
            break
        if group and not lesson_id.startswith(group + "-"):
            continue
        if any(h.status == "written" or h.owner == context.me for h in found.get(lesson_id, [])):
            continue
        if refusal(lesson_id, found, context.source, context.me, context.now, lease, take_stale, allow_same_source)[0] is None:
            chosen.append(lesson_id)
    return chosen


def cmd_next(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    found, _ = world_of(context, lessons)
    free = free_lessons(context, found, lease_of(header), args.group, args.count)
    print("\n".join(free) if free else "none")
    return 0 if free else 1


def require_owner(context: Context) -> None:
    if context.branch in (None, "main", "master") and not context.owner_given:
        raise ClaimsError("claims belong to a work branch; check one out first (or pass --owner)")


def publish(context: Context, message: str) -> None:
    """Commit only the registry and push it to the same-named branch, so the other sessions can see it."""
    if context.branch in (None, "main", "master"):
        raise ClaimsError("--publish pushes the current work branch; it never pushes main")
    git(context.root, "add", "--", context.relative)
    if git(context.root, "diff", "--cached", "--quiet", "--", context.relative, check=False).returncode == 0:
        return
    git(context.root, "commit", "--quiet", "--only", "-m", message, "--", context.relative)
    for delay in (0, *PUSH_BACKOFF_SECONDS):
        time.sleep(delay)
        pushed = git(context.root, "push", "--quiet", "-u", context.remote, f"HEAD:refs/heads/{context.branch}", check=False)
        if pushed.returncode == 0:
            return
    raise ClaimsError(f"the push failed: {pushed.stderr.decode('utf-8', 'replace').strip()}")


def my_claims(lessons: dict[str, dict], me: str, ids: list[str] | None) -> list[str]:
    owned = [lesson_id for lesson_id, entry in lessons.items() if entry.get("status") == "doing" and entry.get("owner") == me]
    return [lesson_id for lesson_id in owned if not ids or lesson_id in ids]


def check_ids(context: Context, lessons: dict[str, dict], ids: list[str]) -> None:
    known = {lesson_id for lesson_id, _ in context.source.lessons}
    for lesson_id in ids:
        if not LESSON_ID.fullmatch(lesson_id) or lesson_id not in known or lesson_id not in lessons:
            raise ClaimsError(f"{lesson_id} is not a lesson of the source map (or of the registry; run sync)")


def verdicts(context: Context, header: dict, lessons: dict[str, dict], ids: list[str]) -> dict[str, str | None]:
    found, _ = world_of(context, lessons)
    lease = lease_of(header)
    out: dict[str, str | None] = {}
    for lesson_id in ids:
        mine = _holding(lessons[lesson_id], "this working tree")
        out[lesson_id] = lost_reason(mine, found, context.me, context.now, lease) if mine else "is not claimed by you"
    return out


def cmd_claim(context: Context, args: argparse.Namespace) -> int:
    require_owner(context)
    header, lessons = load_registry(context)
    lease = lease_of(header)
    found, _ = world_of(context, lessons)
    ids = list(args.ids)
    if args.count:
        ids += free_lessons(context, found, lease, args.group, args.count, args.take_stale, args.allow_same_source)
    if not ids:
        print("claim: no free lesson to claim", file=sys.stderr)
        return 1
    check_ids(context, lessons, ids)
    refused, takes = [], {}
    for lesson_id in ids:
        reason, taken = refusal(lesson_id, found, context.source, context.me, context.now, lease, args.take_stale,
                                args.allow_same_source)
        if reason:
            refused.append(f"{lesson_id}: {reason}")
        elif taken:
            takes[lesson_id] = taken
    if refused:
        print("claim refused, nothing was written:\n  " + "\n  ".join(refused), file=sys.stderr)
        return 1
    for lesson_id in ids:
        entry = lessons[lesson_id]
        if entry.get("status") == "doing" and entry.get("owner") == context.me:
            entry["heartbeat_at"] = stamp(context.now)
            continue
        fresh = {"id": lesson_id, "status": "doing", "title": entry.get("title", ""), "owner": context.me,
                 "claimed_at": stamp(context.now), "heartbeat_at": stamp(context.now)}
        if context.session:
            fresh["session"] = context.session
        if lesson_id in takes:
            fresh["taken_from"] = takes[lesson_id]
        lessons[lesson_id] = fresh
    write_registry(context, header, lessons)
    print(f"claimed {', '.join(ids)} as {context.me}")
    message = args.message or f"System Design vi: claim {', '.join(ids)}"
    if not args.publish:
        print("Other sessions cannot see this claim yet. Publish it now, then confirm it:\n"
              f"  git add {context.relative} && git commit -m {json.dumps(message)} && git push -u {context.remote} {context.branch}\n"
              "  python3 scripts/sd101_claims.py verify")
        return 0
    publish(context, message)
    return report_verdicts(verdicts(context, header, lessons, ids), context)


def report_verdicts(results: dict[str, str | None], context: Context) -> int:
    lost = {lesson_id: reason for lesson_id, reason in results.items() if reason}
    for lesson_id, reason in results.items():
        if reason is None:
            print(f"  {lesson_id}: yours")
        else:
            print(f"  {lesson_id}: {reason}", file=sys.stderr)
    if lost:
        print(f"Stop work on {', '.join(lost)} and release it: python3 scripts/sd101_claims.py release "
              f"{' '.join(lost)} --publish", file=sys.stderr)
        return 1
    return 0


def cmd_verify(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    ids = my_claims(lessons, context.me, args.ids)
    if not ids:
        print(f"verify: {context.me} has no claim in progress")
        return 0
    return report_verdicts(verdicts(context, header, lessons, ids), context)


def cmd_touch(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    ids = my_claims(lessons, context.me, args.ids)
    if not ids:
        print(f"touch: {context.me} has no claim in progress")
        return 0
    results = verdicts(context, header, lessons, ids)
    for lesson_id in ids:
        if results[lesson_id] is None:
            lessons[lesson_id]["heartbeat_at"] = stamp(context.now)
    write_registry(context, header, lessons)
    if args.publish:
        publish(context, args.message or f"System Design vi: heartbeat for {', '.join(ids)}")
    return report_verdicts(results, context)


def cmd_finish(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    check_ids(context, lessons, args.ids)
    problems = []
    for lesson_id in args.ids:
        entry = lessons[lesson_id]
        if entry.get("status") != "doing" or entry.get("owner") != context.me:
            problems.append(f"{lesson_id}: is not claimed by {context.me} (claim it first)")
        elif not (context.store / "lessons" / lesson_id / "lesson.md").is_file():
            problems.append(f"{lesson_id}: lessons/{lesson_id}/lesson.md does not exist yet")
    if problems:
        print("finish refused, nothing was written:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    results = verdicts(context, header, lessons, args.ids)
    if any(results.values()):
        return report_verdicts(results, context)
    for lesson_id in args.ids:
        entry = {"id": lesson_id, "status": "written", "title": lessons[lesson_id].get("title", ""), "owner": context.me,
                 "done_at": stamp(context.now)}
        if context.session:
            entry["session"] = context.session
        if args.pr:
            entry["pr"] = args.pr
        lessons[lesson_id] = entry
    write_registry(context, header, lessons)
    print(f"written: {', '.join(args.ids)}. Commit {context.relative} together with the lesson files.")
    return 0


def cmd_release(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    check_ids(context, lessons, args.ids)
    problems = []
    for lesson_id in args.ids:
        entry = lessons[lesson_id]
        if entry.get("status") != "doing" or entry.get("owner") != context.me:
            problems.append(f"{lesson_id}: is not a claim of {context.me}")
        elif lesson_id in context.on_disk():
            problems.append(f"{lesson_id}: lessons/{lesson_id}/ still exists; remove the draft first, or finish the lesson")
    if problems:
        print("release refused, nothing was written:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    for lesson_id in args.ids:
        lessons[lesson_id] = {"id": lesson_id, "status": "todo", "title": lessons[lesson_id].get("title", "")}
    write_registry(context, header, lessons)
    print(f"released {', '.join(args.ids)}")
    if args.publish:
        publish(context, args.message or f"System Design vi: release {', '.join(args.ids)}")
    return 0


# ---------------------------------------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--store", type=pathlib.Path, default=DEFAULT_STORE)
    parser.add_argument("--source-map", type=pathlib.Path, default=DEFAULT_SOURCE_MAP)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--owner", help="who holds the claims; default is the current branch")
    parser.add_argument("--session", default=os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID"))
    parser.add_argument("--offline", action="store_true", help="decide from this working tree alone")
    commands = parser.add_subparsers(dest="command", required=True)

    def add(name: str, handler, help_text: str) -> argparse.ArgumentParser:
        sub = commands.add_parser(name, help=help_text)
        sub.set_defaults(handler=handler)
        return sub

    add("sync", cmd_sync, "create the registry, or add source-map ids it lacks")
    add("fmt", cmd_fmt, "rewrite the registry in canonical form")
    status = add("status", cmd_status, "counts per group and who is writing what")
    status.add_argument("--group")
    following = add("next", cmd_next, "lessons nobody has taken")
    following.add_argument("--group")
    following.add_argument("-n", "--count", type=int, default=1)
    claim = add("claim", cmd_claim, "take lessons before writing them")
    claim.add_argument("ids", nargs="*")
    claim.add_argument("--next", dest="count", type=int, default=0, help="also take the first N free lessons")
    claim.add_argument("--group")
    claim.add_argument("--take-stale", action="store_true")
    claim.add_argument("--allow-same-source", action="store_true")
    claim.add_argument("--publish", action="store_true", help="commit and push the claim, then verify it")
    claim.add_argument("--message")
    verify = add("verify", cmd_verify, "am I still the winner of my claims?")
    verify.add_argument("ids", nargs="*")
    touch = add("touch", cmd_touch, "renew the heartbeat of my claims")
    touch.add_argument("ids", nargs="*")
    touch.add_argument("--publish", action="store_true")
    touch.add_argument("--message")
    finish = add("finish", cmd_finish, "mark my claimed lessons written")
    finish.add_argument("ids", nargs="+")
    finish.add_argument("--pr", type=int)
    release = add("release", cmd_release, "give claimed lessons back")
    release.add_argument("ids", nargs="+")
    release.add_argument("--publish", action="store_true")
    release.add_argument("--message")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        store = args.store.resolve()
        root = pathlib.Path(git_text(store if store.is_dir() else store.parent, "rev-parse", "--show-toplevel"))
        branch = current_branch(root)
        me = args.owner or branch
        if not me:
            raise ClaimsError("HEAD is detached; check out a work branch or pass --owner")
        context = Context(root, store, load_source(args.source_map), me, args.session, args.remote, args.offline, utcnow(),
                          branch, bool(args.owner))
        return args.handler(context, args)
    except ClaimsError as error:
        print(f"sd101_claims: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
