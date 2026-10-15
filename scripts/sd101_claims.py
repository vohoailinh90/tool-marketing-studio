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
import contextlib
import datetime
import importlib.util
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STORE = ROOT / "system-design-101" / "vi"
DEFAULT_SOURCE_MAP = ROOT / "brainstorm" / "system-design-101-vi" / "source-map.json"
REGISTRY_NAME = "claims.jsonl"
SCHEMA_VERSION = 1
DEFAULT_LEASE_HOURS = 72
CLOCK_SKEW_HOURS = 1  # a heartbeat further ahead of the observing clock than this is not proof of life
STATUSES = ("todo", "doing", "written")
KEY_ORDER = ("id", "status", "title", "owner", "session", "taken_from", "generation", "shared_source", "claimed_at",
             "heartbeat_at", "done_at", "pr")
HEADER_KEYS = ("schema_version", "lease_hours", "source_repository", "source_commit_sha")
FIELDS_BY_STATUS = {
    "todo": set(),
    "doing": {"owner", "session", "taken_from", "generation", "shared_source", "claimed_at", "heartbeat_at"},
    "written": {"owner", "session", "done_at", "pr", "shared_source"},
}
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
LESSON_ID = re.compile(r"sd-\d{2}-\d{3}")
PUSH_BACKOFF_SECONDS = (2, 4, 8, 16)
GIT_TIMEOUT_SECONDS = 120


class ClaimsError(Exception):
    """The repository, the remote or the registry could not be read (exit status 2)."""


class Refusal(Exception):
    """The command asked for something the registry does not allow (exit status 1)."""


LOCAL = "this working tree"
UNPUBLISHED = "your claim is not on "


# --------------------------------------------------------------------------------------------- time

def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def renewal(entry: dict, now: datetime.datetime) -> str:
    """A renewed heartbeat, never earlier than the claim itself: a clock corrected backwards would otherwise write a
    record the loader refuses."""
    claimed = parse_stamp(entry.get("claimed_at"))
    return stamp(max(now, claimed) if claimed else now)


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
    """The canonical text of the registry: one line per record with a blank line between records.

    Git treats two changes on adjacent lines as one conflict, and sessions that claim the next free lessons
    change adjacent records, so an unchanged blank line sits between every two records.
    """
    return "\n\n".join([render_line(header, HEADER_KEYS), *(render_line(lessons[key], KEY_ORDER) for key in lessons)]) + "\n"


def parse(text: str) -> tuple[dict, dict[str, dict], list[str]]:
    """The header, the lesson records by id and the reasons the text is not a registry."""
    problems: list[str] = []
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    records: list[tuple[int, dict]] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
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


def _count(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


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
    for key in ("owner", "session"):
        if key in entry and not _text(entry[key]):
            problems.append(f"{key} must be text")
    if "shared_source" in entry and entry["shared_source"] is not True:
        problems.append("shared_source must be true when present")
    if "taken_from" in entry and not (isinstance(entry["taken_from"], list) and entry["taken_from"]
                                      and all(_text(owner) for owner in entry["taken_from"])):
        problems.append("taken_from must be a list of the owners whose stale claim was taken over")
    if "generation" in entry and not _count(entry["generation"]):
        problems.append("generation must be a whole number, 1 or more: the takeovers this claim stands on")
    for key in ("claimed_at", "heartbeat_at", "done_at"):
        if key in entry and parse_stamp(entry[key]) is None:
            problems.append(f"{key} must be a UTC time like 2026-10-15T08:30:00Z")
    claimed, beat = parse_stamp(entry.get("claimed_at")), parse_stamp(entry.get("heartbeat_at"))
    if claimed and beat and beat < claimed:
        problems.append("heartbeat_at is before claimed_at")
    if "pr" in entry and (not isinstance(entry["pr"], int) or isinstance(entry["pr"], bool) or entry["pr"] < 1):
        problems.append("pr must be a pull request number")
    return problems


def record_problems(lessons: dict[str, dict]) -> list[str]:
    """Every reason a record of a parsed registry is not a valid claim record, as `<id>: <reason>`."""
    return [f"{lesson_id}: {reason}" for lesson_id, entry in lessons.items() for reason in entry_problems(entry)]


def header_problems(header: dict, pin_commit: str | None, pin_repository: str | None) -> list[str]:
    """Every reason the header line is not the one the source map calls for."""
    problems = []
    if header.get("schema_version") != SCHEMA_VERSION or isinstance(header.get("schema_version"), bool):
        problems.append(f"the header's schema_version must be {SCHEMA_VERSION}")
    lease = header.get("lease_hours")
    if not isinstance(lease, int) or isinstance(lease, bool) or lease != DEFAULT_LEASE_HOURS:
        # one lease for every registry: two branches with different leases would disagree about who is stale
        problems.append(f"the header's lease_hours must be {DEFAULT_LEASE_HOURS}")
    if pin_repository is not None and header.get("source_repository") != pin_repository:
        problems.append(f"the header's source_repository is {header.get('source_repository')!r}, "
                        f"but the source map is of {pin_repository}")
    if pin_commit is not None and header.get("source_commit_sha") != pin_commit:
        problems.append(f"the header's source_commit_sha is {header.get('source_commit_sha')!r}, "
                        f"but the source map pins {pin_commit}")
    if set(header) - set(HEADER_KEYS):
        problems.append(f"the header has unknown key(s) {', '.join(sorted(set(header) - set(HEADER_KEYS)))}")
    return problems


def registry_problems(text: str, expected: list[tuple[str, str]], pin_commit: str | None,
                      on_disk: set[str], pin_repository: str | None = None) -> list[str]:
    """Every reason `text` is not the registry of `expected` (source-map id, title) pairs for the lessons `on_disk`."""
    header, lessons, problems = parse(text)
    problems += header_problems(header, pin_commit, pin_repository)
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


def default_branch(root: pathlib.Path, remote: str, ask: bool = True) -> str:
    """The branch the remote calls its default. The remote is asked: the local origin/HEAD is written once, at clone
    time, and goes stale when the default branch is renamed, which would make the real one look like a feature branch."""
    for line in (git(root, "ls-remote", "--symref", remote, "HEAD").stdout.decode("utf-8", "replace").splitlines()
                 if ask else []):
        if line.startswith("ref: refs/heads/") and "\t" in line:
            return line[len("ref: refs/heads/"):].split("\t", 1)[0]
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


def remote_registries(root: pathlib.Path, remote: str, relative: str) -> tuple[dict[str, str], list[str], list[str]]:
    """branch -> registry text for every remote branch that has one, the branches whose file is missing, and the
    branches whose file is not valid UTF-8 (decoded strictly: a replaced byte could turn an owner into another name)."""
    names = [name for name in git_text(root, "for-each-ref", "--format=%(refname:lstrip=3)",
                                       f"refs/remotes/{remote}").splitlines() if name and name != "HEAD"]
    if not names:
        return {}, [], []
    request = "".join(f"refs/remotes/{remote}/{name}:{relative}\n" for name in names).encode()
    output = git(root, "cat-file", "--batch", data=request).stdout
    found: dict[str, str] = {}
    undecodable: list[str] = []
    position = 0
    try:
        for name in names:
            end = output.index(b"\n", position)
            fields = output[position:end].split(b" ")
            position = end + 1
            if len(fields) == 3:  # <oid> <type> <size>, then the content; a tree or a symlink is skipped, not read
                size = int(fields[2])
                if fields[1] == b"blob":
                    try:
                        found[name] = output[position:position + size].decode("utf-8")
                    except UnicodeDecodeError:
                        undecodable.append(name)
                position += size + 1
    except ValueError as error:
        raise ClaimsError(f"git cat-file printed something unexpected: {error}") from error
    return found, [name for name in names if name not in found and name not in undecodable], undecodable


# -------------------------------------------------------------------------------------------- the world

@dataclass(frozen=True)
class Holding:
    lesson_id: str
    status: str                       # doing | written
    owner: str | None
    claimed_at: str | None
    heartbeat_at: str | None
    taken_from: tuple[str, ...]
    where: str
    shared: bool = False              # claimed with --allow-same-source: the owner knowingly shares a source file
    generation: int = 0               # takeovers behind the claim: counts them where a clock could misorder them

    def who(self) -> str:
        return self.owner or "an earlier import"


def _holding(entry: dict, where: str) -> Holding | None:
    if entry.get("status") not in ("doing", "written") or not isinstance(entry.get("id"), str):
        return None
    pick = lambda key: entry[key] if isinstance(entry.get(key), str) else None  # noqa: E731
    taken = entry.get("taken_from")
    superseded = tuple(owner for owner in taken if isinstance(owner, str)) if isinstance(taken, list) else ()
    return Holding(entry["id"], entry["status"], pick("owner"), pick("claimed_at"), pick("heartbeat_at"), superseded, where,
                   entry.get("shared_source") is True, entry["generation"] if _count(entry.get("generation")) else 0)


def is_stale(holding: Holding, now: datetime.datetime, lease_hours: int) -> bool:
    beat = parse_stamp(holding.heartbeat_at) or parse_stamp(holding.claimed_at)
    if beat is None or beat - now > datetime.timedelta(hours=CLOCK_SKEW_HOURS):  # dated from the future: a clock gone wrong
        return True  # would otherwise block the lesson for as long as it is ahead, plus the whole lease
    return now - beat > datetime.timedelta(hours=lease_hours)


def beats(first: Holding, second: Holding) -> bool:
    """Which of two live claims on one lesson wins: a takeover, else the earlier claim, else the smaller owner.

    Two sessions can each have taken the lesson over from the other, one after the other; the later takeover stands.
    It is the higher generation (each takeover counts one more than the claim it supersedes), never the later clock
    time: a session whose clock ran ahead would otherwise outrank the takeover that legitimately replaced it.
    """
    first_took, second_took = second.owner in first.taken_from, first.owner in second.taken_from
    if first_took and second_took:
        return ((first.generation, first.claimed_at or "", first.owner or "")
                > (second.generation, second.claimed_at or "", second.owner or ""))
    if first_took:
        return True
    if second_took:
        return False
    return (first.claimed_at or "", first.owner or "") < (second.claimed_at or "", second.owner or "")


def gather(local: dict[str, dict], remote: dict[str, str], base: str, me: str, offline: bool,
           roster: tuple[str, ...] = (), expected: tuple[str | None, str | None] | None = None,
           sources: dict[str, Source] | None = None) -> tuple[dict[str, list[Holding]], list[str]]:
    """Every claim and every written lesson that any view shows, per lesson, and the views that could not be read."""
    found: dict[str, list[Holding]] = {}
    unreadable: list[str] = []

    def add(entry: dict, where: str) -> None:
        if (holding := _holding(entry, where)) is not None:
            found.setdefault(holding.lesson_id, []).append(holding)

    for entry in local.values():
        if offline or entry.get("owner") == me or entry.get("status") == "written":
            add(entry, LOCAL)
    for branch, text in remote.items():
        header, lessons, problems = parse(text)
        want, ids = expected, roster
        if sources and branch in sources:
            # A repin or a new lesson is published from one branch while the others still have the old pin and roster:
            # each registry is judged against the source map its own branch holds.
            own = sources[branch]
            want, ids = (own.commit_sha, own.repository), tuple(lesson_id for lesson_id, _ in own.lessons)
        if want is not None:  # a header of another schema or source says the records cannot be read as ours
            problems += header_problems(header, *want)
        problems += record_problems(lessons)  # a typo in a status would otherwise hide the claim it sits in
        if missing := [lesson_id for lesson_id in ids if lesson_id not in lessons]:  # so would a truncated file
            problems.append(f"lacks {len(missing)} source-map lesson(s), e.g. {missing[0]}")
        elif extra := [lesson_id for lesson_id in lessons if lesson_id not in ids]:  # and a row its own map dropped
            problems.append(f"holds {len(extra)} lesson(s) its source map does not list, e.g. {extra[0]}")
        if problems:
            unreadable.append(f"origin/{branch} ({problems[0]})")
            continue  # --ignore-unreadable decides without the branch, so none of its records may count
        for entry in lessons.values():
            if branch == base or entry.get("owner") == branch:
                add(entry, f"origin/{branch}")
    return found, unreadable


def refusal(lesson_id: str, found: dict[str, list[Holding]], source: Source, me: str, now: datetime.datetime,
            lease: int, take_stale: bool, allow_same_source: bool) -> tuple[str | None, list[str]]:
    """Why `me` may not claim the lesson (None when it may), and every owner whose stale claim it would take over."""
    taken: list[str] = []
    for holding in found.get(lesson_id, []):
        if holding.owner == me and holding.status == "doing":
            continue
        if holding.status == "written":
            return f"already written by {holding.who()} ({holding.where})", []
        if not is_stale(holding, now, lease):
            return f"claimed by {holding.owner} since {holding.claimed_at} ({holding.where})", []
        if not take_stale:
            return (f"claimed by {holding.owner}, but its last heartbeat was {holding.heartbeat_at or holding.claimed_at} "
                    f"({holding.where}), more than {lease} hours ago; if that session is gone, claim with --take-stale"), []
        # The whole chain, so a session that took the lesson over from a session that had itself taken it over
        # still beats the first owner when that one wakes up and renews its heartbeat.
        taken += [owner for owner in (holding.owner, *holding.taken_from) if owner and owner != me and owner not in taken]
    if not allow_same_source:
        for partner in source.partners.get(lesson_id, ()):
            for holding in found.get(partner, []):
                if holding.status == "written" and holding.owner != me and not holding.shared:  # finished, by someone else or before the registry
                    return (f"shares its source file with {partner}, which {holding.who()} already wrote "
                            f"({holding.where}); pass --allow-same-source only if the two lessons are meant to differ"), []
                if holding.status == "doing" and holding.owner != me and not holding.shared and not is_stale(holding, now, lease):
                    return (f"shares its source file with {partner}, which {holding.owner} is writing "
                            f"({holding.where}); ask that session to cover both, or pass --allow-same-source"), []
    return None, taken


def lost_reason(mine: Holding, found: dict[str, list[Holding]], me: str, now: datetime.datetime, lease: int,
                partners: tuple[str, ...] = (), published_live: bool = True) -> str | None:
    """Why `me` does not hold `mine` any more, or None when it is the winner.

    `partners` are the lessons that share this one's source file. Two sessions that claimed the two halves of a pair
    before either push was visible hold claims on different ids, so the same precedence decides between them, unless
    one of them took its half on purpose (--allow-same-source). A takeover of the same id is recorded in
    `taken_from`; one across a pair is not, so a claim that has no live published copy (expired in public, or never
    pushed) gives way to a live partner claim, whoever claimed first.
    """
    for other in found.get(mine.lesson_id, []):
        if other.owner == me and other.status == "doing":
            continue
        if other.status == "written":  # whoever wrote it: a stale container's own claim is just as finished
            return f"already written by {other.who()} ({other.where})"
        # An expired claim, or one with no live published copy (its branch was deleted, or it never went up), loses to
        # a live one whatever their order: the live claimant may never have seen it, so it could not record the
        # takeover in `taken_from`, and a heartbeat renewed only locally proves nothing to the others.
        if not is_stale(other, now, lease) and (is_stale(mine, now, lease) or not published_live or beats(other, mine)):
            return f"lost to {other.owner}, who claimed it at {other.claimed_at} ({other.where})"
    for partner in partners:
        for other in found.get(partner, []):
            if other.status == "written" and other.owner != me and not mine.shared and not other.shared:  # finished: nothing to wait for
                return (f"shares its source file with {partner}, which {other.who()} has written ({other.where}); "
                        "release it, or keep it on purpose by claiming it again with --allow-same-source")
            if other.status != "doing" or other.owner == me or mine.shared or other.shared or is_stale(other, now, lease):
                continue
            if not published_live or is_stale(mine, now, lease) or beats(other, mine):
                return (f"shares its source file with {partner}, which {other.owner} holds ({other.where}); "
                        "release it, or keep it on purpose by claiming it again with --allow-same-source")
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
    ignore_unreadable: bool = False
    source_map: pathlib.Path | None = None

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


def load_registry(context: Context, complete: bool = True) -> tuple[dict, dict[str, dict]]:
    """The local registry, refused when it is damaged. Unless `complete` is off (sync and fmt, which repair it), a file
    that lags the source map (a truncated roster, another pin) is refused too: a command that wrote and pushed it
    would publish a registry every other session then has to stop for."""
    try:
        text = context.path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ClaimsError(f"cannot read {context.path}: {error} (run sd101_claims.py sync to create it)") from error
    header, lessons, problems = parse(text)
    problems += record_problems(lessons)
    if complete and not problems:
        problems += header_problems(header, context.source.commit_sha, context.source.repository)
        if missing := [lesson_id for lesson_id, _ in context.source.lessons if lesson_id not in lessons]:
            problems.append(f"lacks {len(missing)} source-map lesson(s), e.g. {missing[0]}")
        elif extra := [lesson_id for lesson_id in lessons if lesson_id not in dict(context.source.lessons)]:
            problems.append(f"holds {len(extra)} lesson(s) the source map no longer lists, e.g. {extra[0]}")
        elif stale := [lesson_id for lesson_id, title in context.source.lessons if lessons[lesson_id].get("title") != title]:
            problems.append(f"{len(stale)} title(s) differ from the source map, e.g. {stale[0]}")
        if problems:
            problems[0] += "; sd101_claims.py sync repairs a registry that lags the source map"
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


def world_of(context: Context, local: dict[str, dict],
             tolerate: bool = False) -> tuple[dict[str, list[Holding]], list[str]]:
    """What every session can see, after reading the remote (a failure to read it is an error unless offline).

    A registry on a branch that cannot be parsed may hide a claim, so it stops the decision as well, unless the
    caller only reports (`tolerate`) or was told to go on without it (--ignore-unreadable).
    """
    remote: dict[str, str] = {}
    undecodable: list[str] = []
    missing: list[str] = []
    base = "main"
    if not context.offline:
        try:
            fetch_remote(context.root, context.remote)
            base = default_branch(context.root, context.remote)
            remote, missing, undecodable = remote_registries(context.root, context.remote, context.relative)
        except ClaimsError as error:
            raise ClaimsError(f"cannot read the other sessions' claims from {context.remote}: {error}; "
                              "nothing was decided (pass --offline only if you accept that risk)") from error
    roster = tuple(lesson_id for lesson_id, _ in context.source.lessons)
    found, unreadable = gather(local, remote, base, context.me, context.offline, roster,
                               (context.source.commit_sha, context.source.repository),
                               {} if context.offline else {name: own for name in remote if (
                                   own := source_at(context, f"refs/remotes/{context.remote}/{name}")) is not None})
    unreadable += [f"{context.remote}/{name} (not valid UTF-8)" for name in undecodable]
    gone = not context.offline and base not in remote and base not in missing and base not in undecodable
    if base in missing or gone:  # a legacy feature branch may lack the file, the branch that holds every merged lesson may not
        absent = (f"{context.remote}/{base} (the default branch does not exist on the remote)" if gone
                  else f"{context.remote}/{base} (the default branch has no {REGISTRY_NAME})")
        if not tolerate:  # not even --ignore-unreadable decides without the records of every merged lesson
            raise ClaimsError(f"{absent}; nothing was decided (--ignore-unreadable does not cover the default branch)")
        unreadable.append(absent)
    if (core := [item for item in unreadable if item.startswith((f"origin/{base} (", f"{context.remote}/{base} ("))]) and not tolerate:
        raise ClaimsError(f"the default branch's registry cannot be used ({core[0]}); nothing was decided "
                          "(--ignore-unreadable does not cover the default branch)")
    if unreadable and not tolerate and not context.ignore_unreadable:
        raise ClaimsError(f"the registry on {len(unreadable)} branch(es) cannot be parsed, e.g. {unreadable[0]}; "
                          "a claim in it could be missed, so nothing was decided. Fix or delete that branch, "
                          "or pass --ignore-unreadable to decide without it")
    return found, unreadable


# ------------------------------------------------------------------------------------------- commands

def effective_status(lesson_id: str, found: dict[str, list[Holding]], now: datetime.datetime, lease: int) -> str:
    holdings = found.get(lesson_id, [])
    if any(h.status == "written" for h in holdings):
        return "written"
    live = [h for h in holdings if not is_stale(h, now, lease)]
    if live:
        return "doing"
    return "stale" if holdings else "todo"


def imported_problems(context: Context, ids: list[str]) -> list[str]:
    """Why lessons that sync would record as written cannot be: their four files must exist and the store checker must
    accept them, or the remote would advertise a terminal lesson the others cannot touch and the store cannot check."""
    cache: dict = {}
    out = []
    for lesson_id in ids:
        if missing := missing_artifacts(context, lesson_id):
            out.append(f"{lesson_id}: " + "; ".join(f"{path} does not exist yet (or is a symbolic link)" for path in missing))
        elif broken := content_problems(context.store, context.source_map, lesson_id, cache):
            out.append(f"{lesson_id}: the store checker rejects the lesson: " + "; ".join(broken))
    return out


def cmd_sync(context: Context, _: argparse.Namespace) -> int:
    on_disk = context.on_disk()
    if context.path.is_file():
        header, lessons = load_registry(context, complete=False)
        # A repinned or retitled source map: the registry follows it, keeping every status and claim. The header is
        # rebuilt whole (an empty file has none, a damaged one a wrong schema or lease), never patched.
        header = new_header(context.source)
    else:
        header, lessons = new_header(context.source), {}
    added = retitled = 0
    imported: list[str] = []
    adopted: list[str] = []
    bootstrap = on_default_branch(context, strict=False)  # the registry is born on the default branch, ownerless
    for lesson_id, title in context.source.lessons:
        # A lesson that arrived on disk without the registry hearing of it (a merge of the default branch brings the
        # lessons other sessions finished) is imported as written, whether its row is new or still says todo.
        arrived = lesson_id in on_disk and (lesson_id not in lessons or lessons[lesson_id].get("status") == "todo")
        if lesson_id not in lessons or arrived:
            fresh = lesson_id not in lessons
            lessons[lesson_id] = {"id": lesson_id, "status": "written" if lesson_id in on_disk else "todo", "title": title}
            if lesson_id in on_disk:
                imported.append(lesson_id)
            if lesson_id in on_disk and not bootstrap:
                # Imported on a work branch: other sessions count a record on a non-default branch only when its owner is
                # that branch, so an ownerless one would be invisible to them until it is merged.
                lessons[lesson_id].update(owner=context.me, done_at=stamp(context.now))
            added += fresh
        elif lessons[lesson_id].get("title") != title:
            lessons[lesson_id]["title"] = title
            retitled += 1
    clashes: list[str] = []
    if not bootstrap:
        # A lesson merged from another work branch keeps that branch as its owner, and a record on a non-default branch
        # counts only for its own owner: if the other branch is deleted the lesson would vanish for everybody. Until the
        # default branch holds the record, the branch that now carries the lesson's files answers for it.
        try:
            merged = registry_at(context, f"refs/remotes/{context.remote}/{default_branch(context.root, context.remote, ask=not context.offline)}")
        except ClaimsError:
            merged = {}
        for lesson_id, entry in lessons.items():
            if (entry.get("status") == "written" and entry.get("owner") not in (None, context.me) and lesson_id in on_disk
                    and merged.get(lesson_id) != entry):
                for partner in context.source.partners.get(lesson_id, ()):
                    mine = lessons.get(partner, {})
                    if (mine.get("owner") == context.me and mine.get("status") in ("doing", "written")
                            and not mine.get("shared_source") and not entry.get("shared_source")):
                        clashes.append(f"{lesson_id} (written by {entry.get('owner')}) shares its source file with {partner}, which {context.me} holds")
                entry["owner"] = context.me
                adopted.append(lesson_id)
                imported.append(lesson_id)  # the same file and content checks as for any lesson that becomes written here
    if clashes:
        raise Refusal("sync refused, nothing was written: adopting would hide a shared-source conflict:\n  "
                      + "\n  ".join(clashes) + "\nrelease that half, or claim it again with --allow-same-source, first")
    if broken := imported_problems(context, imported):
        raise Refusal("sync refused, nothing was written: a lesson that is on disk cannot be imported as written yet:\n  "
                      + "\n  ".join(broken))
    known = {lesson_id for lesson_id, _ in context.source.lessons}
    listing = git(context.root, "ls-tree", "-r", "--name-only", "HEAD", "--",
                  context.store.resolve().relative_to(context.root.resolve()).as_posix(), check=False)
    committed = set(listing.stdout.decode("utf-8", "replace").splitlines()) if listing.returncode == 0 else set()  # no commit yet
    if orphans := [lesson_id for lesson_id in lessons if lesson_id not in known and (any(
            (context.store / path).exists() or (context.store / path).is_symlink() for path in (
                f"lessons/{lesson_id}", f"lessons/{lesson_id}.md", f"metadata/{lesson_id}.json", f"diagrams/{lesson_id}-main.svg"))
            or any(re.search(rf"/(lessons|metadata|diagrams)/{lesson_id}[./-]", f"/{name}") for name in committed))]:
        raise Refusal(f"sync refused, nothing was written: the source map no longer lists {', '.join(orphans)}, but its lesson "
                      "files are still in the store; remove them (or restore the source-map entry) first")
    gone = {lesson_id: lessons.pop(lesson_id) for lesson_id in [i for i in lessons if i not in known]}
    write_registry(context, header, lessons)
    print(f"sync: {context.relative} has {len(lessons)} lesson(s), {added} added, {retitled} retitled, {len(gone)} dropped")
    if adopted:
        print(f"sync: {', '.join(adopted)} came from another work branch and now belong to {context.me}", file=sys.stderr)
    if held := [f"{lesson_id} ({entry.get('status')})" for lesson_id, entry in gone.items() if entry.get("status") != "todo"]:
        print(f"sync: dropped lessons the source map no longer lists that were not todo: {', '.join(held)}; "
              "git history keeps their records", file=sys.stderr)
    return 0


def cmd_fmt(context: Context, _: argparse.Namespace) -> int:
    header, lessons = load_registry(context, complete=False)
    write_registry(context, header, lessons)
    print(f"fmt: {context.relative} rewritten in canonical form")
    return 0


def cmd_status(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    lease = lease_of(header)
    found, unreadable = world_of(context, lessons, tolerate=True)
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
        print(f"warning: the registry on {len(unreadable)} branch(es) could not be parsed: {'; '.join(unreadable[:3])}",
              file=sys.stderr)
    return 0


def removed_upstream(context: Context) -> set[str]:
    """Lessons the default branch dropped from its source map after this branch was cut: a checkout that still has the
    old map would otherwise take, write and publish a lesson the roster no longer holds. A lesson added on this branch
    (it was never in the map at the fork point) is not one of them."""
    if context.offline or source_map_in_checkout(context) is None:
        return set()
    try:
        base_ref = f"refs/remotes/{context.remote}/{default_branch(context.root, context.remote)}"
    except ClaimsError:
        return set()
    forked = git(context.root, "merge-base", "HEAD", base_ref, check=False)
    current, then = source_at(context, base_ref), (source_at(context, forked.stdout.decode().strip()) if forked.returncode == 0 else None)
    if current is None or then is None:
        return set()
    return {lesson_id for lesson_id, _ in then.lessons} - {lesson_id for lesson_id, _ in current.lessons}


def free_lessons(context: Context, found: dict[str, list[Holding]], lease: int, group: str | None, count: int,
                 take_stale: bool = False, allow_same_source: bool = False, exclude: tuple[str, ...] = ()) -> list[str]:
    exclude = (*exclude, *removed_upstream(context))
    chosen: list[str] = []
    for lesson_id, _ in context.source.lessons:
        if len(chosen) >= count:
            break
        if lesson_id in exclude or (group and not lesson_id.startswith(group + "-")):
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


def on_default_branch(context: Context, strict: bool) -> bool:
    """Whether the checked-out branch is the one the remote calls its default (main and master always count). With
    `strict` a remote that cannot be asked is an error; without it the cached refs decide, and the read that follows
    reports the broken remote in its own words."""
    if context.branch is None or context.branch in ("main", "master"):
        return True
    try:
        return context.branch == default_branch(context.root, context.remote, ask=not context.offline)
    except ClaimsError:
        if strict:
            raise
        return context.branch == default_branch(context.root, context.remote, ask=False)


def require_owner(context: Context) -> None:
    if not context.owner_given and on_default_branch(context, strict=False):
        raise ClaimsError("claims belong to a work branch; check one out first (or pass --owner)")


def check_publishable(context: Context) -> None:
    """--publish is only for the owner's own work branch: a claim counts on the branch its owner names."""
    if context.branch is None:
        raise ClaimsError("--publish pushes the current work branch, but HEAD is detached")
    if on_default_branch(context, strict=True):
        raise ClaimsError(f"--publish pushes the current work branch; it never pushes {context.branch}, the default branch")
    if context.me != context.branch:
        raise ClaimsError(f"--publish pushes branch {context.branch}, but the claims are owned by {context.me}; "
                          "other sessions count a claim only on the branch its owner names, so publish from that branch")


def lesson_files(context: Context, lesson_id: str) -> list[str]:
    """Everything a written lesson consists of, relative to the repository root."""
    store = context.store.resolve().relative_to(context.root.resolve())
    return [(store / "lessons" / lesson_id).as_posix(), (store / "lessons" / f"{lesson_id}.md").as_posix(),
            (store / "metadata" / f"{lesson_id}.json").as_posix(), (store / "diagrams" / f"{lesson_id}-main.svg").as_posix()]


def regular_in_head(root: pathlib.Path, path: str) -> bool:
    """Whether HEAD holds `path` as a regular file: a symbolic link or a directory exists as an object but is rejected
    by the store checker, which `git cat-file -e` would not tell."""
    entry = git_text(root, "ls-tree", "HEAD", "--", path).split(None, 1)
    return bool(entry) and entry[0] in ("100644", "100755")


def registry_at(context: Context, ref: str) -> dict[str, dict]:
    """The lesson records the registry holds at `ref` (a remote-tracking ref), empty when there is none."""
    shown = git(context.root, "show", f"{ref}:{context.relative}", check=False)
    return parse(shown.stdout.decode("utf-8", "replace"))[1] if shown.returncode == 0 else {}


def unfinished_commits(context: Context, lessons: dict[str, dict]) -> tuple[list[str], list[str], list[str]]:
    with contextlib.ExitStack() as stack:  # the exported tree lives as long as the judgement does
        return _unfinished_commits(context, lessons, stack)


def _unfinished_commits(context: Context, lessons: dict[str, dict], stack: contextlib.ExitStack
                        ) -> tuple[list[str], list[str], list[str]]:
    """Lessons that --publish would advertise as written without their files: a record that turned `written` since
    the pushed branch and whose lesson is absent from HEAD or changed after the last commit. Only the registry is committed by
    --publish, so such a lesson would be terminal for every other session while the pushed branch lacks it (or holds
    an older draft). A record the pushed branch already advertises was judged when it went up, and is left alone; one that is merely
    committed locally has not been, so a registry-only commit does not vouch for it."""
    ref = f"refs/remotes/{context.remote}/{context.branch}"
    head = registry_at(context, ref)
    # A branch cut from the default branch inherits its written lessons: those are advertised there already, so a branch
    # that was never pushed does not answer for all of them (the first publication would check the whole store per lesson).
    base_ref = f"refs/remotes/{context.remote}/{default_branch(context.root, context.remote, ask=False)}"
    inherited = registry_at(context, base_ref)
    out = []
    cache: dict = {}
    tree: list[tuple[pathlib.Path, pathlib.Path]] = []

    def exported() -> tuple[pathlib.Path, pathlib.Path]:
        if not tree:
            tree.append(stack.enter_context(pushed_tree(context)))
        return tree[0]

    def pushed_content_problems(_: Context, lesson_id: str) -> list[str]:
        return content_problems(exported()[0], context.source_map, lesson_id, cache, exported()[1])

    for lesson_id, entry in lessons.items():
        if entry.get("status") != "written":
            continue
        files = lesson_files(context, lesson_id)
        required = [f"{files[0]}/lesson.md", f"{files[0]}/lesson.yaml", files[2], files[3]]  # what the store checker requires
        if head.get(lesson_id) == entry or (lesson_id not in head and inherited.get(lesson_id) == entry):
            # already advertised, on the pushed branch or on the default branch this one was cut from: a rework is
            # fine, a committed deletion or rename is not
            against = ref if lesson_id in head else base_ref
            # T is a regular file turned into a symbolic link, which the checker rejects; the optional pointer may go
            # Valid still? Whatever changed (its files, a link target elsewhere, the source map): the store checker decides.
            if (git_text(context.root, "diff", "--no-renames", "--diff-filter=DT", "--name-only", against, "HEAD", "--", *required)
                    or pushed_content_problems(context, lesson_id)):
                out.append(lesson_id)
            continue
        in_head = all(regular_in_head(context.root, path) for path in required)
        dirty = git_text(context.root, "status", "--porcelain", "--untracked-files=all", "--", *files)
        if not in_head or dirty or pushed_content_problems(context, lesson_id):
            out.append(lesson_id)
    orphans = orphan_problems(exported()[0], context.source_map, set(lessons), cache, exported()[1])
    return out, orphans, source_map_problems(exported()[0], context.source_map, cache, exported()[1])


def drafts_left_behind(context: Context, lessons: dict[str, dict]) -> list[str]:
    """Released lessons (`todo`) whose files HEAD still holds: deleted only in the working tree, they would be pushed as
    free next to the very draft that makes them look taken, and another session could claim over it."""
    store = context.store.resolve().relative_to(context.root.resolve())
    names = git_text(context.root, "ls-tree", "-r", "--name-only", "HEAD", "--",
                     *[(store / folder).as_posix() for folder in ("lessons", "metadata", "diagrams")]).splitlines()
    held = {match.group(0) for name in names if (match := re.search(r"sd-\d{2}-\d{3}", name))}
    return sorted({lesson_id for lesson_id, entry in lessons.items() if entry.get("status") == "todo"} & held)


def source_map_in_checkout(context: Context) -> str | None:
    """The source map's path relative to the repository, or None when there is none to commit with this branch."""
    if context.source_map is None:
        return None
    try:
        return context.source_map.resolve().relative_to(context.root.resolve()).as_posix()
    except ValueError:  # a source map outside the checkout is not something this branch can carry
        return None


def source_map_changed(context: Context, against: str) -> bool:
    """Whether the source map differs from what `against` holds. A repin or retitle can change what makes every written
    lesson valid (the commit its metadata snapshots, the titles), although none of their files changed."""
    relative = source_map_in_checkout(context)
    if relative is None:
        return False
    if git(context.root, "rev-parse", "--verify", "-q", against, check=False).returncode != 0:
        return True  # nothing to compare with
    return bool(git_text(context.root, "diff", "--name-only", against, "HEAD", "--", relative))


def source_at(context: Context, ref: str) -> Source | None:
    """The source map as `ref` holds it, or None when the map is not part of this checkout or not on that branch."""
    relative = source_map_in_checkout(context)
    if relative is None:
        return None
    shown = git(context.root, "show", f"{ref}:{relative}", check=False)
    if shown.returncode != 0:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "source-map.json"
        path.write_bytes(shown.stdout)
        try:
            return load_source(path)
        except ClaimsError:
            return None


def uncommitted_source_map(context: Context) -> bool:
    """Whether the source map this session validated against has changes HEAD does not hold: --publish commits only the
    registry, so the remote would pair a registry synchronized with the new map with the old one."""
    relative = source_map_in_checkout(context)
    return relative is not None and bool(git_text(context.root, "status", "--porcelain", "--", relative))


def guard_publish(context: Context) -> None:
    """The registry is pushed whole, so every claim of this session in it is judged before anything is pushed, not only
    the ones the command names: a renewal made earlier in the working tree would otherwise reach the remote unjudged."""
    header, lessons = load_registry(context)
    if uncommitted_source_map(context):
        raise Refusal("nothing was pushed: the source map has uncommitted changes that the registry was synchronized with; "
                      "commit them together with the registry first (git add -A && git commit), then push")
    pending, orphans, map_findings = unfinished_commits(context, lessons)
    if map_findings:
        raise Refusal("nothing was pushed: the store checker rejects the source map: " + "; ".join(map_findings))
    if orphans:
        raise Refusal(f"nothing was pushed: the store holds {', '.join(orphans)}, which the registry no longer lists; "
                      "remove the files (and commit their deletion) or restore the source-map entry first")
    if pending:
        raise Refusal(f"nothing was pushed: {', '.join(pending)} {'is' if len(pending) == 1 else 'are'} marked written but "
                      "the lesson files are not committed as they are now (or the store checker rejects them); commit them together "
                      "with the registry first "
                      "(git add -A && git commit), then push")
    if left := drafts_left_behind(context, lessons):
        raise Refusal(f"nothing was pushed: {', '.join(left)} {'is' if len(left) == 1 else 'are'} released but the lesson "
                      "files are still committed; commit their deletion together with the registry first "
                      "(git add -A && git commit), then push")
    mine = my_claims(context, lessons, [])
    if not mine:
        return
    results = verdicts(context, header, lessons, mine, live=False)
    if lost := {lesson_id: reason for lesson_id, reason in results.items() if reason and not reason.startswith(UNPUBLISHED)}:
        raise Refusal("nothing was pushed: " + "; ".join(f"{lesson_id} {reason}" for lesson_id, reason in lost.items())
                      + f". Release {' '.join(lost)} first (python3 scripts/sd101_claims.py release {' '.join(lost)} --publish)")


def publish(context: Context, message: str) -> None:
    """Commit only the registry and push it to the same-named branch, so the other sessions can see it."""
    check_publishable(context)
    guard_publish(context)
    git(context.root, "add", "--", context.relative)
    if git(context.root, "diff", "--cached", "--quiet", "--", context.relative, check=False).returncode != 0:
        git(context.root, "commit", "--quiet", "--only", "-m", message, "--", context.relative)
    # Pushed even when there was nothing to commit: the claim may sit in a commit made by hand and never pushed.
    for delay in (0, *PUSH_BACKOFF_SECONDS):
        time.sleep(delay)
        pushed = git(context.root, "push", "--quiet", "-u", context.remote, f"HEAD:refs/heads/{context.branch}", check=False)
        if pushed.returncode == 0:
            return
    raise ClaimsError(f"the push failed: {pushed.stderr.decode('utf-8', 'replace').strip()}")


def my_claims(context: Context, lessons: dict[str, dict], ids: list[str]) -> list[str]:
    """The claims in progress of this session; ids named on the command line must each be one of them."""
    owned = [lesson_id for lesson_id, entry in lessons.items()
             if entry.get("status") == "doing" and entry.get("owner") == context.me]
    if not ids:
        return owned
    check_ids(context, lessons, ids)
    if foreign := [lesson_id for lesson_id in dict.fromkeys(ids) if lesson_id not in owned]:
        raise Refusal(f"{', '.join(foreign)}: not claimed by {context.me}")
    return list(dict.fromkeys(ids))


def check_ids(context: Context, lessons: dict[str, dict], ids: list[str]) -> None:
    known = {lesson_id for lesson_id, _ in context.source.lessons}
    for lesson_id in ids:
        if not LESSON_ID.fullmatch(lesson_id) or lesson_id not in known or lesson_id not in lessons:
            raise ClaimsError(f"{lesson_id} is not a lesson of the source map (or of the registry; run sync)")


def identity(holding: Holding) -> tuple:
    """What makes two records the same claim: the lesson, when it was claimed, whom it was taken from, and whether
    the owner shares the source knowingly. The heartbeat is not part of it: it changes every time the claim is renewed."""
    return holding.lesson_id, holding.claimed_at, holding.taken_from, holding.shared


def verdicts(context: Context, header: dict, lessons: dict[str, dict], ids: list[str],
             live: bool = True) -> dict[str, str | None]:
    """Per claim, why it is not (or not safely) held, or None. Online, a claim that exists only in this working tree
    is not held: no other session can see it, so none of them would respect it. The published copy has to be live
    too (`live`): a heartbeat renewed only here, behind a published one past its lease, leaves the claim open to a
    takeover. `touch` asks only for the copy to be there, since renewing an expired claim is what it is for."""
    found, _ = world_of(context, lessons)
    lease = lease_of(header)
    published = {identity(holding) for holdings in found.values() for holding in holdings
                 if holding.owner == context.me and holding.status == "doing" and holding.where != LOCAL
                 and not (live and is_stale(holding, context.now, lease))}
    live_published = {identity(holding) for holdings in found.values() for holding in holdings
                      if holding.owner == context.me and holding.status == "doing" and holding.where != LOCAL
                      and not is_stale(holding, context.now, lease)}
    out: dict[str, str | None] = {}
    gone = removed_upstream(context)
    for lesson_id in ids:
        mine = _holding(lessons[lesson_id], LOCAL)
        if mine is None:
            out[lesson_id] = "is not claimed by you"
            continue
        if lesson_id in gone:  # a claim taken before the default branch dropped the lesson is not a claim on anything
            out[lesson_id] = ("was removed from the source map by the default branch after this branch was cut; "
                              "merge the default branch into this branch")
            continue
        out[lesson_id] = lost_reason(mine, found, context.me, context.now, lease, context.source.partners.get(lesson_id, ()),
                                     context.offline or identity(mine) in live_published)
        if out[lesson_id] is None and not context.offline and identity(mine) not in published:
            out[lesson_id] = (f"{UNPUBLISHED}{context.remote}/{context.branch} with a live heartbeat yet; push it "
                              f"(git push -u {context.remote} {context.branch}) so the other sessions can see it")
    return out


def cmd_claim(context: Context, args: argparse.Namespace) -> int:
    require_owner(context)
    if args.publish:
        check_publishable(context)
    header, lessons = load_registry(context)
    lease = lease_of(header)
    found, _ = world_of(context, lessons)
    ids = list(dict.fromkeys(args.ids))
    if args.count:
        ids += free_lessons(context, found, lease, args.group, args.count, args.take_stale, args.allow_same_source,
                            exclude=tuple(ids))
    if not ids:
        print("claim: no free lesson to claim", file=sys.stderr)
        return 1
    check_ids(context, lessons, ids)
    if gone := [lesson_id for lesson_id in ids if lesson_id in removed_upstream(context)]:
        print(f"claim refused, nothing was written: the default branch removed {', '.join(gone)} from the source map after "
              "this branch was cut; merge it into this branch first", file=sys.stderr)
        return 1
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
        if entry.get("status") == "doing" and entry.get("owner") == context.me and lesson_id not in takes:
            entry["heartbeat_at"] = renewal(entry, context.now)
            if args.allow_same_source and context.source.partners.get(lesson_id):
                entry["shared_source"] = True  # the way to keep a half on purpose after losing it to the other half
            continue  # (a takeover below starts a new claim even when this session held the lesson before)
        fresh = {"id": lesson_id, "status": "doing", "title": entry.get("title", ""), "owner": context.me,
                 "claimed_at": stamp(context.now), "heartbeat_at": stamp(context.now)}
        if context.session:
            fresh["session"] = context.session
        if lesson_id in takes:
            fresh["taken_from"] = takes[lesson_id]
            fresh["generation"] = 1 + max((h.generation for h in found.get(lesson_id, []) if h.status == "doing"), default=0)
        if args.allow_same_source and context.source.partners.get(lesson_id):
            fresh["shared_source"] = True
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
    unpublished = [lesson_id for lesson_id, reason in results.items() if reason and reason.startswith(UNPUBLISHED)]
    lost = [lesson_id for lesson_id, reason in results.items() if reason and lesson_id not in unpublished]
    for lesson_id, reason in results.items():
        if reason is None:
            print(f"  {lesson_id}: yours")
        else:
            print(f"  {lesson_id}: {reason}", file=sys.stderr)
    if lost:
        print(f"Stop work on {', '.join(lost)} and release it: python3 scripts/sd101_claims.py release "
              f"{' '.join(lost)} --publish", file=sys.stderr)
    return 1 if lost or unpublished else 0


def cmd_verify(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    ids = my_claims(context, lessons, args.ids)
    if not ids:
        print(f"verify: {context.me} has no claim in progress")
        return 0
    return report_verdicts(verdicts(context, header, lessons, ids), context)


def cmd_touch(context: Context, args: argparse.Namespace) -> int:
    if args.publish:
        check_publishable(context)
    header, lessons = load_registry(context)
    ids = my_claims(context, lessons, args.ids)
    if not ids:
        print(f"touch: {context.me} has no claim in progress")
        return 0
    if args.publish:
        # publish() judges every claim of this session before it pushes anything: pushing a renewal first would
        # revive an expired public claim and let it win against a claim that was taken fairly while it was expired.
        publish(context, args.message or f"System Design vi: publish the claim of {', '.join(ids)}")  # a forgotten push
    results = verdicts(context, header, lessons, ids, live=False)
    for lesson_id in ids:
        if results[lesson_id] is None:
            lessons[lesson_id]["heartbeat_at"] = renewal(lessons[lesson_id], context.now)
    write_registry(context, header, lessons)
    if args.publish:
        publish(context, args.message or f"System Design vi: heartbeat for {', '.join(ids)}")
    return report_verdicts(results, context)


STORE_LEVEL_FILES = ("README.md", "PROGRESS.md", "MIGRATION.md", "progress.json", "claims.jsonl")


def content_problems(store: pathlib.Path, source_map: pathlib.Path | None, lesson_id: str,
                     cache: dict | None = None, boundary: pathlib.Path | None = None) -> list[str]:
    """What the store checker finds wrong with this one lesson (its text, metadata, figure). The findings about the
    store as a whole (README links, progress) are not the lesson's: they are fixed after finishing, before the pull
    request, and `scripts/sd101_check.py` stays the authority on them."""
    return [str(problem) for problem in _store_problems(store, source_map, cache, boundary)
            if problem.where not in STORE_LEVEL_FILES and lesson_id in f"{problem.where} {problem.message}"]


def _store_problems(store: pathlib.Path, source_map: pathlib.Path | None, cache: dict | None, boundary: pathlib.Path | None) -> list:
    """The store checker's findings about the whole tree, run once per tree: it is the expensive part, not the filtering."""
    if source_map is None:
        return []
    key = (str(store), str(source_map))
    if cache is not None and key in cache:
        return cache[key]
    spec = importlib.util.spec_from_file_location("sd101_check", pathlib.Path(__file__).with_name("sd101_check.py"))
    if spec is None or spec.loader is None:
        raise ClaimsError("scripts/sd101_check.py cannot be loaded, so the lesson cannot be checked")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("sd101_check", module)
    spec.loader.exec_module(module)
    # The roster pin (15 groups, 404 ids) belongs to the repository's own source map; a copy elsewhere is judged without it.
    pinned = source_map.resolve() == pathlib.Path(module.DEFAULT_SOURCE_MAP).resolve()
    found = module.check_store(store, source_map, pin_roster=pinned, boundary=boundary)
    if cache is not None:
        cache[key] = found
    return found


def source_map_problems(store: pathlib.Path, source_map: pathlib.Path | None, cache: dict | None = None,
                        boundary: pathlib.Path | None = None) -> list[str]:
    """The store checker's findings about the source map itself (not about a lesson): a map it rejects is no ground to
    publish a registry synchronized with it."""
    return [str(problem) for problem in _store_problems(store, source_map, cache, boundary) if problem.where == "source map"]


def orphan_problems(store: pathlib.Path, source_map: pathlib.Path | None, known: set[str], cache: dict | None = None,
                    boundary: pathlib.Path | None = None) -> list[str]:
    """Lesson ids the store checker reports that the registry does not hold: the files of a record that was dropped (or
    never made) are still in the tree, so the store would fail its check while no record answers for them."""
    found: dict[str, str] = {}
    for problem in _store_problems(store, source_map, cache, boundary):
        if problem.where in STORE_LEVEL_FILES:
            continue
        for lesson_id in re.findall(r"sd-\d{2}-\d{3}", f"{problem.where} {problem.message}"):
            if lesson_id not in known:
                found.setdefault(lesson_id, str(problem))
    return sorted(found)


@contextlib.contextmanager
def pushed_tree(context: Context):
    """The checkout as HEAD holds it, exported to a temporary directory: that is the tree --publish pushes, not the
    working tree, which may carry an uncommitted repair (or damage) the remote will never see. The whole checkout is
    exported, not only the store, because a lesson may link to a file elsewhere in it. Yields (store, boundary)."""
    relative = context.store.resolve().relative_to(context.root.resolve()).as_posix()
    archive = git(context.root, "archive", "--format=tar", "HEAD").stdout
    with tempfile.TemporaryDirectory() as tmp, tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(tmp, filter="data")
        yield pathlib.Path(tmp) / relative, pathlib.Path(tmp)


def missing_artifacts(context: Context, lesson_id: str) -> list[str]:
    """The files the store needs for a finished lesson that are absent or symbolic links, relative to the store."""
    return [path for path in (f"lessons/{lesson_id}/lesson.md", f"lessons/{lesson_id}/lesson.yaml",
                              f"metadata/{lesson_id}.json", f"diagrams/{lesson_id}-main.svg")
            if (context.store / path).is_symlink() or not (context.store / path).is_file()]


def cmd_finish(context: Context, args: argparse.Namespace) -> int:
    header, lessons = load_registry(context)
    check_ids(context, lessons, args.ids)
    problems = []
    for lesson_id in args.ids:
        entry = lessons[lesson_id]
        if entry.get("status") != "doing" or entry.get("owner") != context.me:
            problems.append(f"{lesson_id}: is not claimed by {context.me} (claim it first)")
        elif missing := missing_artifacts(context, lesson_id):
            problems.append(f"{lesson_id}: " + "; ".join(f"{path} does not exist yet (or is a symbolic link)" for path in missing))
    if not problems:
        cache: dict = {}  # one traversal of the store for the whole batch
        for lesson_id in args.ids:
            if broken := content_problems(context.store, context.source_map, lesson_id, cache):
                problems.append(f"{lesson_id}: the store checker rejects the lesson: " + "; ".join(broken))
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
        if lessons[lesson_id].get("shared_source"):
            entry["shared_source"] = True  # a half taken on purpose stays one once it is written
        lessons[lesson_id] = entry
    write_registry(context, header, lessons)
    print(f"written: {', '.join(args.ids)}. Commit {context.relative} together with the lesson files.")
    return 0


def cmd_release(context: Context, args: argparse.Namespace) -> int:
    if args.publish:
        check_publishable(context)
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

def pull_request_number(value: str) -> int:
    if not value.isdecimal() or int(value) < 1:
        raise argparse.ArgumentTypeError(f"{value!r} is not a pull request number")
    return int(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--store", type=pathlib.Path, default=DEFAULT_STORE)
    parser.add_argument("--source-map", type=pathlib.Path, default=DEFAULT_SOURCE_MAP)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--owner", help="who holds the claims; default is the current branch")
    parser.add_argument("--session", default=os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID"))
    parser.add_argument("--offline", action="store_true", help="decide from this working tree alone")
    parser.add_argument("--ignore-unreadable", action="store_true",
                        help="decide even though the registry on some branch cannot be parsed")
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
    finish.add_argument("--pr", type=pull_request_number)
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
                          branch, bool(args.owner), args.ignore_unreadable, args.source_map)
        return args.handler(context, args)
    except Refusal as error:
        print(f"sd101_claims: {error}", file=sys.stderr)
        return 1
    except ClaimsError as error:
        print(f"sd101_claims: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
