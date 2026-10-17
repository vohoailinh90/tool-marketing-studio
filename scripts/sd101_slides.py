#!/usr/bin/env python3
"""Claim the slide deck of a System Design lesson before building it, so two sessions never build the same one.

`sd101_claims.py` stops two sessions writing one lesson; this stops two sessions turning one written lesson into slides.
The record is one file per lesson, `lessons/<id>/slides/deck.yaml`, so sessions that take different lessons never touch
the same file and never conflict at merge:

  status doing   a session is building the deck (owner = its branch, claimed_at, heartbeat_at; generation and
                 taken_from after a takeover)
  status done    the deck exists on Moda (moda_canvas, moda_url, slide_count, size) and `exports` says whether its
                 PNG and PPTX files are in the folder as well (`done`) or not yet (`pending`)

Visibility follows sd101_claims.py: every command fetches all branches of the remote. On the default branch every
record counts; on any other branch only the records whose owner is that branch (a copy inherited by merging is not a
claim). A claim therefore protects nothing until it is pushed, which `--publish` does. A `doing` record whose
heartbeat is older than the lease is stale and is taken over on purpose with `claim <id> --take-stale`.

  python3 scripts/sd101_slides.py status                            # counts per group, next free lessons
  python3 scripts/sd101_slides.py claim --next 3 --publish          # or: claim sd-01-002 sd-01-003 --publish
  python3 scripts/sd101_slides.py verify                            # exit 0 = every claim of mine is still mine
  python3 scripts/sd101_slides.py touch --publish                   # renew the heartbeat while you work
  python3 scripts/sd101_slides.py finish sd-01-002 --canvas cvs_... --url https://moda.app/canvas/... --slides 10
  python3 scripts/sd101_slides.py exported sd-01-002 --publish      # its PPTX and PNG files are now in slides/
  python3 scripts/sd101_slides.py release sd-01-003 --publish       # give a lesson back

There is no compare-and-swap on a git remote: two sessions that read before either pushed can both claim a lesson.
The earlier claimed_at wins (then the smaller owner), and the loser's `verify`, `touch` and `finish` fail.
"""

from __future__ import annotations

import argparse
import datetime
import importlib.util
import os
import pathlib
import re
import struct
import sys
import time
import zipfile
from dataclasses import dataclass

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_STORE = ROOT / "system-design-101" / "vi"
SLIDES_DIR = "slides"
RECORD = "deck.yaml"
STATUSES = ("doing", "done")
EXPORTS = ("pending", "done")
KEY_ORDER = ("id", "status", "owner", "session", "taken_from", "generation", "claimed_at", "heartbeat_at", "done_at",
             "moda_canvas", "moda_url", "slide_count", "size", "exports")
DOING_KEYS = {"id", "status", "owner", "session", "taken_from", "generation", "claimed_at", "heartbeat_at"}
DONE_KEYS = {"id", "status", "owner", "session", "taken_from", "generation", "claimed_at", "done_at", "moda_canvas",
             "moda_url", "slide_count", "size", "exports"}
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
LESSON_ID = re.compile(r"sd-\d{2}-\d{3}")
CANVAS_ID = re.compile(r"cvs_[0-9A-Za-z]{20,}")
SIZE = re.compile(r"[1-9]\d{2,4}x[1-9]\d{2,4}")
MODA_URL = "https://moda.app/canvas/"
SLIDE_COUNTS = range(8, 11)  # docs/sd101-slides.md: 8 to 10 slides, one progress dot each
LEASE_HOURS = 72
CLOCK_SKEW_HOURS = 1
PUSH_BACKOFF_SECONDS = (2, 4, 8, 16)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class SlidesError(Exception):
    """The remote or git could not be read: nothing is decided on a guess (exit 2)."""


def now() -> datetime.datetime:
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


def claims_module():
    """The git helpers of sd101_claims.py, loaded the way sd101_check.py loads it."""
    module = sys.modules.get("sd101_claims")
    if module is None:
        spec = importlib.util.spec_from_file_location("sd101_claims", pathlib.Path(__file__).with_name("sd101_claims.py"))
        if spec is None or spec.loader is None:
            raise SlidesError("scripts/sd101_claims.py cannot be loaded")
        module = importlib.util.module_from_spec(spec)
        sys.modules["sd101_claims"] = module
        spec.loader.exec_module(module)
    return module


def git(root: pathlib.Path, *args: str, check: bool = True, data: bytes | None = None):
    try:
        return claims_module().git(root, *args, check=check, data=data)
    except claims_module().ClaimsError as error:
        raise SlidesError(str(error)) from error


def git_text(root: pathlib.Path, *args: str) -> str:
    return git(root, *args).stdout.decode("utf-8", "replace").strip()


# ----------------------------------------------------------------------------------------------- the record

def render(record: dict) -> str:
    ordered = {key: record[key] for key in KEY_ORDER if key in record}
    return yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, default_flow_style=False)


def parse_record(text: str) -> dict | None:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    for key in ("claimed_at", "heartbeat_at", "done_at"):
        if isinstance(data.get(key), datetime.datetime):  # YAML reads an unquoted 2026-10-17T09:00:00Z as a timestamp
            moment = data[key] if data[key].tzinfo else data[key].replace(tzinfo=datetime.timezone.utc)
            data[key] = stamp(moment)
    return data


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _count(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def record_problems(record: object, lesson_id: str) -> list[str]:
    """What is wrong with one deck.yaml, in words; empty when it is well formed."""
    if not isinstance(record, dict):
        return ["is not a mapping"]
    problems: list[str] = []
    status = record.get("status")
    if status not in STATUSES:
        return [f"status must be one of {', '.join(STATUSES)}"]
    allowed = DOING_KEYS if status == "doing" else DONE_KEYS
    for key in record:
        if key not in allowed:
            problems.append(f"key {key!r} is not allowed on a {status} record")
    if record.get("id") != lesson_id:
        problems.append(f"id must be {lesson_id}")
    if not _text(record.get("owner")):
        problems.append("owner is missing")
    if "session" in record and not _text(record["session"]):
        problems.append("session must be text")
    if "generation" in record and not _count(record["generation"]):
        problems.append("generation must be a whole number of 1 or more")
    if "taken_from" in record and not (isinstance(record["taken_from"], list) and record["taken_from"]
                                       and all(_text(item) for item in record["taken_from"])):
        problems.append("taken_from must be a list of owners")
    elif ("taken_from" in record) != ("generation" in record):
        problems.append("generation and taken_from come together: both after a takeover, neither otherwise")
    elif "taken_from" in record and record.get("owner") in record["taken_from"]:
        problems.append("taken_from must not name the owner itself")
    if "claimed_at" in record and parse_stamp(record["claimed_at"]) is None:
        problems.append("claimed_at must look like 2026-10-17T11:00:00Z")
    if status == "doing":
        for key in ("claimed_at", "heartbeat_at"):
            if parse_stamp(record.get(key)) is None:
                problems.append(f"{key} must look like 2026-10-17T11:00:00Z")
        return problems
    if parse_stamp(record.get("done_at")) is None:
        problems.append("done_at must look like 2026-10-17T11:00:00Z")
    canvas = record.get("moda_canvas")
    if not (isinstance(canvas, str) and CANVAS_ID.fullmatch(canvas)):
        problems.append("moda_canvas must be the cvs_ id of the Moda canvas")
    url = record.get("moda_url")
    if not (isinstance(url, str) and url.startswith(MODA_URL) and len(url) > len(MODA_URL) and " " not in url):
        problems.append(f"moda_url must start with {MODA_URL}")
    if not (_count(record.get("slide_count")) and record["slide_count"] in SLIDE_COUNTS):
        problems.append(f"slide_count must be between {SLIDE_COUNTS.start} and {SLIDE_COUNTS.stop - 1}")
    if not (isinstance(record.get("size"), str) and SIZE.fullmatch(record["size"])):
        problems.append("size must look like 1920x1080")
    if record.get("exports") not in EXPORTS:
        problems.append(f"exports must be one of {', '.join(EXPORTS)}")
    return problems


def png_size(path: pathlib.Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            head = handle.read(24)
    except OSError:
        return None
    if len(head) < 24 or head[:8] != PNG_SIGNATURE or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


def folder_problems(slides_dir: pathlib.Path, lesson_id: str) -> list[str]:
    """What is wrong with a lesson's slides/ folder: the record, and the exports the record promises."""
    problems: list[str] = []
    if slides_dir.is_symlink() or not slides_dir.is_dir():
        return ["slides is not a directory"]
    names = sorted(path.name for path in slides_dir.iterdir())
    for path in sorted(slides_dir.iterdir()):
        if path.is_symlink() or not path.is_file():
            problems.append(f"{path.name} is not a regular file")
    record_file = slides_dir / RECORD
    if not record_file.is_file():
        return problems + [f"{RECORD} is missing"]
    try:
        record = parse_record(record_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        record = None
    if record is None:
        return problems + [f"{RECORD} does not parse as a mapping"]
    found = record_problems(record, lesson_id)
    problems += [f"{RECORD}: {problem}" for problem in found]
    if found:
        return problems
    exported = record["status"] == "done" and record["exports"] == "done"
    want = {RECORD}
    if exported:
        want |= {f"{lesson_id}.pptx", *(f"{number:02d}.png" for number in range(1, record["slide_count"] + 1))}
    for name in names:
        if name not in want:
            problems.append(f"{name} is not expected here" + ("" if exported else " (exports are not recorded as done)"))
    for name in sorted(want - set(names)):
        problems.append(f"{name} is missing")
    if exported:
        width, height = (int(part) for part in record["size"].split("x"))
        for name in sorted(want & set(names)):
            path = slides_dir / name
            if name.endswith(".png") and png_size(path) != (width, height):
                problems.append(f"{name} is not a {width}x{height} PNG")
            if name.endswith(".pptx") and not zipfile.is_zipfile(path):
                problems.append(f"{name} is not a PowerPoint file")
    return problems


# --------------------------------------------------------------------------------------------- the world

@dataclass(frozen=True)
class Holding:
    lesson_id: str
    status: str
    owner: str
    claimed_at: str | None
    heartbeat_at: str | None
    generation: int
    taken_from: tuple[str, ...]
    where: str
    problems: tuple[str, ...] = ()    # what is wrong with the record; status is "invalid" when it cannot be read at all


LOCAL = "this working tree"


@dataclass
class Context:
    root: pathlib.Path
    store: pathlib.Path
    remote: str
    me: str | None
    offline: bool

    def record_path(self, lesson_id: str) -> pathlib.Path:
        return self.store / "lessons" / lesson_id / SLIDES_DIR / RECORD

    def relative(self, lesson_id: str) -> str:
        return self.record_path(lesson_id).resolve().relative_to(self.root.resolve()).as_posix()

    def written(self) -> list[str]:
        lessons = self.store / "lessons"
        found = [path.name for path in lessons.iterdir()
                 if path.is_dir() and LESSON_ID.fullmatch(path.name) and (path / "lesson.md").is_file()] \
            if lessons.is_dir() else []
        return sorted(found)


def _holding(lesson_id: str, record: dict | None, where: str) -> Holding:
    """What a deck.yaml says, read leniently: a record that fails validation still holds its lesson (a bad `done`
    must not offer the lesson again), and one that cannot be read at all is `invalid` and blocks it until fixed."""
    if record is None:
        return Holding(lesson_id, "invalid", "", None, None, 0, (), where, ("does not parse as a mapping",))
    taken = record.get("taken_from") if isinstance(record.get("taken_from"), list) else []
    return Holding(lesson_id, record["status"] if record.get("status") in STATUSES else "invalid",
                   record["owner"] if _text(record.get("owner")) else "",
                   record["claimed_at"] if isinstance(record.get("claimed_at"), str) else None,
                   record["heartbeat_at"] if isinstance(record.get("heartbeat_at"), str) else None,
                   record["generation"] if _count(record.get("generation")) else 0,
                   tuple(item for item in taken if _text(item)), where, tuple(record_problems(record, lesson_id)))


def remote_branches(context: Context) -> list[str]:
    output = git_text(context.root, "for-each-ref", "--format=%(refname:lstrip=3)", f"refs/remotes/{context.remote}")
    return [name for name in output.splitlines() if name and name != "HEAD"]


def read_remote(context: Context, names: list[str], ids: list[str]) -> dict[tuple[str, str], str]:
    """(branch, lesson id) -> deck.yaml text, for every pair that has one."""
    pairs = [(name, lesson_id) for name in names for lesson_id in ids]
    if not pairs:
        return {}
    request = "".join(f"refs/remotes/{context.remote}/{name}:{context.relative(lesson_id)}\n"
                      for name, lesson_id in pairs).encode()
    output = git(context.root, "cat-file", "--batch", data=request).stdout
    found: dict[tuple[str, str], str] = {}
    position = 0
    try:
        for pair in pairs:
            end = output.index(b"\n", position)
            fields = output[position:end].split(b" ")
            position = end + 1
            if len(fields) == 3:
                size = int(fields[2])
                if fields[1] == b"blob":
                    found[pair] = output[position:position + size].decode("utf-8", "replace")
                position += size + 1
    except ValueError as error:
        raise SlidesError(f"git cat-file printed something unexpected: {error}") from error
    return found


def gather(context: Context, ids: list[str]) -> tuple[dict[str, list[Holding]], list[str]]:
    """Every holding of every lesson in ids as the remote and this tree show it, and the records it could not use."""
    holdings: dict[str, list[Holding]] = {lesson_id: [] for lesson_id in ids}
    warnings: list[str] = []
    if not context.offline:
        helpers = claims_module()
        try:
            helpers.fetch_remote(context.root, context.remote)
            base = helpers.default_branch(context.root, context.remote)
        except helpers.ClaimsError as error:
            raise SlidesError(f"the remote could not be read ({error}); pass --offline to decide without it") from error
        names = remote_branches(context)
        for (name, lesson_id), text in read_remote(context, names, ids).items():
            where = f"{context.remote}/{name}"
            holding = _holding(lesson_id, parse_record(text), where)
            if holding.problems:
                warnings.append(f"{where}: {lesson_id}/{SLIDES_DIR}/{RECORD} {'; '.join(holding.problems)}")
            if name == base:
                if holding.status == "doing" and holding.owner in names and holding.owner != base:
                    continue  # a claim in progress belongs to its owner's branch, which says whether it still stands
                holdings[lesson_id].append(holding)
            elif holding.owner == name or holding.status == "invalid":  # an unreadable record names no owner but blocks
                holdings[lesson_id].append(holding)
            else:
                warnings.append(f"{where}: {lesson_id} names another owner ({holding.owner or 'none'}); not a claim")
    for lesson_id in ids:
        path = context.record_path(lesson_id)
        if path.is_file():
            holding = _holding(lesson_id, parse_record(path.read_text(encoding="utf-8")), LOCAL)
            if holding.owner == context.me:
                holdings[lesson_id].append(holding)
    return holdings, warnings


def is_stale(holding: Holding, moment: datetime.datetime) -> bool:
    if holding.status != "doing":
        return False
    beat = parse_stamp(holding.heartbeat_at)
    if beat is None or beat - moment > datetime.timedelta(hours=CLOCK_SKEW_HOURS):
        return True
    return moment - beat > datetime.timedelta(hours=LEASE_HOURS)


def beats(first: Holding, second: Holding) -> bool:
    """Whether first wins the lesson over second: a takeover over the claim it took, then the higher generation, the
    earlier claim, the smaller owner. No clock decides between two takeovers."""
    if second.owner in first.taken_from:
        return True
    if first.owner in second.taken_from:
        return False
    return (-first.generation, first.claimed_at or "", first.owner) < (-second.generation, second.claimed_at or "", second.owner)


def standing(holdings: list[Holding], moment: datetime.datetime) -> tuple[str, Holding | None]:
    """free | done | invalid (a record that cannot be read) | doing (the live winner) | stale (only stale claims)."""
    done = [holding for holding in holdings if holding.status == "done"]
    if done:
        return "done", min(done, key=lambda holding: (holding.claimed_at or "", holding.owner))
    invalid = [holding for holding in holdings if holding.status == "invalid"]
    if invalid:
        return "invalid", invalid[0]
    live = [holding for holding in holdings if holding.status == "doing" and not is_stale(holding, moment)]
    if live:
        winner = live[0]
        for holding in live[1:]:
            if beats(holding, winner):
                winner = holding
        return "doing", winner
    stale = [holding for holding in holdings if holding.status == "doing"]
    if stale:
        return "stale", sorted(stale, key=lambda holding: (holding.claimed_at or "", holding.owner))[0]
    return "free", None


def refusal(lesson_id: str, found: list[Holding], context: Context, moment: datetime.datetime,
            take_stale: bool) -> str | None:
    state, holding = standing(found, moment)
    if state == "done":
        return f"{lesson_id}: already built by {holding.owner or 'an unknown owner'} ({holding.where})"
    if state == "invalid":
        return (f"{lesson_id}: {holding.where} holds a record that cannot be read ({'; '.join(holding.problems)}); "
                "fix it first")
    if state == "doing" and holding.owner != context.me:
        return f"{lesson_id}: claimed by {holding.owner} (heartbeat {holding.heartbeat_at})"
    if state == "stale" and not any(other.owner == context.me for other in found) and not take_stale:
        return (f"{lesson_id}: claimed by {holding.owner}, whose heartbeat ({holding.heartbeat_at}) is older than "
                f"{LEASE_HOURS} hours; take it over on purpose with --take-stale")
    return None


def lost_reason(lesson_id: str, found: list[Holding], context: Context, moment: datetime.datetime) -> str | None:
    """Why a claim of mine no longer holds, or None when it does."""
    mine = [holding for holding in found if holding.owner == context.me and holding.status == "doing"]
    if not mine:
        return f"{lesson_id}: you hold no claim"
    published = [holding for holding in mine if holding.where != LOCAL]
    if not published:
        return f"{lesson_id}: your claim is not on {context.remote}/{context.me}; run with --publish"
    me = max(published, key=lambda holding: holding.heartbeat_at or "")
    for holding in found:
        if holding.owner == context.me and holding.status == "doing":
            continue
        if holding.status == "invalid":
            return f"{lesson_id}: {holding.where} holds a record that cannot be read; fix it first"
        if holding.status == "done":
            return f"{lesson_id}: already built by {holding.owner}"
        if not is_stale(holding, moment) and beats(holding, me):
            return f"{lesson_id}: lost to {holding.owner}"
    if is_stale(me, moment):
        return f"{lesson_id}: your published heartbeat ({me.heartbeat_at}) has expired; run touch --publish"
    return None


# -------------------------------------------------------------------------------------------- git helpers

def current_branch(root: pathlib.Path) -> str | None:
    return claims_module().current_branch(root)


def require_branch(context: Context) -> str:
    if not context.me:
        raise SlidesError("HEAD is detached; work on a branch (or pass --owner)")
    if not context.offline:
        helpers = claims_module()
        try:
            base = helpers.default_branch(context.root, context.remote)
        except helpers.ClaimsError as error:
            raise SlidesError(f"the remote could not be read ({error}); pass --offline to decide without it") from error
        if context.me == base:
            raise SlidesError(f"{context.me} is the default branch of {context.remote}; claims are pushed from a work branch")
    return context.me


def publish(context: Context, paths: list[pathlib.Path], message: str) -> None:
    """Commit only these paths and push the work branch, never the default branch."""
    branch = require_branch(context)
    relative = [path.resolve().relative_to(context.root.resolve()).as_posix() for path in paths]
    git(context.root, "add", "-A", "--", *relative, check=False)  # a record that was never committed has nothing to add
    if git(context.root, "diff", "--cached", "--quiet", "--", *relative, check=False).returncode != 0:
        git(context.root, "commit", "--quiet", "--only", "-m", message, "--", *relative)
    last = ""
    for delay in (0, *PUSH_BACKOFF_SECONDS):
        time.sleep(delay)
        result = git(context.root, "push", "--quiet", "-u", context.remote, f"HEAD:refs/heads/{branch}", check=False)
        if result.returncode == 0:
            return
        last = result.stderr.decode("utf-8", "replace").strip()
        if "non-fast-forward" in last or "rejected" in last or "fetch first" in last:
            break
    raise SlidesError(f"git push failed: {last}")


# ------------------------------------------------------------------------------------------------ commands

def my_records(context: Context) -> list[str]:
    """The lessons whose deck.yaml in this tree is a `doing` claim of mine."""
    mine = []
    for lesson_id in context.written():
        path = context.record_path(lesson_id)
        record = parse_record(path.read_text(encoding="utf-8")) if path.is_file() else None
        if record and record.get("owner") == context.me and record.get("status") == "doing":
            mine.append(lesson_id)
    return mine


def free_lessons(context: Context, holdings: dict[str, list[Holding]], moment: datetime.datetime, group: str | None,
                 count: int, take_stale: bool) -> list[str]:
    chosen: list[str] = []
    for lesson_id in sorted(holdings):
        if group and not lesson_id.startswith(group):
            continue
        if len(chosen) >= count:
            break
        if refusal(lesson_id, holdings[lesson_id], context, moment, take_stale) is None \
                and standing(holdings[lesson_id], moment)[0] != "doing":
            chosen.append(lesson_id)
    return chosen


def cmd_status(context: Context, args: argparse.Namespace) -> int:
    ids = context.written()
    holdings, warnings = gather(context, ids)
    moment = now()
    table: dict[str, dict[str, int]] = {}
    for lesson_id in ids:
        state, _ = standing(holdings[lesson_id], moment)
        table.setdefault(lesson_id[:5], {"free": 0, "doing": 0, "stale": 0, "done": 0, "invalid": 0})[state] += 1
    totals = {key: sum(row[key] for row in table.values()) for key in ("free", "doing", "stale", "done", "invalid")}
    print(f"Slide decks of {len(ids)} written lessons: done {totals['done']} | doing {totals['doing']} | "
          f"stale {totals['stale']} | invalid {totals['invalid']} | free {totals['free']}")
    print(f"{'group':<8}{'done':>6}{'doing':>7}{'stale':>7}{'invalid':>9}{'free':>6}")
    for group, row in sorted(table.items()):
        print(f"{group:<8}{row['done']:>6}{row['doing']:>7}{row['stale']:>7}{row['invalid']:>9}{row['free']:>6}")
    for lesson_id in ids:
        state, holding = standing(holdings[lesson_id], moment)
        if state in ("doing", "stale", "invalid") and (args.all or holding.owner == context.me or state == "invalid"):
            print(f"  {lesson_id} {state} by {holding.owner or 'unknown'} ({holding.where}), "
                  f"heartbeat {holding.heartbeat_at}")
    free = free_lessons(context, holdings, moment, None, 5, False)
    print("Next free: " + (", ".join(free) if free else "none"))
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


def cmd_next(context: Context, args: argparse.Namespace) -> int:
    holdings, _ = gather(context, context.written())
    free = free_lessons(context, holdings, now(), args.group, args.count, False)
    print(" ".join(free))
    return 0 if free else 1


def cmd_claim(context: Context, args: argparse.Namespace) -> int:
    branch = require_branch(context)
    written = context.written()
    holdings, warnings = gather(context, written)
    moment = now()
    wanted = list(dict.fromkeys(args.ids))
    unknown = [lesson_id for lesson_id in wanted if lesson_id not in written]
    if unknown:
        print(f"{', '.join(unknown)}: not a written lesson in this checkout (merge the default branch first?)",
              file=sys.stderr)
        return 1
    if args.next:
        extra = [lesson_id for lesson_id in free_lessons(context, holdings, moment, args.group, args.next + len(wanted),
                                                         args.take_stale) if lesson_id not in wanted]
        wanted += extra[:args.next]
    if not wanted:
        print("nothing free to claim", file=sys.stderr)
        return 1
    refused = [reason for lesson_id in wanted
               if (reason := refusal(lesson_id, holdings[lesson_id], context, moment, args.take_stale))]
    if refused:
        print("\n".join(refused), file=sys.stderr)
        return 1
    for lesson_id in wanted:
        state, holding = standing(holdings[lesson_id], moment)
        if state == "doing" and holding.owner == context.me:
            continue  # already mine; --publish below pushes it if it is not on the remote yet
        taken = sorted({item for other in holdings[lesson_id] if other.status == "doing" and other.owner != context.me
                        for item in (other.owner, *other.taken_from)})
        generation = max([other.generation for other in holdings[lesson_id] if other.owner != context.me] + [0]) + 1 \
            if taken else 0
        record = {"id": lesson_id, "status": "doing", "owner": branch, "claimed_at": stamp(moment),
                  "heartbeat_at": stamp(moment)}
        if args.session:
            record["session"] = args.session
        if taken:
            record.update(taken_from=taken, generation=generation)
        path = context.record_path(lesson_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(record), encoding="utf-8")
    print(f"claimed {', '.join(wanted)} as {branch}")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if args.publish:
        publish(context, [context.record_path(lesson_id) for lesson_id in wanted], f"Slides: claim {', '.join(wanted)}")
        return report(context, wanted)
    return 0


def report(context: Context, ids: list[str]) -> int:
    holdings, _ = gather(context, ids)
    moment = now()
    problems = [reason for lesson_id in ids if (reason := lost_reason(lesson_id, holdings[lesson_id], context, moment))]
    for reason in problems:
        print(reason, file=sys.stderr)
    if problems:
        print("stop work on the lessons you lost and release them; do not push their decks", file=sys.stderr)
        return 1
    print("verified: " + ", ".join(ids))
    return 0


def named_or_mine(context: Context, ids: list[str]) -> list[str]:
    mine = my_records(context)
    chosen = list(dict.fromkeys(ids)) if ids else mine
    stranger = [lesson_id for lesson_id in chosen if lesson_id not in mine]
    if stranger:
        raise SlidesError(f"{', '.join(stranger)}: not a claim of {context.me}")
    if not chosen:
        raise SlidesError("you hold no claim")
    return chosen


def cmd_verify(context: Context, args: argparse.Namespace) -> int:
    return report(context, named_or_mine(context, args.ids))


def cmd_touch(context: Context, args: argparse.Namespace) -> int:
    ids = named_or_mine(context, args.ids)
    holdings, _ = gather(context, ids)
    moment = now()
    lost = [reason for lesson_id in ids if (reason := lost_reason(lesson_id, holdings[lesson_id], context, moment))
            and "expired" not in reason]
    if lost:
        print("\n".join(lost), file=sys.stderr)
        return 1
    paths = []
    for lesson_id in ids:
        path = context.record_path(lesson_id)
        record = parse_record(path.read_text(encoding="utf-8")) or {}
        record["heartbeat_at"] = stamp(moment)
        path.write_text(render(record), encoding="utf-8")
        paths.append(path)
    print(f"renewed {', '.join(ids)}")
    if args.publish:
        publish(context, paths, f"Slides: renew {', '.join(ids)}")
        return report(context, ids)
    return 0


def cmd_finish(context: Context, args: argparse.Namespace) -> int:
    lesson_id = args.id
    named_or_mine(context, [lesson_id])
    holdings, _ = gather(context, [lesson_id])
    reason = lost_reason(lesson_id, holdings[lesson_id], context, now())
    if reason and "expired" not in reason:
        print(reason, file=sys.stderr)
        return 1
    path = context.record_path(lesson_id)
    old = parse_record(path.read_text(encoding="utf-8")) or {}
    record = {key: old[key] for key in ("id", "owner", "session", "taken_from", "generation", "claimed_at") if key in old}
    record.update(status="done", done_at=stamp(now()), moda_canvas=args.canvas, moda_url=args.url,
                  slide_count=args.slides, size=args.size, exports=args.exports)
    problems = record_problems(record, lesson_id)
    if problems:
        print("\n".join(f"{lesson_id}: {problem}" for problem in problems), file=sys.stderr)
        return 1
    previous = path.read_text(encoding="utf-8")
    path.write_text(render(record), encoding="utf-8")
    found = folder_problems(path.parent, lesson_id)
    if found:
        path.write_text(previous, encoding="utf-8")
        print("\n".join(f"{lesson_id}: {problem}" for problem in found), file=sys.stderr)
        return 1
    print(f"finished {lesson_id}: {args.slides} slides, exports {args.exports}")
    if args.publish:
        publish(context, [path.parent], f"Slides: finish {lesson_id}")
        remote = gather(context, [lesson_id])[0][lesson_id]
        mine = [holding for holding in remote
                if holding.status == "done" and holding.owner == context.me and holding.where != LOCAL]
        if not mine:
            print(f"{lesson_id}: the finished record is not on {context.remote}/{context.me}", file=sys.stderr)
            return 1
        moment = now()  # the finished record keeps its claim's time and generation, so it is judged as that claim
        rivals = [holding for holding in remote if holding.status == "doing" and holding.owner != context.me
                  and not is_stale(holding, moment) and beats(holding, mine[0])]
        if rivals:
            print(f"pushed, but {lesson_id} is finished here and {rivals[0].owner} holds the earlier claim; delete this "
                  f"branch's slides/ for it, commit and push, so the lesson goes to {rivals[0].owner}", file=sys.stderr)
            return 1
    return 0


def cmd_exported(context: Context, args: argparse.Namespace) -> int:
    """A finished deck whose PPTX and PNG files were added to its folder: record that exports are done."""
    path = context.record_path(args.id)
    previous = path.read_text(encoding="utf-8") if path.is_file() else ""
    record = parse_record(previous) if previous else None
    if not record or record.get("status") != "done":
        print(f"{args.id}: not a finished deck; finish it first", file=sys.stderr)
        return 1
    record["exports"] = "done"
    path.write_text(render(record), encoding="utf-8")
    found = folder_problems(path.parent, args.id)
    if found:
        path.write_text(previous, encoding="utf-8")
        print("\n".join(f"{args.id}: {problem}" for problem in found), file=sys.stderr)
        return 1
    print(f"exports of {args.id} are done")
    if args.publish:
        publish(context, [path.parent], f"Slides: exports of {args.id}")
    return 0


def cmd_release(context: Context, args: argparse.Namespace) -> int:
    paths = []
    for lesson_id in dict.fromkeys(args.ids):
        path = context.record_path(lesson_id)
        record = parse_record(path.read_text(encoding="utf-8")) if path.is_file() else None
        if not record or record.get("owner") != context.me:
            print(f"{lesson_id}: not a claim of {context.me}", file=sys.stderr)
            return 1
        if record.get("status") == "done":
            print(f"{lesson_id}: already finished; a finished deck is not released", file=sys.stderr)
            return 1
        stray = sorted(other.name for other in path.parent.iterdir() if other.name != RECORD)
        if stray:
            print(f"{lesson_id}: slides/ also holds {', '.join(stray)}; remove them first", file=sys.stderr)
            return 1
        paths.append(path)
    for path in paths:
        path.unlink()
        if not any(path.parent.iterdir()):
            path.parent.rmdir()
    print(f"released {', '.join(path.parent.parent.name for path in paths)}")
    if args.publish:
        publish(context, [path.parent for path in paths],
                f"Slides: release {', '.join(path.parent.parent.name for path in paths)}")
    return 0


# ----------------------------------------------------------------------------------------------- entry point

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--store", type=pathlib.Path, default=DEFAULT_STORE, help="the store (default: system-design-101/vi)")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--owner", help="override the owner, which is the current branch (tests, detached checkouts)")
    parser.add_argument("--offline", action="store_true", help="decide without reading the remote (accepts the risk)")
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="counts per group and the next free lessons")
    status.add_argument("--all", action="store_true", help="list every live claim, not only mine")
    status.set_defaults(run=cmd_status)
    following = commands.add_parser("next", help="print the next free lessons")
    following.add_argument("--count", type=int, default=3)
    following.add_argument("--group")
    following.set_defaults(run=cmd_next)
    claim = commands.add_parser("claim", help="claim lessons before building their decks")
    claim.add_argument("ids", nargs="*", metavar="sd-XX-NNN")
    claim.add_argument("--next", type=int, default=0, metavar="N", help="also claim the next N free lessons")
    claim.add_argument("--group", help="with --next: only lessons of this group, e.g. sd-01")
    claim.add_argument("--take-stale", action="store_true", help="take over a claim whose heartbeat expired")
    claim.add_argument("--session", help="the session URL, recorded on the claim")
    claim.add_argument("--publish", action="store_true", help="commit the records and push your work branch")
    claim.set_defaults(run=cmd_claim)
    verify = commands.add_parser("verify", help="exit 0 when every claim of mine is still mine and pushed")
    verify.add_argument("ids", nargs="*", metavar="sd-XX-NNN")
    verify.set_defaults(run=cmd_verify)
    touch = commands.add_parser("touch", help="renew the heartbeat of my claims")
    touch.add_argument("ids", nargs="*", metavar="sd-XX-NNN")
    touch.add_argument("--publish", action="store_true")
    touch.set_defaults(run=cmd_touch)
    finish = commands.add_parser("finish", help="record a built deck")
    finish.add_argument("id", metavar="sd-XX-NNN")
    finish.add_argument("--canvas", required=True, help="the Moda canvas id, cvs_...")
    finish.add_argument("--url", required=True, help="the Moda editor link, https://moda.app/canvas/...")
    finish.add_argument("--slides", type=int, required=True)
    finish.add_argument("--size", default="1920x1080")
    finish.add_argument("--exports", choices=EXPORTS, default="pending",
                        help="done only when <id>.pptx and 01.png.. are in slides/")
    finish.add_argument("--publish", action="store_true")
    finish.set_defaults(run=cmd_finish)
    exported = commands.add_parser("exported", help="record that a finished deck's PPTX and PNG files are in its folder")
    exported.add_argument("id", metavar="sd-XX-NNN")
    exported.add_argument("--publish", action="store_true")
    exported.set_defaults(run=cmd_exported)
    release = commands.add_parser("release", help="give back lessons you will not build")
    release.add_argument("ids", nargs="+", metavar="sd-XX-NNN")
    release.add_argument("--publish", action="store_true")
    release.set_defaults(run=cmd_release)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = args.store.resolve()
    try:
        root = pathlib.Path(git_text(store, "rev-parse", "--show-toplevel"))
        context = Context(root, store, args.remote, args.owner or current_branch(root), args.offline)
        return args.run(context, args)
    except SlidesError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
