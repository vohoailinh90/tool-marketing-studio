"""scripts/sd101_check.py: the Vietnamese System Design store rules, on fixtures and on the real store."""

from __future__ import annotations

import ast
import contextlib
import copy
import importlib.metadata
import io
import json
import os
import re
import sys
import tempfile
import unicodedata
import unittest
from unittest import mock
from pathlib import Path

import yaml

from scripts import sd101_check as check

COMMIT = "b28380a4710c5ec9638ec037d4168e288f334cba"
SOURCE_PATH = "data/guides/one.md"
BLOB = "a" * 40
PIN = {"source_repository": "ByteByteGoHq/system-design-101", "source_commit_sha": COMMIT}
SNAPSHOT = f"https://github.com/ByteByteGoHq/system-design-101/blob/{COMMIT}/{SOURCE_PATH}"
TITLES = {"sd-01-001": "Bài một", "sd-01-002": "Bài hai", "sd-01-003": "Bài ba"}
FIGURE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>Sơ đồ</title><rect width="1" height="1"/></svg>'
README = "# Kho\n\n| ID | Bài |\n|---|---|\n| [sd-01-001](lessons/sd-01-001/lesson.md) | Bài một |\n"
GOOD_CLAIM = {"claim_vi": "Polling hỏi định kỳ.", "source": "https://www.rfc-editor.org/rfc/rfc6202.html", "section": "2.1"}
GOOD_EVIDENCE = {"url": "https://assets.bytebytego.com/d/1.png", "sha256": "a" * 64, "retrieved_on": "2026-10-12"}


def source_entry(lesson_id: str = "sd-01-001", title: str | None = "Bài một", snapshot: object = SNAPSHOT,
                 **changes: object) -> dict:
    """A complete source-map entry, as the real map records one."""
    entry = {"id": lesson_id, "title_vi": title, "title_source": "One", "source_url": "https://bytebytego.com/guides/one",
             "source_path": SOURCE_PATH, "source_body_reviewed": False, "source_blob_sha": BLOB,
             "source_snapshot_url": snapshot}
    entry.update(changes)
    return entry


def body_of(lesson_id: str = "sd-01-001") -> str:
    """A lesson that shows its figure and links the pinned source."""
    return (f"# Bài\n\n![Sơ đồ của bài](../../diagrams/{lesson_id}-main.svg)\n\nNội dung.\n\n"
            f"## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n")


BODY = body_of()


def happened(step: str, **extra: object) -> dict:
    """A verification step that happened, with the date and the evidence the checker asks for."""
    base = {"status": check.VERIFICATION_STEPS[step][1], "checked_on": "2026-10-12"}
    if step == "mobile":
        base.update(widths_px=[320, 375, 430], whole_lesson_no_horizontal_overflow=True, text_outside_viewbox=False,
                    evidence="Chromium rendered the lesson at each width.")
    base.update(extra)
    return base


def metadata(lesson_id: str = "sd-01-001", **changes: object) -> dict:
    """The metadata of a draft lesson whose source has been read, as DECISIONS.md describes it."""
    data = {
        "id": lesson_id,
        "title_vi": TITLES.get(lesson_id, "Bài"),
        "language": "vi",
        "kind": "flow",
        "content_status": "draft",
        "source_ref": lesson_id,
        "source_snapshot": {"repository": PIN["source_repository"], "commit_sha": COMMIT, "path": SOURCE_PATH,
                            "blob_sha": BLOB},
        "diagram": f"../diagrams/{lesson_id}-main.svg",
        "prerequisites": [],
        "related": [],
        "verification": {
            "source_body": happened("source_body"),
            "claims": {"status": "pending"},
            "technical_review": {"status": "pending", "reason": "integration"},
            "mobile": {"status": "pending"},
            "user_testing": {"status": "not_performed"},
        },
        "claims": [],
    }
    data.update(changes)
    return data


def all_happened() -> dict:
    """Every verification step done except the learner test, which DECISIONS.md keeps apart."""
    return {step: happened(step) for step in check.VERIFICATION_STEPS if step != "user_testing"} | {
        "user_testing": {"status": "not_performed"}}


class StoreCase(unittest.TestCase):
    """A one-lesson store in a temp directory; each test breaks one thing."""

    auto_progress = True  # problems() first brings progress.json in line with the source map and the lessons on disk

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.store = self.root / "store"
        self.source_map = self.root / "source-map.json"
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT)})
        self.write_lesson("sd-01-001")
        self.write_readme(README)

    def write_source_map(self, lessons: dict[str, tuple[str, str]]) -> None:
        # the fixture lessons share one source file, so when there are several they name each other
        data = {**PIN, "categories": [{"id": "sd-01", "lessons": [
            source_entry(lesson_id, title, snapshot,
                         **({"same_source_as": [other for other in lessons if other != lesson_id]}
                            if len(lessons) > 1 else {}))
            for lesson_id, (title, snapshot) in lessons.items()]}]}
        self.source_map.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def write_lesson(self, lesson_id: str, *, meta: object = None, body: str | None = None,
                     figure: str | bytes | None = FIGURE) -> Path:
        lesson_dir = self.store / "lessons" / lesson_id
        lesson_dir.mkdir(parents=True, exist_ok=True)
        (lesson_dir / "lesson.yaml").write_text(
            yaml.safe_dump({"id": lesson_id, "metadata_ref": f"../../metadata/{lesson_id}.json"}), encoding="utf-8")
        (lesson_dir / "lesson.md").write_text(body_of(lesson_id) if body is None else body, encoding="utf-8")
        self.write_metadata(lesson_id, metadata(lesson_id) if meta is None else meta)
        if figure is not None:
            self.write_figure(lesson_id, figure)
        return lesson_dir

    def write_metadata(self, lesson_id: str, data: object) -> None:
        (self.store / "metadata").mkdir(parents=True, exist_ok=True)
        (self.store / "metadata" / f"{lesson_id}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def write_figure(self, lesson_id: str, content: str | bytes = FIGURE) -> Path:
        (self.store / "diagrams").mkdir(parents=True, exist_ok=True)
        figure = self.store / "diagrams" / f"{lesson_id}-main.svg"
        figure.write_bytes(content.encode() if isinstance(content, str) else content)
        return figure

    def write_readme(self, text: str) -> None:
        self.store.mkdir(parents=True, exist_ok=True)
        (self.store / "README.md").write_text(text, encoding="utf-8")

    def sync_progress(self, **changes: object) -> None:
        """progress.json as it should be for the source map and the lessons on disk, with some fields changed."""
        try:
            entries = [lesson for category in json.loads(self.source_map.read_text(encoding="utf-8"))["categories"]
                       for lesson in category["lessons"]]
            on_disk = {path.name for path in (self.store / "lessons").iterdir() if path.is_dir()}
            written = [entry["id"] for entry in entries if entry["id"] in on_disk]
            following = next((entry["id"] for entry in entries if entry["id"] not in written), None)
            data = {"language": "vi", "total_occurrences": len(entries),
                    "total_source_documents": len({entry["source_path"] for entry in entries}),
                    "written_ids": written, "reviewed_ids": [], "next_id": following}
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            return  # a malformed source map: nothing to follow
        self.store.mkdir(parents=True, exist_ok=True)
        (self.store / "progress.json").write_text(json.dumps({**data, **changes}), encoding="utf-8")

    def problems(self) -> list[str]:
        if self.auto_progress:
            self.sync_progress()
        return [str(problem) for problem in check.check_store(self.store, self.source_map)]

    def meta(self, lesson_id: str = "sd-01-001", **changes: object) -> dict:
        return metadata(lesson_id, **changes)

    def assertProblem(self, fragment: str) -> None:
        found = self.problems()
        self.assertTrue(any(fragment in line for line in found), f"{fragment!r} not in {found}")


class RealStoreTests(unittest.TestCase):
    def test_the_real_store_passes_every_rule(self) -> None:
        problems = check.check_store(check.DEFAULT_STORE, check.DEFAULT_SOURCE_MAP, pin_roster=True)
        self.assertEqual([], [str(problem) for problem in problems])


class SourceMapPinTests(unittest.TestCase):
    """The real source map, altered one way at a time: the roster and the pinned URLs are guarded."""

    def check(self, change, *, pin_roster: bool = True) -> list[str]:
        data = json.loads(check.DEFAULT_SOURCE_MAP.read_text(encoding="utf-8"))
        change(data)
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "source-map.json"
            altered.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            problems = check.check_store(check.DEFAULT_STORE, altered, pin_roster=pin_roster)
        return [str(problem) for problem in problems if str(problem).startswith("source map")]

    def test_the_unaltered_source_map_has_no_problem(self) -> None:
        self.assertEqual([], self.check(lambda data: None))

    def test_removing_an_unwritten_entry_is_reported(self) -> None:
        def remove(data):
            del data["categories"][0]["lessons"][12]  # sd-01-013
        found = self.check(remove)
        self.assertTrue(any("first difference: ('sd-01', 49) instead of ('sd-01', 50)" in line for line in found), found)
        self.assertTrue(any("sd-01-014 should be sd-01-013" in line for line in found), found)

    def test_the_other_ways_to_change_the_roster_are_reported(self) -> None:
        def drop_last(data):
            data["categories"][-1]["lessons"].pop()

        def drop_group(data):
            data["categories"].pop(2)

        def add_entry(data):
            extra = dict(data["categories"][0]["lessons"][-1], id="sd-01-051")
            data["categories"][0]["lessons"].append(extra)

        def swap(data):
            lessons = data["categories"][1]["lessons"]
            lessons[0], lessons[1] = lessons[1], lessons[0]

        def renumber(data):
            data["categories"][4]["lessons"][0]["id"] = "sd-05-009"

        def empty(data):
            data["categories"] = []

        def rename_a_group_and_its_ids(data):
            group = data["categories"][-1]
            group["id"] = "sd-99"
            for number, lesson in enumerate(group["lessons"], 1):
                lesson["id"] = f"sd-99-{number:03d}"

        def rename_a_group_only(data):
            data["categories"][5]["id"] = "sd-66"

        def swap_two_groups(data):
            data["categories"][2], data["categories"][3] = data["categories"][3], data["categories"][2]

        def renumber_a_group_as_another(data):
            for number, lesson in enumerate(data["categories"][0]["lessons"], 1):
                lesson["id"] = f"sd-02-{number:03d}"
            data["categories"][0]["id"] = "sd-02"

        self.assertTrue(any("first difference: ('sd-15', 11) instead of ('sd-15', 12)" in line for line in self.check(drop_last)))
        for name, change in {"the last entry removed": drop_last, "a group removed": drop_group,
                             "an entry added": add_entry, "two entries swapped": swap, "an id renumbered": renumber,
                             "no groups": empty, "a group and its ids renamed": rename_a_group_and_its_ids,
                             "a group renamed, its ids kept": rename_a_group_only, "two groups swapped": swap_two_groups,
                             "a group renumbered as another": renumber_a_group_as_another}.items():
            with self.subTest(change=name):
                self.assertTrue(self.check(change), name)

    def test_the_roster_is_pinned_only_for_the_real_source_map(self) -> None:
        def remove(data):
            del data["categories"][0]["lessons"][12]
        self.assertEqual([], self.check(remove, pin_roster=False))

    def test_the_command_line_pins_the_default_source_map_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "source-map.json"
            copy.write_bytes(check.DEFAULT_SOURCE_MAP.read_bytes())
            with mock.patch.object(check, "EXPECTED_GROUPS", (("sd-01", 1),)), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, check.main([]))
                self.assertEqual(1, check.main(["--source-map", str(check.DEFAULT_SOURCE_MAP.parent / ".." /
                                                                   check.DEFAULT_SOURCE_MAP.parent.name /
                                                                   check.DEFAULT_SOURCE_MAP.name)]))
                self.assertEqual(0, check.main(["--source-map", str(copy)]))

    def test_a_moving_snapshot_url_is_reported_even_if_the_lesson_links_it(self) -> None:
        def moving(data):
            entry = data["categories"][0]["lessons"][0]
            entry["source_snapshot_url"] = f"https://github.com/ByteByteGoHq/system-design-101/blob/main/{entry['source_path']}"
        found = self.check(moving)
        self.assertTrue(any("sd-01-001: source_snapshot_url is not" in line for line in found), found)

    def test_every_other_wrong_snapshot_url_is_reported(self) -> None:
        def entry_of(data):
            return data["categories"][0]["lessons"][1]

        def set_url(url):
            return lambda data: entry_of(data).update(source_snapshot_url=url)

        path, commit = "data/guides/x.md", COMMIT
        for name, change in {
            "another repository": set_url(f"https://github.com/someone/else/blob/{commit}/{path}"),
            "another commit": set_url(f"https://github.com/ByteByteGoHq/system-design-101/blob/{'0' * 40}/{path}"),
            "a short commit": set_url(f"https://github.com/ByteByteGoHq/system-design-101/blob/b28380a/{path}"),
            "another path": set_url(f"https://github.com/ByteByteGoHq/system-design-101/blob/{commit}/data/other.md"),
            "a tree URL": set_url(f"https://github.com/ByteByteGoHq/system-design-101/tree/{commit}/{path}"),
            "a raw URL": set_url(f"https://raw.githubusercontent.com/ByteByteGoHq/system-design-101/{commit}/{path}"),
            "a trailing fragment": lambda data: entry_of(data).update(
                source_snapshot_url=entry_of(data)["source_snapshot_url"] + "#L1"),
            "no URL": lambda data: entry_of(data).pop("source_snapshot_url"),
            "a null URL": set_url(None),
            "a null source path with a matching tail": lambda data: entry_of(data).update(
                source_path=None, source_snapshot_url=f"https://github.com/ByteByteGoHq/system-design-101/blob/{commit}/None"),
            "a numeric source path with a matching tail": lambda data: entry_of(data).update(
                source_path=5, source_snapshot_url=f"https://github.com/ByteByteGoHq/system-design-101/blob/{commit}/5"),
            "an empty source path": lambda data: entry_of(data).update(
                source_path="", source_snapshot_url=f"https://github.com/ByteByteGoHq/system-design-101/blob/{commit}/"),
        }.items():
            with self.subTest(change=name):
                self.assertTrue(any("sd-01-002: source_snapshot_url is not" in line
                                    for line in self.check(change, pin_roster=False)), name)

    def test_the_map_needs_its_own_pinned_commit_and_repository(self) -> None:
        for name, change in {
            "no commit": lambda data: data.pop("source_commit_sha"),
            "a short commit": lambda data: data.update(source_commit_sha="b28380a"),
            "an upper-case commit": lambda data: data.update(source_commit_sha=data["source_commit_sha"].upper()),
            "a branch name": lambda data: data.update(source_commit_sha="main"),
            "no repository": lambda data: data.pop("source_repository"),
            "a repository without an owner": lambda data: data.update(source_repository="system-design-101"),
            "a null commit": lambda data: data.update(source_commit_sha=None),
        }.items():
            with self.subTest(change=name):
                self.assertTrue(any("needs a source_repository" in line
                                    for line in self.check(change, pin_roster=False)), name)

    def entry(self, data, number=1):
        return data["categories"][0]["lessons"][number]  # sd-01-002 by default

    def test_a_missing_entry_field_is_reported(self) -> None:
        for key in sorted(check.SOURCE_ENTRY_KEYS - {"id"}):
            with self.subTest(key=key):
                found = self.check(lambda data: self.entry(data).pop(key), pin_roster=False)
                self.assertTrue(any(f"sd-01-002 is missing {key}" in line or f"sd-01-002: source_snapshot_url" in line
                                    for line in found), found)

    def test_an_entry_field_of_the_wrong_kind_is_reported(self) -> None:
        cases = {
            "source_body_reviewed": ["yes", 1, 0, None, "true", []],
            "source_blob_sha": ["a" * 39, "A" * 40, "g" * 40, None, 5, "", ["a" * 40]],
            "title_source": ["", "  ", None, 5, ["x"]],
            "source_path": ["", "  ", None, 5],
            "source_url": ["", "not a url", "ftp://bytebytego.com/x", None, 5, "https://"],
            "title_vi": ["", "  ", 5, ["x"], {"a": 1}, True],
        }
        for key, values in cases.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    found = self.check(lambda data: self.entry(data).update({key: value}), pin_roster=False)
                    self.assertTrue(any(line.startswith("source map: sd-01-002 ") or "sd-01-002:" in line
                                        for line in found), found)

    def test_a_null_title_vi_is_allowed_and_a_string_is_too(self) -> None:
        self.assertEqual([], self.check(lambda data: self.entry(data).update(title_vi=None), pin_roster=False))
        self.assertEqual([], self.check(lambda data: self.entry(data).update(title_vi="Tiêu đề"), pin_roster=False))
        self.assertEqual([], self.check(lambda data: self.entry(data).update(source_body_reviewed=True),
                                        pin_roster=False))

    def test_progress_fields_do_not_belong_in_the_source_map(self) -> None:
        for key in ("status", "content_status", "verification", "learner_test"):
            with self.subTest(key=key):
                found = self.check(lambda data: self.entry(data).update({key: "draft"}), pin_roster=False)
                self.assertTrue(any(f"sd-01-002 has unknown keys {key}" in line for line in found), found)

    def test_same_source_entries_must_name_each_other(self) -> None:
        def entry_of(data, lesson_id):
            return next(lesson for category in data["categories"] for lesson in category["lessons"]
                        if lesson["id"] == lesson_id)

        cases = {
            "one side dropped": (lambda data: entry_of(data, "sd-10-023").pop("same_source_as"),
                                 "sd-01-045: same_source_as names sd-10-023, which does not name sd-01-045 back"),
            "a missing partner": (lambda data: entry_of(data, "sd-01-045").update(same_source_as=["sd-99-999"]),
                                  "sd-01-045: same_source_as names sd-99-999, which is not another entry"),
            "itself": (lambda data: entry_of(data, "sd-01-045").update(same_source_as=["sd-01-045"]),
                       "sd-01-045: same_source_as names sd-01-045, which is not another entry"),
            "another source path": (lambda data: entry_of(data, "sd-10-023").update(
                source_path="data/guides/other.md",
                source_snapshot_url=f"https://github.com/ByteByteGoHq/system-design-101/blob/{data['source_commit_sha']}/data/guides/other.md"),
                                    "sd-01-045: same_source_as names sd-10-023, which has another source_path"),
            "not a list": (lambda data: entry_of(data, "sd-01-045").update(same_source_as="sd-10-023"),
                           "sd-01-045: same_source_as must be a non-empty list of ids"),
            "an empty list": (lambda data: entry_of(data, "sd-01-045").update(same_source_as=[]),
                              "sd-01-045: same_source_as must be a non-empty list of ids"),
            "a list of numbers": (lambda data: entry_of(data, "sd-01-045").update(same_source_as=[5]),
                                  "sd-01-045: same_source_as must be a non-empty list of ids"),
        }
        for name, (change, expected) in cases.items():
            with self.subTest(change=name):
                found = self.check(change, pin_roster=False)
                self.assertTrue(any(expected in line for line in found), found)

    def test_two_entries_sharing_a_source_file_must_say_so(self) -> None:
        def share(data):
            first, second = data["categories"][0]["lessons"][4], data["categories"][0]["lessons"][5]
            second["source_path"] = first["source_path"]
            second["source_snapshot_url"] = first["source_snapshot_url"]
        found = self.check(share, pin_roster=False)
        self.assertTrue(any("sd-01-005: shares its source_path with sd-01-006 but does not list them" in line
                            for line in found), found)
        self.assertTrue(any("sd-01-006: shares its source_path with sd-01-005 but does not list them" in line
                            for line in found), found)

    ODD = [None, True, 0, 1.5, "", " ", "sd-01-001", "x" * 300, [], [None], [{}], [[1]], [5], ["sd-01-001"],
           {}, {"a": 1}, [{"a": 1}]]

    def load(self, change, *, pin_roster: bool = True) -> list[str]:
        """Only the source-map rules, on an altered copy of the real map (fast enough to sweep)."""
        data = json.loads(check.DEFAULT_SOURCE_MAP.read_text(encoding="utf-8"))
        change(data)
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "source-map.json"
            altered.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return [str(problem) for problem in check.load_source_map(altered, pin_roster)[2]]

    def test_an_odd_value_in_any_source_map_field_is_reported_not_raised(self) -> None:
        keys = sorted(check.SOURCE_ENTRY_KEYS) + ["same_source_as", "unknown"]
        for key in keys:
            for value in self.ODD:
                for lesson in (1, 44):  # sd-01-002, and sd-01-045 which has a same-source partner
                    with self.subTest(key=key, value=value, lesson=lesson):
                        self.load(lambda data: self.entry(data, lesson).update({key: value}))

    def test_an_odd_value_for_a_map_level_field_or_a_group_is_reported_not_raised(self) -> None:
        for key in ("source_repository", "source_commit_sha", "categories", "schema_version"):
            for value in self.ODD:
                with self.subTest(key=key, value=value):
                    self.load(lambda data: data.update({key: value}))
        for key in ("id", "lessons", "extra"):
            for value in self.ODD:
                with self.subTest(group=key, value=value):
                    self.load(lambda data: data["categories"][0].update({key: value}))

    def test_an_odd_group_or_entry_is_reported_not_raised(self) -> None:
        for value in self.ODD:
            with self.subTest(value=value):
                self.load(lambda data: data["categories"].insert(3, value))
                self.load(lambda data: data["categories"][0]["lessons"].insert(5, value))
                self.load(lambda data: data["categories"][0]["lessons"].__setitem__(2, value))

    def test_an_odd_value_in_the_entry_of_a_written_lesson_is_reported_not_raised(self) -> None:
        for key in ("id", "title_vi", "source_path", "source_snapshot_url", "source_blob_sha", "same_source_as"):
            for value in self.ODD:
                with self.subTest(key=key, value=value):
                    self.check(lambda data: self.entry(data, 0).update({key: value}))

    def check_text(self, text: str, *, pin_roster: bool = True) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            altered = Path(tmp) / "source-map.json"
            altered.write_text(text, encoding="utf-8")
            return [str(problem) for problem in check.load_source_map(altered, pin_roster)[2]]

    def test_a_key_named_twice_in_the_source_map_is_reported(self) -> None:
        text = check.DEFAULT_SOURCE_MAP.read_text(encoding="utf-8")
        data = json.loads(text)
        commit, blob = data["source_commit_sha"], data["categories"][0]["lessons"][0]["source_blob_sha"]
        for name, (old, new) in {
            "the pinned commit": (f'"source_commit_sha": "{commit}"', f'"source_commit_sha": "{"0" * 40}", "source_commit_sha": "{commit}"'),
            "a blob id": (f'"source_blob_sha": "{blob}"', f'"source_blob_sha": "{blob}", "source_blob_sha": "{blob}"'),
            "the schema version": ('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
        }.items():
            with self.subTest(key=name):
                self.assertEqual(1, text.count(old))
                found = self.check_text(text.replace(old, new, 1))
                self.assertTrue(any("cannot be read: duplicate key" in line for line in found), found)

    def test_a_source_path_that_a_url_would_read_differently_is_reported(self) -> None:
        for path in ["../README.md", "/data/x.md", "data//x.md", "./data/x.md", "data/./x.md", "data/../x.md",
                     "data/x.md/", "data/a b.md", "data/a#b.md", "data/a?b.md", "data\\a.md", "data/a\tb.md", "..",
                     ".", "/", "./", "data/.", "data/..", "data/", "data/a\x7fb.md"]:
            def change(data, path=path):
                entry = self.entry(data)
                entry["source_path"] = path
                entry["source_snapshot_url"] = f"https://github.com/{data['source_repository']}/blob/{data['source_commit_sha']}/{path}"
            with self.subTest(path=path):
                found = self.check(change, pin_roster=False)
                self.assertTrue(any("sd-01-002 source_path must be a normalised path" in line for line in found), found)

    def test_the_real_source_paths_with_an_apostrophe_or_a_plus_are_fine(self) -> None:
        data = json.loads(check.DEFAULT_SOURCE_MAP.read_text(encoding="utf-8"))
        paths = [lesson["source_path"] for category in data["categories"] for lesson in category["lessons"]]
        self.assertTrue(any("'" in path for path in paths) and any("+" in path for path in paths))
        self.assertEqual([], self.check(lambda data: None))

    @staticmethod
    def move_to_another_repository(data) -> None:
        old = data["source_repository"]
        data["source_repository"] = "someone/else"
        for category in data["categories"]:
            for lesson in category["lessons"]:
                lesson["source_snapshot_url"] = lesson["source_snapshot_url"].replace(old, "someone/else")

    def test_the_top_level_records_of_the_real_map_are_pinned(self) -> None:
        cases = {
            "no schema version": lambda data: data.pop("schema_version"),
            "another schema version": lambda data: data.update(schema_version=2),
            "a boolean schema version": lambda data: data.update(schema_version=True),
            "another language": lambda data: data.update(language="en"),
            "another repository": self.move_to_another_repository,
            "no tree sha": lambda data: data.pop("source_tree_sha"),
            "a short tree sha": lambda data: data.update(source_tree_sha="7c914cc"),
            "a corrupted readme blob sha": lambda data: data.update(source_readme_blob_sha="z" * 40),
            "no readme blob sha": lambda data: data.pop("source_readme_blob_sha"),
            "no observation date": lambda data: data.pop("observed_on"),
            "an impossible observation date": lambda data: data.update(observed_on="2026-02-30"),
            "a free-text observation date": lambda data: data.update(observed_on="yesterday"),
            "a numeric observation date": lambda data: data.update(observed_on=20261012),
            "no note": lambda data: data.pop("note"),
            "an empty note": lambda data: data.update(note="  "),
            "an unknown top-level key": lambda data: data.update(status="draft"),
        }
        for name, change in cases.items():
            with self.subTest(change=name):
                found = self.check(change)
                self.assertTrue(any(("top-level" in line or "must be" in line) for line in found), found)
                self.assertEqual([], self.check(change, pin_roster=False), "only the real map is held to its top-level records")

    def test_the_groups_of_the_real_map_are_pinned(self) -> None:
        cases = {
            "no title_vi": lambda data: data["categories"][2].pop("title_vi"),
            "an empty title_vi": lambda data: data["categories"][2].update(title_vi=""),
            "a null title_vi": lambda data: data["categories"][2].update(title_vi=None),
            "no title_source": lambda data: data["categories"][2].pop("title_source"),
            "an empty title_source": lambda data: data["categories"][2].update(title_source=""),
            "a blank title_source": lambda data: data["categories"][2].update(title_source="  "),
            "a numeric title_source": lambda data: data["categories"][2].update(title_source=5),
            "an unknown group key": lambda data: data["categories"][2].update(status="draft"),
        }
        for name, change in cases.items():
            with self.subTest(change=name):
                found = self.check(change)
                self.assertTrue(any("group sd-03 needs exactly" in line for line in found), found)

    def test_re_pinning_every_entry_and_the_map_to_one_new_commit_is_allowed(self) -> None:
        new = "0123456789abcdef0123456789abcdef01234567"

        def repin(data):
            old = data["source_commit_sha"]
            data["source_commit_sha"] = new
            for category in data["categories"]:
                for lesson in category["lessons"]:
                    lesson["source_snapshot_url"] = lesson["source_snapshot_url"].replace(old, new)
            # a lesson's metadata records the commit it was written from; the real store is not re-pinned here
        found = self.check(repin)
        self.assertEqual([], found)


class LessonFilesTests(StoreCase):
    """lessons/<id>/: lesson.md, and lesson.yaml that only points at the metadata."""

    def test_a_valid_store_has_no_problems(self) -> None:
        self.assertEqual([], self.problems())

    def test_a_missing_file_is_reported(self) -> None:
        lesson_dir = self.store / "lessons" / "sd-01-001"
        for path, fragment in {lesson_dir / "lesson.yaml": "lesson.yaml is missing",
                               lesson_dir / "lesson.md": "lesson.md is missing",
                               self.store / "metadata" / "sd-01-001.json": "metadata/sd-01-001.json is missing",
                               self.store / "diagrams" / "sd-01-001-main.svg": "diagrams/sd-01-001-main.svg is missing",
                               }.items():
            with self.subTest(file=path.name):
                self.write_lesson("sd-01-001")
                path.unlink()
                self.assertProblem(fragment)

    def test_a_lesson_yaml_that_does_not_parse_is_reported_not_raised(self) -> None:
        lesson_dir = self.store / "lessons" / "sd-01-001"
        for name, text in {"invalid syntax": "id: [unclosed\n", "a tab": "id:\n\t- x\n",
                           "deep nesting": "[" * 100_000 + "]" * 100_000}.items():
            with self.subTest(file=name):
                (lesson_dir / "lesson.yaml").write_text(text, encoding="utf-8")
                self.assertProblem("lesson.yaml does not parse")
        with self.subTest(file="not utf-8"):
            (lesson_dir / "lesson.yaml").write_bytes(b"id: \xff\xfe\n")
            self.assertProblem("lesson.yaml does not parse")

    def test_a_key_named_twice_in_lesson_yaml_is_reported(self) -> None:
        lesson_dir = self.store / "lessons" / "sd-01-001"
        base = "id: sd-01-001\nmetadata_ref: ../../metadata/sd-01-001.json\n"
        for name, text in {"a key with another value": base + "id: sd-01-002\n",
                           "a key with the same value": base + "id: sd-01-001\n",
                           "a quoted and an unquoted spelling": base + "'id': sd-01-002\n"}.items():
            with self.subTest(file=name):
                (lesson_dir / "lesson.yaml").write_text(text, encoding="utf-8")
                self.assertProblem("duplicate key")

    def test_an_unhashable_yaml_key_is_reported_not_raised(self) -> None:
        (self.store / "lessons" / "sd-01-001" / "lesson.yaml").write_text("? [a, b]\n: c\nid: sd-01-001\n", encoding="utf-8")
        self.assertProblem("lesson.yaml does not parse")

    def test_a_yaml_merge_key_and_repeated_values_are_not_duplicate_keys(self) -> None:
        lesson_dir = self.store / "lessons" / "sd-01-001"
        (lesson_dir / "lesson.yaml").write_text(
            "id: sd-01-001\nmetadata_ref: ../../metadata/sd-01-001.json\nbase: &b {id: sd-01-001}\nextra: {<<: *b, id: x}\n",
            encoding="utf-8")
        self.assertFalse(any("does not parse" in line for line in self.problems()), self.problems())

    def test_lesson_yaml_only_points_at_the_metadata(self) -> None:
        lesson_dir = self.store / "lessons" / "sd-01-001"
        ref = "../../metadata/sd-01-001.json"
        cases = {
            "a status copied into it": (f"id: sd-01-001\nmetadata_ref: {ref}\ncontent_status: draft\n", "lesson.yaml keys are"),
            "no metadata_ref": ("id: sd-01-001\n", "lesson.yaml keys are"),
            "no id": (f"metadata_ref: {ref}\n", "lesson.yaml keys are"),
            "an id that is not the directory name": (f"id: sd-01-002\nmetadata_ref: {ref}\n", "expected the directory name"),
            "a ref to another lesson": ("id: sd-01-001\nmetadata_ref: ../../metadata/sd-01-002.json\n", "metadata_ref must be"),
            "a ref without the directory": ("id: sd-01-001\nmetadata_ref: sd-01-001.json\n", "metadata_ref must be"),
            "an absolute ref": ("id: sd-01-001\nmetadata_ref: /metadata/sd-01-001.json\n", "metadata_ref must be"),
            "a null ref": ("id: sd-01-001\nmetadata_ref:\n", "metadata_ref must be"),
            "a list": ("- id: sd-01-001\n", "lesson.yaml is not a mapping"),
            "a string": ("hello\n", "lesson.yaml is not a mapping"),
            "empty": ("", "lesson.yaml is not a mapping"),
        }
        for name, (text, fragment) in cases.items():
            with self.subTest(file=name):
                (lesson_dir / "lesson.yaml").write_text(text, encoding="utf-8")
                self.assertProblem(fragment)

    @staticmethod
    def refusing(name: str):
        """Reading a file called `name` fails as it does for a file the process may not open."""
        real = Path.read_text

        def read_text(path, *args, **kwargs):
            if path.name == name:
                raise PermissionError(13, "Permission denied", str(path))
            return real(path, *args, **kwargs)
        return mock.patch.object(Path, "read_text", read_text)

    def test_a_file_the_filesystem_refuses_is_reported_not_raised(self) -> None:
        (self.store / "PROGRESS.md").write_text("# x\n", encoding="utf-8")
        (self.store / "lessons" / "sd-01-001.md").write_text("[x](sd-01-001/lesson.md)\n", encoding="utf-8")
        cases = {"lesson.md": "sd-01-001: lesson.md cannot be read", "lesson.yaml": "sd-01-001: lesson.yaml does not parse",
                 "README.md": "README.md: cannot be read", "PROGRESS.md": "PROGRESS.md: cannot be read",
                 "sd-01-001.md": "lessons: sd-01-001.md cannot be read",
                 "sd-01-001.json": "metadata/sd-01-001.json: cannot be read", "progress.json": "progress.json: cannot be read"}
        for name, fragment in cases.items():
            with self.subTest(file=name), self.refusing(name):
                self.assertProblem(fragment)

    def test_text_that_is_not_utf8_is_reported_not_raised(self) -> None:
        (self.store / "lessons" / "sd-01-001" / "lesson.md").write_bytes(BODY.encode() + b"\xff\xfe")
        self.assertProblem("lesson.md is not valid UTF-8 text")
        self.write_lesson("sd-01-001")
        (self.store / "README.md").write_bytes(README.encode() + b"\xff\xfe")
        self.assertProblem("README.md: is not valid UTF-8 text")


class MetadataRuleTests(StoreCase):
    """metadata/<id>.json: the one record of a lesson's status and evidence."""

    def put(self, **changes: object) -> None:
        """Rewrite sd-01-001's metadata; a claims step that happened comes with a claim unless claims is given."""
        data = self.meta(**changes)
        claims_step = data["verification"].get("claims") if isinstance(data["verification"], dict) else None
        if "claims" not in changes and isinstance(claims_step, dict) and claims_step.get("status") == "checked":
            data["claims"] = [GOOD_CLAIM]
        self.write_metadata("sd-01-001", data)

    def problems_of_metadata(self) -> list[str]:
        return [line for line in self.problems() if line.startswith("metadata/sd-01-001.json")]

    def test_a_metadata_file_that_cannot_be_read_is_reported_not_raised(self) -> None:
        path = self.store / "metadata" / "sd-01-001.json"
        cases = {"invalid json": b"{", "empty": b"", "not utf-8": b"\xff\xfe{}"}
        for name, content in cases.items():
            with self.subTest(file=name):
                path.write_bytes(content)
                self.assertProblem("metadata/sd-01-001.json: cannot be read")
                self.assertEqual(1, len(self.problems_of_metadata()), self.problems_of_metadata())
        for name, content in {"a list": b"[]", "a string": b'"x"', "null": b"null", "a number": b"3"}.items():
            with self.subTest(file=name):
                path.write_bytes(content)
                self.assertProblem("metadata/sd-01-001.json: is not a JSON object")

    def test_a_key_named_twice_in_the_metadata_is_reported(self) -> None:
        text = json.dumps(self.meta())
        for name, (old, new) in {"a top-level key": ('"language": "vi"', '"language": "en", "language": "vi"'),
                                 "a nested key": ('"status": "read"', '"status": "pending", "status": "read"')}.items():
            with self.subTest(key=name):
                self.assertEqual(1, text.count(old))
                (self.store / "metadata" / "sd-01-001.json").write_text(text.replace(old, new, 1), encoding="utf-8")
                self.assertProblem("duplicate key")

    def test_unknown_or_missing_keys_are_reported(self) -> None:
        data = self.meta()
        data["status"] = "draft"
        self.write_metadata("sd-01-001", data)
        self.assertProblem("has unknown keys status")
        for key in sorted(check.METADATA_REQUIRED):
            with self.subTest(missing=key):
                data = self.meta()
                del data[key]
                self.write_metadata("sd-01-001", data)
                self.assertProblem(f"is missing {key}")

    def test_the_optional_keys_may_be_left_out(self) -> None:
        self.assertEqual([], self.problems())
        self.assertTrue(check.METADATA_OPTIONAL.isdisjoint(self.meta()))

    def test_an_id_that_is_not_the_file_name_is_reported(self) -> None:
        self.put(id="sd-01-002")
        self.assertProblem("expected the file name")

    def test_an_id_missing_from_the_source_map_is_reported(self) -> None:
        self.write_source_map({"sd-09-009": ("Khác", SNAPSHOT)})
        self.assertProblem("id is not in the source map")

    def test_a_title_that_differs_from_the_source_map_is_reported(self) -> None:
        self.put(title_vi="Tiêu đề khác")
        self.assertProblem("title_vi differs")

    def test_a_null_or_empty_title_is_reported(self) -> None:
        self.write_source_map({"sd-01-001": (None, SNAPSHOT)})
        self.put(title_vi=None)
        self.assertProblem("title_vi must be a non-empty string")
        self.write_source_map({"sd-01-001": ("", SNAPSHOT)})
        self.put(title_vi="  ")
        self.assertProblem("title_vi must be a non-empty string")

    def test_the_language_kind_and_diagram_are_checked(self) -> None:
        for key, value, fragment in [("language", "en", "language must be 'vi'"), ("language", None, "language must be 'vi'"),
                                     ("kind", "", "kind must be a non-empty string"), ("kind", 5, "kind must be a non-empty string"),
                                     ("diagram", "../diagrams/sd-01-002-main.svg", "diagram must be ../diagrams/sd-01-001-main.svg"),
                                     ("diagram", "diagrams/sd-01-001-main.svg", "diagram must be"),
                                     ("diagram", None, "diagram must be")]:
            with self.subTest(key=key, value=value):
                self.put(**{key: value})
                self.assertProblem(fragment)

    def test_a_status_outside_the_vocabulary_is_reported(self) -> None:
        for status in ("approved", "drafted", "planned", "", None, ["draft"]):
            with self.subTest(status=status):
                self.put(content_status=status)
                self.assertProblem("content_status")

    def test_done_needs_the_technical_review_and_the_mobile_check(self) -> None:
        for step in check.DONE_NEEDS:
            with self.subTest(missing=step):
                verification = all_happened()
                verification[step] = {"status": "pending"}
                self.put(content_status="done", verification=verification)
                self.assertProblem("done needs technical_review and mobile to have happened")
        self.put(content_status="done", verification=all_happened())
        self.assertEqual([], self.problems())

    def test_done_does_not_wait_for_the_learner_test_and_review_does_not_need_either_step(self) -> None:
        self.assertEqual("not_performed", all_happened()["user_testing"]["status"])
        self.put(content_status="done", verification=all_happened())
        self.assertEqual([], self.problems())
        self.put(content_status="review")
        self.assertEqual([], self.problems())

    def test_the_verification_record_has_exactly_the_five_steps(self) -> None:
        for name, value in {"a step missing": {k: v for k, v in all_happened().items() if k != "mobile"},
                            "a step added": {**all_happened(), "learner_test": "done"}, "a list": [], "null": None,
                            "a string": "done"}.items():
            with self.subTest(verification=name):
                self.put(verification=value)
                self.assertProblem("verification must have exactly")

    def test_a_step_state_outside_its_vocabulary_is_reported(self) -> None:
        for step, (initial, completed) in check.VERIFICATION_STEPS.items():
            for value in ("done", "ok", "", None, 5, ["pending"], {"status": "pending"}):
                with self.subTest(step=step, value=value):
                    verification = all_happened()
                    verification[step] = {"status": value}
                    self.put(verification=verification)
                    self.assertProblem(f"verification {step} status {value!r} is not {initial} or {completed}")
            with self.subTest(step=step, value="a step that is not an object"):
                self.put(verification={**all_happened(), step: "checked"})
                self.assertProblem(f"verification {step} status None is not {initial} or {completed}")

    def test_a_step_that_happened_needs_a_real_date(self) -> None:
        for step in check.VERIFICATION_STEPS:
            if step == "user_testing":
                continue
            for date in (None, "", "yesterday", "2026-02-30", "2026-10-12 12:00:00", 20261012, ["2026-10-12"]):
                with self.subTest(step=step, date=date):
                    verification = all_happened()
                    verification[step] = {**happened(step), "checked_on": date}
                    self.put(verification=verification)
                    self.assertProblem(f"verification {step} is {check.VERIFICATION_STEPS[step][1]} but has no real checked_on date")
            with self.subTest(step=step, date="missing"):
                verification = all_happened()
                del verification[step]["checked_on"]
                self.put(verification=verification)
                self.assertProblem("has no real checked_on date")

    def test_a_step_that_has_not_happened_needs_no_date(self) -> None:
        self.assertEqual([], self.problems_of_metadata())
        self.assertNotIn("checked_on", self.meta()["verification"]["claims"])

    def test_a_user_test_that_happened_is_dated_too(self) -> None:
        self.put(verification={**all_happened(), "user_testing": {"status": "performed"}})
        self.assertProblem("verification user_testing is performed but has no real checked_on date")
        self.put(verification={**all_happened(), "user_testing": happened("user_testing")})
        self.assertEqual([], self.problems())

    def test_a_mobile_check_records_widths_and_no_overflow(self) -> None:
        cases = {
            "no widths": ({"widths_px": None}, "mobile widths_px must be a list"),
            "no 320": ({"widths_px": [375, 430]}, "mobile widths_px must be a list"),
            "an empty list": ({"widths_px": []}, "mobile widths_px must be a list"),
            "a string width": ({"widths_px": [320, "375"]}, "mobile widths_px must be a list"),
            "a boolean width": ({"widths_px": [320, True]}, "mobile widths_px must be a list"),
            "a negative width": ({"widths_px": [320, -1]}, "mobile widths_px must be a list"),
            "a width that is not a list": ({"widths_px": 320}, "mobile widths_px must be a list"),
            "overflow reported": ({"whole_lesson_no_horizontal_overflow": False}, "whole_lesson_no_horizontal_overflow must be true"),
            "overflow not recorded": ({"whole_lesson_no_horizontal_overflow": None}, "whole_lesson_no_horizontal_overflow must be true"),
            "text outside the viewBox": ({"text_outside_viewbox": True}, "text_outside_viewbox must be false"),
            "text outside not recorded": ({"text_outside_viewbox": None}, "text_outside_viewbox must be false"),
            "the older overflow flag set": ({"overflow": True}, "mobile overflow must be false"),
            "no evidence": ({"evidence": ""}, "mobile needs evidence text"),
            "evidence that is not text": ({"evidence": 5}, "mobile needs evidence text"),
        }
        for name, (changes, fragment) in cases.items():
            with self.subTest(case=name):
                self.put(verification={**all_happened(), "mobile": happened("mobile", **changes)})
                self.assertProblem(fragment)
        for extra in ({"overflow": False}, {"minimum_diagram_text_px": 14.4}, {"widths_px": [320]}):
            with self.subTest(accepted=extra):
                self.put(verification={**all_happened(), "mobile": happened("mobile", **extra)})
                self.assertEqual([], self.problems())

    def test_a_mobile_check_that_has_not_happened_is_not_held_to_those_rules(self) -> None:
        self.put(verification={**all_happened(), "mobile": {"status": "pending", "widths_px": "later"}})
        self.assertEqual([], self.problems())

    def test_claims_are_statements_with_an_http_source(self) -> None:
        url = "https://www.rfc-editor.org/rfc/rfc6202.html"
        good = {"claim_vi": "Polling hỏi định kỳ.", "source": url, "section": "2.1"}
        for claims in ([good], [{**good, "id": "polling"}], [{"claim_vi": "x", "sources": [url, url + "#a"]}],
                       [{"claim_vi": "x", "source": url, "checked_on": "2026-10-12", "result": "ok"}]):
            with self.subTest(claims=claims):
                self.put(claims=claims)
                self.assertEqual([], self.problems())
        cases = {
            "not a list": ({"a": 1}, "claims must be a list"),
            "an entry that is not an object": (["x"], "claim 1 is not an object"),
            "no statement": ([{"source": url}], "claim 1 needs a claim_vi"),
            "a blank statement": ([{"claim_vi": " ", "source": url}], "claim 1 needs a claim_vi"),
            "no source": ([{"claim_vi": "x"}], "claim 1 needs an http(s) source URL"),
            "a source that is not a URL": ([{"claim_vi": "x", "source": "rfc 6202"}], "needs an http(s) source URL"),
            "an ftp source": ([{"claim_vi": "x", "source": "ftp://example.com/a"}], "needs an http(s) source URL"),
            "a null source": ([{"claim_vi": "x", "source": None}], "needs an http(s) source URL"),
            "sources that is not a list": ([{"claim_vi": "x", "sources": url}], "needs an http(s) source URL"),
            "an empty sources list": ([{"claim_vi": "x", "sources": []}], "needs an http(s) source URL"),
            "one bad source among good ones": ([{"claim_vi": "x", "sources": [url, "nope"]}], "needs an http(s) source URL"),
            "a source and a sources that is not a list": ([{"claim_vi": "x", "source": url, "sources": url}], "needs an http(s) source URL"),
            "a blank id": ([{**good, "id": " "}], "claim 1 id must be a non-empty string"),
            "the second claim is the bad one": ([good, {"source": url}], "claim 2 needs a claim_vi"),
        }
        for name, (claims, fragment) in cases.items():
            with self.subTest(case=name):
                self.put(claims=claims)
                self.assertProblem(fragment)

    def test_a_checked_claims_step_needs_a_claim(self) -> None:
        self.put(verification={**all_happened(), "claims": happened("claims")}, claims=[])
        self.assertProblem("claims is empty, but the claims step is marked checked")
        self.put(verification={**all_happened(), "claims": happened("claims")})
        self.assertEqual([], self.problems())
        self.put(claims=[])
        self.assertEqual([], self.problems())

    def test_source_ref_names_the_lessons_own_source_entry(self) -> None:
        self.put(source_ref="sd-01-002")
        self.assertProblem("source_ref 'sd-01-002' is not in the source map")
        for value in (None, 5, ["sd-01-001"], ""):
            with self.subTest(source_ref=value):
                self.put(source_ref=value)
                self.assertProblem(f"source_ref {value!r} is not in the source map")

    def test_source_ref_may_name_an_entry_that_shares_the_source_file(self) -> None:
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT), "sd-01-002": ("Bài hai", SNAPSHOT)})
        self.write_lesson("sd-01-002")
        self.write_readme(README + "| [sd-01-002](lessons/sd-01-002/lesson.md) | Bài hai |\n")
        self.put(source_ref="sd-01-002")
        self.assertEqual([], self.problems())
        other = f"https://github.com/ByteByteGoHq/system-design-101/blob/{COMMIT}/data/guides/two.md"
        self.source_map.write_text(json.dumps({**PIN, "categories": [{"id": "sd-01", "lessons": [
            source_entry(), source_entry("sd-01-002", "Bài hai", other, source_path="data/guides/two.md")]}]}),
            encoding="utf-8")
        self.put(source_ref="sd-01-002")
        self.assertProblem("source_ref 'sd-01-002' is neither the lesson itself nor an entry it shares a source with")

    def test_the_snapshot_says_what_the_source_map_says(self) -> None:
        cases = {
            "another repository": ("repository", "someone/else"),
            "another commit": ("commit_sha", "0" * 40),
            "another path": ("path", "data/guides/other.md"),
            "another blob": ("blob_sha", "b" * 40),
            "another URL": ("snapshot_url", SNAPSHOT.replace("one", "two")),
            "a null path": ("path", None),
        }
        for name, (key, value) in cases.items():
            with self.subTest(case=name):
                snapshot = {**self.meta()["source_snapshot"], key: value}
                self.put(source_snapshot=snapshot)
                self.assertProblem(f"source_snapshot {key} is {value!r}, but the source map has")
        self.put(source_snapshot={**self.meta()["source_snapshot"], "snapshot_url": SNAPSHOT})
        self.assertEqual([], self.problems())

    def test_the_snapshot_has_its_keys_and_well_formed_extras(self) -> None:
        base = self.meta()["source_snapshot"]
        for key in sorted(check.SNAPSHOT_REQUIRED):
            with self.subTest(missing=key):
                self.put(source_snapshot={k: v for k, v in base.items() if k != key})
                self.assertProblem(f"source_snapshot is missing {key}")
        self.put(source_snapshot={**base, "extra": 1})
        self.assertProblem("source_snapshot has unknown keys extra")
        for value in (None, [], "x", 5):
            with self.subTest(snapshot=value):
                self.put(source_snapshot=value)
                self.assertProblem("source_snapshot must be an object")
        good = {"snapshot_url": SNAPSHOT, "blob_identity_status": "verified_against_retrieved_body", "note": "ok",
                "retrieved_body_sha256": "c" * 64, "retrieved_body_bytes": 1531}
        self.put(source_snapshot={**base, **good})
        self.assertEqual([], self.problems())
        for key, value, fragment in [("retrieved_body_sha256", "c" * 63, "retrieved_body_sha256 must be 64 hex"),
                                     ("retrieved_body_sha256", "z" * 64, "retrieved_body_sha256 must be 64 hex"),
                                     ("retrieved_body_sha256", 5, "retrieved_body_sha256 must be 64 hex"),
                                     ("retrieved_body_bytes", 0, "retrieved_body_bytes must be a positive integer"),
                                     ("retrieved_body_bytes", True, "retrieved_body_bytes must be a positive integer"),
                                     ("retrieved_body_bytes", "12", "retrieved_body_bytes must be a positive integer"),
                                     ("note", "", "note must be a non-empty string"),
                                     ("blob_identity_status", None, "blob_identity_status must be a non-empty string")]:
            with self.subTest(key=key, value=value):
                self.put(source_snapshot={**base, **good, key: value})
                self.assertProblem(fragment)

    def test_prerequisites_and_related_name_other_source_map_ids(self) -> None:
        related = {"lesson_id": "sd-01-011", "relation": "compare-with", "reason_vi": "Cùng chủ đề."}
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT), "sd-01-011": ("Khác", SNAPSHOT)})
        self.put(prerequisites=["sd-01-011"], related=[related])
        self.assertEqual([], self.problems_of_metadata())
        cases = {
            "an unknown prerequisite": ({"prerequisites": ["sd-99-999"]}, "'sd-99-999' in prerequisites or related"),
            "itself as a prerequisite": ({"prerequisites": ["sd-01-001"]}, "'sd-01-001' in prerequisites or related"),
            "a number as a prerequisite": ({"prerequisites": [5]}, "5 in prerequisites or related"),
            "a prerequisites that is not a list": ({"prerequisites": "sd-01-011"}, "prerequisites must be a list"),
            "an unknown related lesson": ({"related": [{**related, "lesson_id": "sd-99-999"}]}, "'sd-99-999' in prerequisites or related"),
            "itself as related": ({"related": [{**related, "lesson_id": "sd-01-001"}]}, "'sd-01-001' in prerequisites or related"),
            "a related that is not a list": ({"related": {}}, "related must be a list"),
            "a related entry that is a string": ({"related": ["sd-01-011"]}, "each related entry needs exactly"),
            "a related entry without a reason": ({"related": [{"lesson_id": "sd-01-011", "relation": "x"}]}, "each related entry needs exactly"),
            "a related entry with a blank relation": ({"related": [{**related, "relation": " "}]}, "each related entry needs exactly"),
            "a related entry with a blank reason": ({"related": [{**related, "reason_vi": " "}]}, "each related entry needs exactly"),
            "a related entry with an extra key": ({"related": [{**related, "x": 1}]}, "each related entry needs exactly"),
        }
        for name, (changes, fragment) in cases.items():
            with self.subTest(case=name):
                self.put(**changes)
                self.assertProblem(fragment)

    def test_the_optional_notes_and_records_are_checked_when_present(self) -> None:
        migration = {"source_repository": "owner/old", "source_commit_sha": "c" * 40, "destination_repository": "owner/new",
                     "imported_on": "2026-10-13"}
        for changes in ({"design_notes_vi": "Ghi chú."}, {"editorial_note_vi": "Ghi chú."},
                        {"source_only_trivia": [{"topic": "x"}]}, {"source_deviations": ["Bỏ một so sánh."]},
                        {"prior_reviews": [{"sha": "x"}, {"status": "checked"}]}, {"migration": migration}):
            with self.subTest(accepted=list(changes)):
                self.put(**changes)
                self.assertEqual([], self.problems())
        cases = {
            "a blank design note": ({"design_notes_vi": " "}, "design_notes_vi must be a non-empty string"),
            "a design note that is a list": ({"design_notes_vi": ["x"]}, "design_notes_vi must be a non-empty string"),
            "a blank editorial note": ({"editorial_note_vi": ""}, "editorial_note_vi must be a non-empty string"),
            "trivia that is a string": ({"source_only_trivia": "x"}, "source_only_trivia must be a list of objects"),
            "trivia with a string in it": ({"source_only_trivia": ["x"]}, "source_only_trivia must be a list of objects"),
            "prior reviews that is an object": ({"prior_reviews": {}}, "prior_reviews must be a list of objects"),
            "a prior review that is a string": ({"prior_reviews": ["x"]}, "prior_reviews must be a list of objects"),
            "deviations that is a string": ({"source_deviations": "x"}, "source_deviations must be a list of non-empty strings"),
            "a blank deviation": ({"source_deviations": ["ok", " "]}, "source_deviations must be a list of non-empty strings"),
            "a deviation that is an object": ({"source_deviations": [{}]}, "source_deviations must be a list of non-empty strings"),
            "a migration with a key missing": ({"migration": {k: v for k, v in migration.items() if k != "imported_on"}},
                                               "migration must have exactly"),
            "a migration with an extra key": ({"migration": {**migration, "x": 1}}, "migration must have exactly"),
            "a migration that is a string": ({"migration": "x"}, "migration must have exactly"),
            "a migration that is null": ({"migration": None}, "migration must have exactly"),
            "a migration that is a number": ({"migration": 5}, "migration must have exactly"),
            "a numeric migration commit": ({"migration": {**migration, "source_commit_sha": 5}},
                                           "migration source_commit_sha must be a 40-hex commit"),
            "a null migration commit": ({"migration": {**migration, "source_commit_sha": None}},
                                        "migration source_commit_sha must be a 40-hex commit"),
            "a numeric migration repository": ({"migration": {**migration, "source_repository": 5}},
                                                 "migration source_repository must be owner/name"),
            "a migration repository without an owner": ({"migration": {**migration, "source_repository": "old"}},
                                                         "migration source_repository must be owner/name"),
            "a migration destination that is null": ({"migration": {**migration, "destination_repository": None}},
                                                      "migration destination_repository must be owner/name"),
            "a short migration commit": ({"migration": {**migration, "source_commit_sha": "abc"}},
                                         "migration source_commit_sha must be a 40-hex commit"),
            "an impossible migration date": ({"migration": {**migration, "imported_on": "2026-02-30"}},
                                              "migration imported_on must be a YYYY-MM-DD date"),
        }
        for name, (changes, fragment) in cases.items():
            with self.subTest(case=name):
                self.put(**changes)
                self.assertProblem(fragment)

    def test_image_evidence_with_real_values_is_accepted(self) -> None:
        self.put(image_evidence=[GOOD_EVIDENCE])
        self.assertEqual([], self.problems())
        self.put(image_evidence=[])
        self.assertEqual([], self.problems())

    def test_image_evidence_values_must_be_real(self) -> None:
        good = GOOD_EVIDENCE
        bad = {"null url": {**good, "url": None}, "not an http url": {**good, "url": "ftp://x/y.png"},
               "empty digest": {**good, "sha256": ""}, "short digest": {**good, "sha256": "a" * 63},
               "non-hex digest": {**good, "sha256": "z" * 64}, "null date": {**good, "retrieved_on": None},
               "not a date": {**good, "retrieved_on": "yesterday"}, "url without a host": {**good, "url": "https://"},
               "month 99": {**good, "retrieved_on": "2026-99-99"}, "february 30": {**good, "retrieved_on": "2026-02-30"},
               "no digest": {"url": "https://x/y.png"}, "an extra key": {**good, "note": "x"}, "a string": "x",
               "a numeric digest": {**good, "sha256": 5}, "a null digest": {**good, "sha256": None},
               "a numeric url": {**good, "url": 5}, "a numeric date": {**good, "retrieved_on": 5}}
        for name, entry in bad.items():
            with self.subTest(entry=name):
                self.put(image_evidence=[entry])
                self.assertProblem("image_evidence must be a list of entries")
        self.put(image_evidence={})
        self.assertProblem("image_evidence must be a list of entries")

    def evidence_problems(self, url: str) -> list[str]:
        self.put(image_evidence=[{"url": url, "sha256": "a" * 64, "retrieved_on": "2026-10-12"}])
        return [line for line in self.problems() if "image_evidence" in line]

    def test_an_evidence_url_needs_a_real_host_and_a_readable_port(self) -> None:
        for url in ["https://@/image.png", "https://user@/image.png", "https://:443/image.png", "https://./a.png",
                    "https://-a.com/x", "https://a-.com/x", "https://a..b/x", "https://a_b.com/x", "https://host:abc/x",
                    "https://host:99999/x", "https://tên.vn/x", "http://", "https:///x", "ftp://example.com/x",
                    "https://" + "a" * 64 + ".com/x", "https://1.2.3/x extra", "https://example.com/a b.png",
                    "https://example.com/a\tb", "https://example.com/a\x01b", "https://example.com/​b"]:
            with self.subTest(url=url):
                self.assertTrue(self.evidence_problems(url), f"{url!r} was accepted")

    def test_ordinary_evidence_urls_are_accepted(self) -> None:
        for url in ["https://user@example.com/a.png", "https://example.com:8443/a", "http://127.0.0.1/a",
                    "https://[::1]/a", "https://example.com./a", "https://sub-1.example.co.uk/a?b=c#d",
                    "https://localhost/a", "https://EXAMPLE.com/a", "https://xn--tn-qla.vn/a"]:
            with self.subTest(url=url):
                self.assertEqual([], self.evidence_problems(url))

    def test_a_timestamp_is_not_a_retrieval_date(self) -> None:
        good = {"url": "https://example.com/a.png", "sha256": "a" * 64}
        for name, when in {"a quoted timestamp": "2026-10-12 12:34:56", "an ISO timestamp": "2026-10-12T12:34:56Z",
                           "a number": 20261012, "a list": ["2026-10-12"], "a compact date": "20261012",
                           "a week date": "2026-W41-1", "a date with spaces": " 2026-10-12"}.items():
            with self.subTest(value=name):
                self.put(image_evidence=[{**good, "retrieved_on": when}])
                self.assertTrue([line for line in self.problems() if "image_evidence" in line])
        self.put(image_evidence=[{**good, "retrieved_on": "2026-10-12"}])
        self.assertEqual([], self.problems())



FIGURE_PATH = "../../diagrams/sd-01-001-main.svg"


class LessonMarkdownRuleTests(StoreCase):
    def test_an_unclosed_code_fence_is_reported(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n```mermaid\nflowchart TB\n")
        self.assertProblem("unclosed code fence")

    def test_details_with_attributes_is_a_balanced_details_block(self) -> None:
        block = "<details open>\n<summary>x</summary>\n\nnội dung\n\n</details>"
        self.write_lesson("sd-01-001", body=BODY + "\n" + block + "\n")
        self.assertEqual([], self.problems())

    def test_a_details_tag_in_a_code_block_a_code_span_or_a_comment_is_not_counted(self) -> None:
        for name, text in {"code block": "```html\n<details>\n```", "code span": "Gõ `<details>` để mở.",
                           "comment": "<!-- <details> -->"}.items():
            with self.subTest(where=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + text + "\n")
                self.assertEqual([], self.problems())

    def test_a_self_closing_details_tag_opens_a_block_as_it_does_in_html(self) -> None:
        for name, tag in {"slash": "<details/>", "space and slash": "<details />", "attribute": "<details open/>"}.items():
            with self.subTest(tag=name):
                self.write_lesson("sd-01-001", body=BODY + f"\n{tag}\n<summary>x</summary>\n\nchữ\n")
                self.assertProblem("unbalanced <details> tags")
        self.write_lesson("sd-01-001", body=BODY + "\n<details/>\n<summary>x</summary>\n\nchữ\n\n</details>\n")
        self.assertEqual([], self.problems())

    def test_self_closing_void_tags_are_fine(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\ndòng<br/>sau<br />nữa\n")
        self.assertEqual([], self.problems())

    def test_a_stray_closing_details_tag_is_reported_even_when_a_later_block_balances_the_count(self) -> None:
        block = "<details>\n<summary>x</summary>\n\nnội dung\n\n</details>"
        forms = {"close then an open block left open": "</details>\n\n<details>\n<summary>x</summary>\n\nnội dung\n",
                 "close then a balanced block": "</details>\n\n" + block,
                 "close only": "</details>"}
        for name, text in forms.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + text + "\n")
                self.assertProblem("unbalanced <details>")

    def test_nested_details_blocks_are_balanced(self) -> None:
        inner = "<details>\n<summary>trong</summary>\n\nb\n\n</details>"
        outer = f"<details>\n<summary>ngoài</summary>\n\n{inner}\n\n</details>"
        self.write_lesson("sd-01-001", body=BODY + "\n" + outer + "\n")
        self.assertEqual([], self.problems())

    def test_a_closed_fence_inside_a_blockquote_or_a_list_is_closed(self) -> None:
        forms = {"blockquote": "> ```\n> flowchart TB\n> ```", "nested blockquote": "> > ~~~\n> > a\n> > ~~~",
                 "blockquote without a space": ">```\n>a\n>```", "list item": "- mục\n\n  ```\n  a\n  ```",
                 "blockquote in a list": "- mục\n\n  > ```\n  > a\n  > ```"}
        for name, block in forms.items():
            with self.subTest(block=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + block + "\n")
                self.assertEqual([], self.problems())

    def test_an_unclosed_fence_inside_a_blockquote_is_reported(self) -> None:
        for name, block in {"unclosed": "> ```\n> flowchart TB", "closed by a shorter fence": "> ````\n> a\n> ```"}.items():
            with self.subTest(block=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + block + "\n")
                self.assertProblem("unclosed code fence")

    def test_a_lone_opening_fence_at_the_end_of_the_file_is_reported(self) -> None:
        for name, ending in {"backticks": "```", "tildes": "~~~", "long backticks": "````",
                             "backticks and a newline": "```\n", "an info string": "```mermaid"}.items():
            with self.subTest(ending=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + ending)
                self.assertProblem("unclosed code fence")

    def test_an_empty_fenced_block_is_not_unclosed(self) -> None:
        for name, block in {"backticks": "```\n```", "tildes": "~~~\n~~~", "an info string": "```text\n```\n"}.items():
            with self.subTest(block=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + block + "\n")
                self.assertEqual([], self.problems())

    def test_closed_fences_of_either_marker_and_any_length_are_accepted(self) -> None:
        for name, fence in {"backticks": "```mermaid\nx\n```", "tildes": "~~~\nx\n~~~",
                            "long backticks": "````\nx\n````",
                            "a long fence may contain a short one": "````\n```\nx\n```\n````"}.items():
            with self.subTest(fence=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + fence + "\n")
                self.assertEqual([], self.problems())

    def test_a_closing_fence_of_the_other_marker_does_not_close_it(self) -> None:
        for name, body in {"backticks closed by tildes": "```\ncode\n~~~\n", "tildes closed by backticks": "~~~\ncode\n```\n"}.items():
            with self.subTest(fence=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + body)
                self.assertProblem("unclosed code fence")

    def test_a_closing_fence_shorter_than_the_opening_one_does_not_close_it(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n````\ncode\n```\n")
        self.assertProblem("unclosed code fence")

    def test_unbalanced_details_tags_are_reported(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n<details>\n<summary>x</summary>\n")
        self.assertProblem("unbalanced <details>")

    # --- figures: images are the lesson's .svg files in diagrams/, with alt text -----------------------------------

    def test_a_missing_local_image_is_reported_in_every_form(self) -> None:
        forms = {"inline": "![sơ đồ](missing.svg)", "reference": "![sơ đồ][i]\n\n[i]: missing.svg",
                 "html img": '<img src="missing.svg" alt="sơ đồ">'}
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + form + "\n")
                self.assertProblem("'missing.svg' does not resolve")

    def test_the_lessons_figure_is_accepted_in_every_form(self) -> None:
        forms = {"inline": f"![sơ đồ]({FIGURE_PATH})", "reference": f"![sơ đồ][i]\n\n[i]: {FIGURE_PATH}",
                 "html img": f'<img src="{FIGURE_PATH}" alt="sơ đồ">',
                 "html srcset": f'<img srcset="{FIGURE_PATH} 1x, {FIGURE_PATH} 2x" alt="sơ đồ">',
                 "html srcset only": f'<img srcset="{FIGURE_PATH}" alt="sơ đồ">'}
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + form + "\n")
                self.assertEqual([], self.problems())

    def test_a_detour_to_the_figure_is_the_same_figure(self) -> None:
        for name, path in {"a detour": "../../diagrams/../diagrams/sd-01-001-main.svg",
                           "encoded slashes": "..%2F..%2Fdiagrams%2Fsd-01-001-main.svg",
                           "dot slash": "./../../diagrams/sd-01-001-main.svg"}.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + f"\n![sơ đồ]({path})\n")
                self.assertEqual([], self.problems())

    def test_an_image_that_is_not_an_svg_in_diagrams_is_reported(self) -> None:
        forms = {"local png": "![x](diagram.png)", "local jpeg in html": '<img src="diagram.jpg" alt="x">',
                 "remote svg": "![x](https://example.com/a.svg)", "remote png": "![x](https://example.com/a.png)",
                 "a png in diagrams": "![x](../../diagrams/sd-01-001-main.png)"}
        for name, form in forms.items():
            with self.subTest(form=name):
                lesson_dir = self.write_lesson("sd-01-001", body=BODY + "\n" + form + "\n")
                (lesson_dir / "diagram.png").write_bytes(b"\x89PNG")
                (lesson_dir / "diagram.jpg").write_bytes(b"\xff\xd8")
                (self.store / "diagrams" / "sd-01-001-main.png").write_bytes(b"\x89PNG")
                self.assertProblem("must be an .svg figure directly inside diagrams/")

    def test_an_svg_outside_diagrams_is_not_a_figure_of_the_lesson(self) -> None:
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT), "sd-01-002": ("Bài hai", SNAPSHOT)})
        other = self.write_lesson("sd-01-002")
        (other / "figure.svg").write_text(FIGURE, encoding="utf-8")
        (self.store / "root.svg").write_text(FIGURE, encoding="utf-8")
        (self.store / "diagrams" / "sub").mkdir()
        (self.store / "diagrams" / "sub" / "x-main.svg").write_text(FIGURE, encoding="utf-8")
        forms = {"another lesson's directory": "../sd-01-002/figure.svg", "the store root": "../../root.svg",
                 "a subdirectory of diagrams": "../../diagrams/sub/x-main.svg",
                 "an absolute path": "/diagrams/sd-01-001-main.svg"}
        for name, destination in forms.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + f"\n![x]({destination})\n")
                self.assertProblem("must be an .svg figure directly inside diagrams/")

    def test_another_lessons_figure_may_be_shown_next_to_its_own(self) -> None:
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT), "sd-01-002": ("Bài hai", SNAPSHOT)})
        self.write_lesson("sd-01-002")
        self.write_readme(README + "| [sd-01-002](lessons/sd-01-002/lesson.md) | Bài hai |\n")
        self.write_lesson("sd-01-001", body=BODY + "\n![x](../../diagrams/sd-01-002-main.svg)\n")
        self.assertEqual([], self.problems())

    def test_a_lesson_must_show_its_own_figure(self) -> None:
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT), "sd-01-002": ("Bài hai", SNAPSHOT)})
        self.write_lesson("sd-01-002")
        self.write_readme(README + "| [sd-01-002](lessons/sd-01-002/lesson.md) | Bài hai |\n")
        for name, body in {"no image": f"# Bài một\n\n[nguồn]({SNAPSHOT})\n",
                           "only another lesson's figure": f"# Bài một\n\n![x](../../diagrams/sd-01-002-main.svg)\n[nguồn]({SNAPSHOT})\n",
                           "a link to the figure, not an image": f"# Bài một\n\n[hình]({FIGURE_PATH})\n[nguồn]({SNAPSHOT})\n"}.items():
            with self.subTest(body=name):
                self.write_lesson("sd-01-001", body=body)
                self.assertProblem("lesson.md does not show its figure diagrams/sd-01-001-main.svg")
        self.write_lesson("sd-01-001", body=f"# Bài một\n\n![x]({FIGURE_PATH})\n[nguồn]({SNAPSHOT})\n")
        self.assertEqual([], self.problems())

    def test_an_image_without_alt_text_is_reported(self) -> None:
        forms = {"empty inline": f"![]({FIGURE_PATH})", "blank inline": f"![ ]({FIGURE_PATH})",
                 "empty reference": f"![][i]\n\n[i]: {FIGURE_PATH}", "html without alt": f'<img src="{FIGURE_PATH}">',
                 "html with empty alt": f'<img src="{FIGURE_PATH}" alt="">', "html with blank alt": f"<img src='{FIGURE_PATH}' alt=' '>"}
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + form + "\n")
                self.assertProblem("lesson.md has an image without alt text")

    def test_an_image_with_alt_text_is_not_reported(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + f'\n![ngắn]({FIGURE_PATH}) <img src="{FIGURE_PATH}" alt="ngắn">\n')
        self.assertFalse(any("alt text" in line for line in self.problems()), self.problems())

    def test_a_src_attribute_on_a_tag_other_than_img_is_not_an_image(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + '\nH<sub src="missing.png">2</sub>O\n')
        self.assertEqual([], self.problems())

    def test_an_html_image_without_a_source_is_reported(self) -> None:
        forms = {"no attributes": "<img>", "only alt": '<img alt="sơ đồ">', "empty src": '<img src="" alt="x">',
                 "empty single-quoted src": "<img src=''>", "empty srcset": '<img srcset="" alt="x">',
                 "only a width": '<img width="100">'}
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + form + "\n")
                self.assertProblem("must be an .svg figure directly inside diagrams/")

    def test_a_missing_or_non_svg_image_in_an_img_srcset_is_reported(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + f'\n<img srcset="{FIGURE_PATH} 1x, ../../diagrams/two-main.svg 2x" alt="x">\n')
        self.assertProblem("'../../diagrams/two-main.svg' does not resolve")
        (self.store / "diagrams" / "two-main.png").write_bytes(b"x")
        self.write_lesson("sd-01-001", body=BODY + f'\n<img srcset="{FIGURE_PATH} 1x, ../../diagrams/two-main.png 2x" alt="x">\n')
        self.assertProblem("'../../diagrams/two-main.png' must be an .svg figure")

    def test_srcset_urls_are_split_like_the_html_spec_splits_them(self) -> None:
        cases = {
            "a.svg": ["a.svg"],
            "a.svg 1x, b.svg 2x": ["a.svg", "b.svg"],
            "a.svg, b.svg": ["a.svg", "b.svg"],
            "a.svg 1x,b.svg 2x": ["a.svg", "b.svg"],
            "a.svg,b.svg": ["a.svg,b.svg"],
            "  a.svg 100w ,  b.svg 200w  ": ["a.svg", "b.svg"],
            "a,b.svg 1x": ["a,b.svg"],
            "": [],
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(expected, check.srcset_urls(value))

    # --- what a lesson directory, diagrams/, metadata/ and lessons/ may hold ------------------------------------

    def test_a_lesson_directory_may_hold_only_lesson_md_and_lesson_yaml(self) -> None:
        lesson_dir = self.write_lesson("sd-01-001")
        for name in ("diagram.png", "photo.JPG", "notes.txt", "diagram.svg", "FIGURE.SVG", "metadata.json"):
            with self.subTest(file=name):
                (lesson_dir / name).write_bytes(b"x")
                self.assertProblem(f"{name} is not allowed")
                (lesson_dir / name).unlink()
        (lesson_dir / "assets").mkdir()
        self.assertProblem("assets is not allowed")

    def test_diagrams_holds_only_the_figures_of_lesson_directories(self) -> None:
        diagrams = self.store / "diagrams"
        self.assertEqual([], self.problems())
        for name in ("sd-01-009-main.svg", "sd-01-001.svg", "sd-01-001-main.svg.png", "sd-01-001-main.png",
                     "notes.txt", "SD-01-001-MAIN.SVG", "-main.svg"):
            with self.subTest(file=name):
                (diagrams / name).write_text(FIGURE, encoding="utf-8")
                self.assertProblem(f"diagrams: {name} is not the <id>-main.svg figure of a lesson directory")
                (diagrams / name).unlink()
        (diagrams / "folder-main.svg").mkdir()
        self.assertProblem("diagrams: folder-main.svg is not the <id>-main.svg figure")
        (diagrams / "folder-main.svg").rmdir()
        (diagrams / "sd-01-001-main.svg").unlink()
        (diagrams / "sd-01-001-main.svg").mkdir()
        self.assertProblem("diagrams: sd-01-001-main.svg is not the <id>-main.svg figure")

    def test_metadata_holds_only_the_json_of_lesson_directories(self) -> None:
        metadata_dir = self.store / "metadata"
        for name in ("sd-01-009.json", "sd-01-001.txt", "notes.json", "sd-01-001.json.bak"):
            with self.subTest(file=name):
                (metadata_dir / name).write_text("{}", encoding="utf-8")
                self.assertProblem(f"metadata: {name} is not the metadata of a lesson directory")
                (metadata_dir / name).unlink()
        (metadata_dir / "sd-01-001.json.d").mkdir()
        self.assertProblem("metadata: sd-01-001.json.d is not the metadata")
        (metadata_dir / "sd-01-001.json.d").rmdir()
        (metadata_dir / "sd-01-001.json").unlink()
        (metadata_dir / "sd-01-001.json").mkdir()
        self.assertProblem("metadata: sd-01-001.json is not the metadata of a lesson directory")

    def test_lessons_holds_lesson_directories_and_pointers_to_them(self) -> None:
        pointer = self.store / "lessons" / "sd-01-001.md"
        pointer.write_text("Bài này ở [trang bài chính](sd-01-001/lesson.md).\n", encoding="utf-8")
        self.assertEqual([], self.problems())
        pointer.write_text("Bài này ở [trang bài chính](<./sd-01-001/lesson.md#a>).\n", encoding="utf-8")
        self.assertEqual([], self.problems())
        pointer.write_text("Không có liên kết.\n", encoding="utf-8")
        self.assertProblem("lessons: sd-01-001.md is a pointer that does not link sd-01-001/lesson.md")
        pointer.write_text("[bài khác](sd-01-002/lesson.md)\n", encoding="utf-8")
        self.assertProblem("lessons: sd-01-001.md is a pointer that does not link sd-01-001/lesson.md")
        pointer.write_bytes(b"[x](sd-01-001/lesson.md)\n\xff\xfe")
        self.assertEqual([], self.problems())
        pointer.unlink()
        for name in ("sd-01-009.md", "notes.md", "sd-01-001.txt", "copied-source.png"):
            with self.subTest(file=name):
                (self.store / "lessons" / name).write_bytes(b"x")
                self.assertProblem(f"lessons: {name} is not a lesson directory, or a .md pointer to one")
                (self.store / "lessons" / name).unlink()

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symbolic links")
    def test_a_symbolic_link_is_not_a_lesson_file(self) -> None:
        lesson_dir = self.write_lesson("sd-01-001")
        lesson_md = lesson_dir / "lesson.md"
        real = self.root / "real.md"
        real.write_text(BODY, encoding="utf-8")
        lesson_md.unlink()
        lesson_md.symlink_to(real)
        self.assertProblem("lesson.md is a symbolic link")

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symbolic links")
    def test_a_symbolic_link_for_a_figure_or_a_metadata_file_is_reported(self) -> None:
        figure = self.store / "diagrams" / "sd-01-001-main.svg"
        elsewhere = self.root / "shared.svg"
        elsewhere.write_text(FIGURE, encoding="utf-8")
        figure.unlink()
        figure.symlink_to(elsewhere)
        found = self.problems()
        self.assertTrue(any("diagrams: sd-01-001-main.svg is not the <id>-main.svg figure" in line for line in found), found)
        self.assertTrue(any("directly inside diagrams/" in line for line in found), found)
        figure.unlink()
        self.write_figure("sd-01-001")
        metadata_file = self.store / "metadata" / "sd-01-001.json"
        real = self.root / "real.json"
        real.write_text(metadata_file.read_text(encoding="utf-8"), encoding="utf-8")
        metadata_file.unlink()
        metadata_file.symlink_to(real)
        self.assertProblem("metadata: sd-01-001.json is not the metadata of a lesson directory")

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symbolic links")
    def test_a_symbolic_link_for_a_lesson_directory_the_readme_or_a_store_directory_is_reported(self) -> None:
        copy = self.root / "elsewhere"
        copy.mkdir()
        (copy / "lesson.md").write_text(BODY, encoding="utf-8")
        (copy / "lesson.yaml").write_text("id: sd-01-002\n", encoding="utf-8")
        (self.store / "lessons" / "sd-01-002").symlink_to(copy, target_is_directory=True)
        found = self.problems()
        self.assertTrue(any("lessons: sd-01-002 is not a lesson directory" in line for line in found), found)
        self.assertFalse(any(line.startswith("sd-01-002:") for line in found), "the linked directory is not checked as a lesson")
        (self.store / "lessons" / "sd-01-002").unlink()
        readme = self.store / "README.md"
        real = self.root / "README.real"
        real.write_text(README, encoding="utf-8")
        readme.unlink()
        readme.symlink_to(real)
        self.assertProblem("README.md: is a symbolic link")
        readme.unlink()
        self.write_readme(README)
        for name in ("lessons", "metadata", "diagrams"):
            with self.subTest(directory=name):
                moved = self.root / f"{name}-real"
                (self.store / name).rename(moved)
                (self.store / name).symlink_to(moved, target_is_directory=True)
                self.assertProblem(f"{name}: is a symbolic link")
                (self.store / name).unlink()
                moved.rename(self.store / name)

    # --- diagrams: each figure is a drawing, not a renamed picture ----------------------------------------------------

    def figure_problems(self, content: str | bytes) -> list[str]:
        self.write_figure("sd-01-001", content)
        return [line for line in self.problems() if "sd-01-001-main.svg" in line]

    def test_an_svg_file_must_be_a_drawing_not_a_renamed_picture(self) -> None:
        png = "data:image/png;base64,iVBORw0KGgo="
        svgs = {
            "a renamed png": (b"\x89PNG\r\n\x1a\n\x00\x00", "is not well-formed XML"),
            "an empty file": (b"", "is not well-formed XML"),
            "xml with another root": (b"<html/>", "does not have an <svg> root"),
            "an embedded raster": (f'<svg><image href="{png}"/></svg>'.encode(), "embeds a picture with <image>"),
            "a linked raster": (b'<svg><image href="source.png"/></svg>', "embeds a picture with <image>"),
            "a namespaced image": (b'<svg xmlns="http://www.w3.org/2000/svg"><image/></svg>',
                                   "embeds a picture with <image>"),
            "a bare html img": (b'<svg><img xmlns="http://www.w3.org/1999/xhtml" src="a.png"/></svg>',
                                "embeds a picture with <img>"),
            "an html img inside foreignObject": (
                b'<svg xmlns="http://www.w3.org/2000/svg"><foreignObject>'
                b'<img xmlns="http://www.w3.org/1999/xhtml" src="a.png"/></foreignObject></svg>',
                "uses <foreignobject>"),
            "an html object holding a data uri inside foreignObject": (
                f'<svg xmlns="http://www.w3.org/2000/svg"><foreignObject><object xmlns="http://www.w3.org/1999/xhtml" '
                f'data="{png}"/></foreignObject></svg>'.encode(), "uses <foreignobject>"),
            "a bare object holding a data uri": (f'<svg><object data="{png}"/></svg>'.encode(), "uses <object>"),
            "an embed": (b'<svg><embed src="a.png"/></svg>', "uses <embed>"),
            "an iframe": (b'<svg><iframe src="a.html"/></svg>', "uses <iframe>"),
            "a script": (b"<svg><script>alert(1)</script></svg>", "uses <script>"),
            "an animation that sets an href": (b'<svg><use href="#a"><set attributeName="href" to="x.svg"/></use></svg>',
                                              "uses <set>"),
            "an animate": (b'<svg><rect><animate attributeName="x" to="9"/></rect></svg>', "uses <animate>"),
            "a link element": (b'<svg><a href="#a"><rect/></a></svg>', "uses <a>"),
            "an inkscape element": (b'<svg xmlns:s="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"><s:namedview/></svg>',
                                    "uses <namedview>"),
            "a svg-named element in another namespace": (b'<svg><rect xmlns="http://www.w3.org/1999/xhtml"/></svg>',
                                                         "uses <rect>"),
            "a feImage that loads the source host": (
                b'<svg xmlns="http://www.w3.org/2000/svg"><filter><feImage href="https://assets.bytebytego.com/'
                b'source.png"/></filter></svg>', "assets.bytebytego.com"),
            "a feImage that loads another picture": (
                b'<svg xmlns="http://www.w3.org/2000/svg"><filter><feImage href="#a"/></filter></svg>',
                "embeds a picture with <feimage>"),
            "the source host in a label": (b"<svg><text>assets.bytebytego.com</text></svg>", "assets.bytebytego.com"),
            "the source host in capitals": (b"<svg><text>ASSETS.BYTEBYTEGO.COM</text></svg>", "assets.bytebytego.com"),
            "an upper-case @import": (b'<svg><style>@IMPORT "fonts.css";</style></svg>', "url() or @import"),
            "an href to another file": (b'<svg><use href="other.svg#a"/></svg>', "outside the drawing"),
            "an href to a web page": (b'<svg><use href="https://example.com/a.svg"/></svg>', "outside the drawing"),
            "a namespaced xlink:href": (
                b'<svg xmlns:xlink="http://www.w3.org/1999/xlink"><use xlink:href="https://example.com/a.svg"/></svg>',
                "outside the drawing"),
            "a data uri in an href": (f'<svg><use href="{png}"/></svg>'.encode(), "outside the drawing"),
            "a url() to a file in an attribute": (b'<svg><rect style="fill:url(https://example.com/a.png)"/></svg>',
                                                  "url() or @import"),
            "a data uri in a url() in an attribute": (f'<svg><rect style="fill:url({png})"/></svg>'.encode(),
                                                      "url() or @import"),
            "a quoted url() in an attribute": (b'<svg><rect style="fill:url( \'a.png\' )"/></svg>',
                                               "url() or @import"),
            "a url() in a style element": (f"<svg><style>.a{{background:url({png})}}</style></svg>".encode(),
                                           "url() or @import"),
            "an @import in a style element": (b'<svg><style>@import "fonts.css";</style></svg>', "url() or @import"),
        }
        for name, (content, reason) in svgs.items():
            with self.subTest(file=name):
                found = self.figure_problems(content)
                self.assertTrue(any(reason in line for line in found), found)

    def test_the_elements_of_an_ordinary_drawing_are_accepted(self) -> None:
        names = ["g", "defs", "symbol", "use", "title", "desc", "style", "path", "rect", "circle", "ellipse", "line",
                 "polyline", "polygon", "text", "tspan", "textPath", "marker", "pattern", "mask", "clipPath",
                 "linearGradient", "radialGradient", "stop", "filter", "feBlend", "feColorMatrix", "feComposite",
                 "feDropShadow", "feGaussianBlur", "feFlood", "feOffset", "feMerge", "feMergeNode"]
        for name in names:
            with self.subTest(element=name):
                self.assertEqual([], self.figure_problems(
                    f'<svg xmlns="http://www.w3.org/2000/svg"><title>Sơ đồ</title><svg><{name}/></svg></svg>'))

    def test_an_svg_needs_a_text_description(self) -> None:
        for name, svg in {"nothing": "<svg/>", "a rectangle only": "<svg><rect/></svg>",
                          "a text label only": "<svg><text>Nhãn</text></svg>",
                          "an empty title": "<svg><title></title><rect/></svg>",
                          "a blank title": "<svg><title>  </title><rect/></svg>",
                          "a description of children only": "<svg><desc><tspan>x</tspan></desc></svg>"}.items():
            with self.subTest(file=name):
                found = self.figure_problems(svg)
                self.assertTrue(any("has no text description" in line for line in found), found)
        for name, svg in {"a title": "<svg><title>Sơ đồ</title></svg>", "a desc": "<svg><desc>Mô tả</desc></svg>",
                          "a title in a group": "<svg><g><title>Nút</title></g></svg>",
                          "a namespaced title": '<svg xmlns="http://www.w3.org/2000/svg"><title>Sơ đồ</title></svg>'}.items():
            with self.subTest(file=name):
                self.assertEqual([], self.figure_problems(svg))

    def test_an_svg_with_a_processing_instruction_is_reported(self) -> None:
        for name, svg in {"a stylesheet in the prolog": '<?xml-stylesheet href="https://example.com/s.css"?><svg/>',
                          "a stylesheet after the declaration":
                              '<?xml version="1.0"?>\n<?xml-stylesheet href="s.css" type="text/css"?>\n<svg/>',
                          "an instruction inside the drawing": "<svg><g><?php echo 1 ?></g></svg>",
                          "an instruction after the drawing": "<svg/><?xpacket end='w'?>"}.items():
            with self.subTest(file=name):
                found = self.figure_problems(svg)
                self.assertTrue(any("has a processing instruction" in line for line in found), found)

    def test_css_animation_and_transition_in_an_svg_are_reported(self) -> None:
        cases = {
            "keyframes in a style element": "<svg><style>@keyframes x{from{opacity:0}to{opacity:1}} rect{animation:x 1s}</style></svg>",
            "an entity-escaped keyframes": "<svg><style>@keyframes x&#123;from&#123;opacity:0&#125;&#125;</style></svg>",
            "an animation in a style attribute": '<svg><rect style="animation: spin 1s infinite"/></svg>',
            "an animation-name property": '<svg><rect style="animation-name:spin"/></svg>',
            "a prefixed animation": '<svg><rect style="-webkit-animation: spin 1s"/></svg>',
            "a transition": '<svg><rect style="transition: all 1s"/></svg>',
            "an upper-case property": '<svg><rect style="ANIMATION : spin 1s"/></svg>',
        }
        for name, svg in cases.items():
            with self.subTest(file=name):
                found = self.figure_problems(svg)
                self.assertTrue(any("uses a CSS animation or transition" in line for line in found), found)

    def test_words_that_only_look_like_animation_are_fine(self) -> None:
        self.assertEqual([], self.figure_problems(
            '<svg><style>.animal{fill:red} .a{transform:rotate(3deg)}</style><title>animation: demo</title>'
            '<text>animation: transition: @keyframes</text><rect class="animation"/></svg>'))

    def test_an_svg_with_a_doctype_is_reported(self) -> None:
        cases = {
            "an external DTD": '<!DOCTYPE svg SYSTEM "https://example.com/svg.dtd"><svg/>',
            "the W3C SVG 1.1 DTD": '<?xml version="1.0"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
                                   '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg/>',
            "an internal subset with an entity": '<!DOCTYPE svg [<!ENTITY a "x">]><svg>&a;</svg>',
            "a bare DOCTYPE": "<!DOCTYPE svg><svg/>",
            "a DOCTYPE after a comment": "<!-- c --><!DOCTYPE svg><svg/>",
        }
        for name, svg in cases.items():
            with self.subTest(file=name):
                found = self.figure_problems(svg)
                self.assertTrue(any("has a DOCTYPE declaration" in line for line in found), found)

    def test_the_xml_declaration_is_not_a_processing_instruction(self) -> None:
        self.assertEqual([], self.figure_problems(
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?><svg><title>Sơ đồ</title></svg>'))

    def test_a_real_looking_svg_drawing_is_accepted(self) -> None:
        drawing = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                   'viewBox="0 0 10 10" aria-label="Data: sơ đồ"><title>Data: sơ đồ</title>'
                   '<defs><style>.a::after{content:"data: chữ"}</style>'
                   '<marker id="m"/><linearGradient id="g"/></defs>'
                   '<rect fill="url(\'#g\')" style="marker-end:url( #m )"/><use href="#a"/><use xlink:href="#a"/>'
                   '<text>Data: chữ</text></svg>')
        self.assertEqual([], self.figure_problems(drawing))

    # --- relative links, the pinned source, mentions of other lessons ----------------------------------------------

    def test_a_relative_link_that_does_not_resolve_is_reported(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n[thiếu](nowhere.md)\n")
        self.assertProblem("does not resolve")

    def test_a_root_relative_link_is_not_looked_up_on_the_machine_running_the_check(self) -> None:
        on_this_machine = self.root / "exists.md"
        on_this_machine.write_text("x", encoding="utf-8")
        for name, destination in {"a file on this machine": str(on_this_machine), "a directory": str(self.root),
                                  "the filesystem root": "/", "a missing one": "/no/such/file",
                                  "a file inside the store, by its absolute path": str(self.store / "README.md")}.items():
            with self.subTest(destination=name):
                self.write_lesson("sd-01-001", body=BODY + f"\n[x]({destination})\n")
                self.assertProblem(f"relative link '{destination}' does not resolve")

    def test_a_relative_link_that_resolves_is_accepted(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n[meta](lesson.yaml) [json](../../metadata/sd-01-001.json)\n")
        self.assertEqual([], self.problems())

    def test_a_broken_reference_style_relative_link_is_reported(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n[tài liệu][ref]\n\n[ref]: missing.md\n")
        self.assertProblem("'missing.md' does not resolve")

    def test_a_broken_relative_html_anchor_is_reported(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + '\n<a href="missing.md">tài liệu</a>\n')
        self.assertProblem("'missing.md' does not resolve")

    def test_a_reference_style_relative_link_that_resolves_is_accepted(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n[meta][ref]\n\n[ref]: lesson.yaml\n")
        self.assertEqual([], self.problems())

    def test_a_relative_link_with_a_fragment_or_query_is_checked_by_its_path(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n[a](lesson.yaml#id) [b](lesson.yaml?x=1)\n")
        self.assertEqual([], self.problems())
        self.write_lesson("sd-01-001", body=BODY + "\n[c](missing.md#id)\n")
        self.assertProblem("'missing.md#id' does not resolve")

    def test_anchors_urls_and_mail_links_are_not_relative_links(self) -> None:
        links = "[a](#phan-nguon) [b](https://example.com/x) [c](mailto:a@b.vn) [d](//example.com/x)"
        self.write_lesson("sd-01-001", body=BODY + "\n" + links + "\n")
        self.assertEqual([], self.problems())

    def test_a_link_shaped_text_in_a_code_block_is_not_checked(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n```\n[x](missing.md)\n```\n")
        self.assertEqual([], self.problems())

    def test_a_percent_encoded_relative_link_resolves(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n[meta](lesson%2Eyaml) [json](<../../metadata/sd%2D01%2D001.json>)\n")
        self.assertEqual([], self.problems())

    def test_a_source_map_entry_without_a_snapshot_url_is_reported(self) -> None:
        missing = object()
        for name, value in {"null": None, "empty": "", "blank": "  ", "a number": 5, "a list": [SNAPSHOT],
                            "missing": missing}.items():
            with self.subTest(entry=name):
                entry = source_entry()
                if value is missing:
                    del entry["source_snapshot_url"]
                else:
                    entry["source_snapshot_url"] = value
                data = {**PIN, "categories": [{"id": "sd-01", "lessons": [entry]}]}
                self.source_map.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                self.assertProblem("the source map has no source_snapshot_url for this lesson")

    def test_a_lesson_that_is_not_in_the_source_map_is_not_also_missing_a_snapshot(self) -> None:
        self.write_source_map({})
        found = self.problems()
        self.assertTrue(any("id is not in the source map" in line for line in found), found)
        self.assertFalse(any("snapshot" in line for line in found), found)

    def test_a_lesson_that_does_not_link_the_pinned_snapshot_is_reported(self) -> None:
        self.write_lesson("sd-01-001", body=f"# Bài một\n\n![Sơ đồ]({FIGURE_PATH})\n\nKhông có nguồn.\n")
        self.assertProblem("pinned source snapshot")

    def snapshot_body(self, text: str) -> str:
        return f"# Bài một\n\n![Sơ đồ]({FIGURE_PATH})\n\n{text}\n"

    def test_a_mention_of_a_lesson_without_a_directory_is_reported(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\nĐọc cùng sd-01-011.\n")
        self.assertProblem("mentions sd-01-011")

    def test_a_mention_of_an_existing_lesson_or_of_itself_is_accepted(self) -> None:
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT), "sd-01-002": ("Bài hai", SNAPSHOT)})
        self.write_lesson("sd-01-002")
        self.write_readme(README + "| [sd-01-002](lessons/sd-01-002/lesson.md) | Bài hai |\n")
        self.write_lesson("sd-01-001", body=BODY + "\nXem sd-01-002 và chính sd-01-001.\n")
        self.assertEqual([], self.problems())

    def test_a_snapshot_url_in_a_code_block_is_not_a_link(self) -> None:
        self.write_lesson("sd-01-001", body=self.snapshot_body(f"```\n{SNAPSHOT}\n```"))
        self.assertProblem("pinned source snapshot")

    def test_a_snapshot_url_in_an_html_comment_is_not_a_link(self) -> None:
        for name, comment in {"markdown link": f"<!-- [nguồn]({SNAPSHOT}) -->",
                              "html anchor": f'<!-- <a href="{SNAPSHOT}">nguồn</a> -->'}.items():
            with self.subTest(comment=name):
                self.write_lesson("sd-01-001", body=self.snapshot_body(comment))
                self.assertProblem("pinned source snapshot")

    def test_a_snapshot_url_in_plain_text_is_not_a_link(self) -> None:
        self.write_lesson("sd-01-001", body=self.snapshot_body(f"Nguồn: {SNAPSHOT}"))
        self.assertProblem("pinned source snapshot")

    def test_a_link_to_a_section_of_the_pinned_snapshot_is_a_link_to_it(self) -> None:
        for name, text in {"markdown": f"[nguồn]({SNAPSHOT}#phan-1)",
                           "html": f'<a href="{SNAPSHOT}#phan-1">nguồn</a>',
                           "reference": f"[nguồn][s]\n\n[s]: {SNAPSHOT}#L10-L20"}.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=self.snapshot_body(text))
                self.assertEqual([], self.problems())

    def test_a_link_to_another_file_with_a_fragment_is_not_the_snapshot(self) -> None:
        self.write_lesson("sd-01-001", body=self.snapshot_body(f"[nguồn]({SNAPSHOT}x#phan-1)"))
        self.assertProblem("does not link the pinned source snapshot")

    def test_a_snapshot_given_as_an_html_anchor_is_a_link(self) -> None:
        self.write_lesson("sd-01-001", body=self.snapshot_body(f'<a href="{SNAPSHOT}">nguồn</a>'))
        self.assertEqual([], self.problems())

    def test_href_text_inside_another_attribute_is_not_a_link(self) -> None:
        for name, tag in {"title": f"<a title='href=\"{SNAPSHOT}\"'>nguồn</a>",
                          "no href": f'<a data-x="{SNAPSHOT}">nguồn</a>',
                          "other tag": f'<span href="{SNAPSHOT}">nguồn</span>'}.items():
            with self.subTest(tag=name):
                self.write_lesson("sd-01-001", body=self.snapshot_body(tag))
                self.assertProblem("pinned source snapshot")

    def test_an_upper_case_or_single_quoted_html_anchor_is_a_link(self) -> None:
        for name, tag in {"upper case": f'<A HREF="{SNAPSHOT}">nguồn</A>',
                          "single quotes": f"<a href='{SNAPSHOT}'>nguồn</a>"}.items():
            with self.subTest(tag=name):
                self.write_lesson("sd-01-001", body=self.snapshot_body(tag))
                self.assertEqual([], self.problems())

    def test_a_snapshot_given_as_a_reference_style_link_is_a_link(self) -> None:
        self.write_lesson("sd-01-001", body=self.snapshot_body(f"[nguồn][s]\n\n[s]: {SNAPSHOT}"))
        self.assertEqual([], self.problems())

    def test_every_form_of_source_image_embed_is_reported(self) -> None:
        url = "https://assets.bytebytego.com/diagrams/0001-x.png"
        forms = {
            "inline image": f"![]({url})",
            "reference-style image": f"![x][img]\n\n[img]: {url}",
            "html img": f'<img src="{url}">',
            "html picture": f'<picture><source srcset="{url}"></picture>',
            "bare url": url,
            "upper case host": "HTTPS://ASSETS.BYTEBYTEGO.COM/diagrams/0001-x.png",
            "plain mention of the host": "Ảnh nguồn ở assets.bytebytego.com chưa được mở.",
        }
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + form + "\n")
                self.assertProblem("lessons must not use source images")

    def test_raw_html_outside_the_allow_list_is_reported(self) -> None:
        forms = {
            "picture": '<picture><source srcset="a.svg"></picture>',
            "inline svg": '<svg><image href="a.png"/></svg>',
            "object": '<object data="a.svg"></object>',
            "video": '<video poster="a.png"></video>',
            "iframe": '<iframe src="https://example.com"></iframe>',
            "script": "<script>alert(1)</script>",
            "div": "<div>chữ</div>",
            "a closing tag without its opener": "</div>",
            "an inline closing tag without its opener": "chữ</span> nữa",
            "a void element without a closing tag": "<hr>",
            "an embed with a source": '<embed src="a.svg">',
            "an input": '<input type="text">',
        }
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_lesson("sd-01-001", body=BODY + "\n" + form + "\n")
                self.assertProblem("raw HTML is limited to")

    def test_the_allowed_html_tags_are_accepted(self) -> None:
        body = (BODY + "\nH<sub>2</sub>O, x<sup>2</sup>, <kbd>Ctrl</kbd><br>dòng sau\n\n"
                "<details open>\n<summary>Gợi ý</summary>\n\nĐáp án.\n\n</details>\n")
        self.write_lesson("sd-01-001", body=body)
        self.assertEqual([], self.problems())

    def test_html_tags_inside_code_are_not_raw_html(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n`<div>`\n\n```html\n<picture></picture>\n```\n")
        self.assertEqual([], self.problems())


LLM_ENTRY = "- **LLM** (Large Language Model) — mô hình ngôn ngữ lớn: chương trình sinh văn bản từ câu hỏi.\n"


def svg_with(*strings: str, tag: str = "text") -> str:
    """A valid figure whose drawn text (or <desc>) is the given strings."""
    drawn = "".join(f"<{tag}>{string}</{tag}>" for string in strings)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>Sơ đồ</title>{drawn}</svg>'


class AbbreviationRuleTests(StoreCase):
    """Every abbreviation a lesson or its figure uses is explained in full, in the lesson's own glossary."""

    def lesson(self, intro: str = "Nội dung.", glossary: str | None = LLM_ENTRY, *, after: str = "",
               figure: str = FIGURE) -> None:
        """The fixture lesson with a glossary section (when given) as its first "##", then `after`."""
        section = "" if glossary is None else f"## Từ viết tắt\n\n{glossary}\n"
        body = (f"# Bài\n\n![Sơ đồ của bài](../../diagrams/sd-01-001-main.svg)\n\n{intro}\n\n{section}{after}"
                f"## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n")
        self.write_lesson("sd-01-001", body=body, figure=figure)

    def test_a_lesson_that_uses_no_abbreviation_needs_no_glossary(self) -> None:
        self.lesson("Trình duyệt hỏi máy chủ.", glossary=None)
        self.assertEqual([], self.problems())

    def test_an_abbreviation_with_no_glossary_section_is_reported(self) -> None:
        self.lesson("Bài này nói về LLM và DNS.", glossary=None)
        self.assertProblem("uses the abbreviation(s) DNS, LLM but has no \"## Từ viết tắt\" section")

    def test_an_explained_abbreviation_passes(self) -> None:
        self.lesson("Bài này nói về LLM.")
        self.assertEqual([], self.problems())

    def test_an_abbreviation_the_glossary_leaves_out_is_reported(self) -> None:
        self.lesson("Bài này nói về LLM và DNS.")
        self.assertProblem("uses the abbreviation DNS but the glossary does not explain it")
        self.assertFalse(any("LLM but" in line for line in self.problems()))

    def test_the_figure_text_counts_as_use(self) -> None:
        for where, figure in {"a drawn label": svg_with("Gọi LLM qua mạng"),
                              "the description": svg_with("Gọi LLM qua mạng", tag="desc")}.items():
            with self.subTest(where=where):
                self.lesson(glossary=None, figure=figure)
                self.assertProblem("uses the abbreviation(s) LLM")
                self.lesson(figure=figure)
                self.assertEqual([], self.problems())

    def test_a_heading_in_capitals_is_not_read_for_abbreviations(self) -> None:
        self.lesson(glossary=None, figure=svg_with("ĐƠN HÀNG CÓ TIN MỚI", "HAI MÁY · MỘT SỐ", "TRANG HIỆN RA"))
        self.assertEqual([], self.problems())

    def test_a_mixed_case_term_in_a_heading_in_capitals_still_counts(self) -> None:
        figure = svg_with("HAI MÁY · MỘT IPv4")
        self.lesson(glossary=None, figure=figure)
        self.assertProblem("uses the abbreviation(s) IPv4")
        self.lesson(glossary="- **IPv4** (Internet Protocol version 4) — phiên bản 4 của giao thức Internet.\n", figure=figure)
        self.assertEqual([], self.problems())
        # a term spelled in capitals is the term, whether or not a glossary of the store explains it: OAUTH is OAuth
        figure = svg_with("LUỒNG OAUTH 2.0")
        self.lesson(glossary=None, figure=figure)
        self.assertProblem("uses the abbreviation(s) OAuth")
        self.lesson(glossary="- **OAuth** (Open AUTHorization) — chuẩn cho phép một ứng dụng hành động thay bạn.\n", figure=figure)
        self.assertEqual([], self.problems())

    def test_the_alt_text_of_a_raw_html_image_counts_as_use(self) -> None:
        for where, tag in {"a block": '<img src="../../diagrams/sd-01-001-main.svg" alt="Sơ đồ LLM">',
                           "inside a line": 'Xem <img src="../../diagrams/sd-01-001-main.svg" alt="Sơ đồ LLM"> này.'}.items():
            with self.subTest(where=where):
                self.lesson(tag, glossary=None)
                self.assertProblem("uses the abbreviation(s) LLM")
                self.lesson(tag)
                self.assertEqual([], self.problems())

    def test_the_alt_text_of_the_figure_counts_as_use(self) -> None:
        body = (f"# Bài\n\n![Hình về LLM](../../diagrams/sd-01-001-main.svg)\n\n## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n")
        self.write_lesson("sd-01-001", body=body)
        self.assertProblem("uses the abbreviation(s) LLM")

    def test_text_inside_a_details_block_counts_as_use(self) -> None:
        self.lesson(glossary=None, after="<details>\n<summary>Về LLM</summary>\n\nChi tiết.\n\n</details>\n\n")
        self.assertProblem("uses the abbreviation(s) LLM")

    def test_a_glossary_must_be_the_first_section_of_the_lesson(self) -> None:
        body = (f"# Bài\n\n![Sơ đồ của bài](../../diagrams/sd-01-001-main.svg)\n\n## Đọc hình\n\nVề LLM.\n\n"
                f"## Từ viết tắt\n\n{LLM_ENTRY}\n## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n")
        self.write_lesson("sd-01-001", body=body)
        self.assertProblem('must be the first "##" section')

    def test_a_bullet_that_is_not_in_the_form_is_reported(self) -> None:
        for name, bullet in {"no bold": "- LLM (Large Language Model) — mô hình ngôn ngữ lớn của máy.",
                             "no full form": "- **LLM** — mô hình ngôn ngữ lớn của máy.",
                             "no dash": "- **LLM** (Large Language Model): mô hình ngôn ngữ lớn của máy.",
                             "lower case": "- **llm** (Large Language Model) — mô hình ngôn ngữ lớn của máy."}.items():
            with self.subTest(bullet=name):
                self.lesson("Về LLM.", glossary=bullet + "\n")
                self.assertProblem("is not in the form")

    def test_the_full_form_must_spell_the_abbreviation_out(self) -> None:
        for name, full in {"only Vietnamese": "mô hình ngôn ngữ lớn", "the abbreviation again": "LLM",
                           "another phrase": "Big Neural Network", "wrong first letter": "Very Large Model"}.items():
            with self.subTest(full=name):
                self.lesson("Về LLM.", glossary=f"- **LLM** ({full}) — mô hình ngôn ngữ lớn của máy.\n")
                self.assertProblem("do not give exactly LLM")

    def test_the_full_form_may_skip_little_words_and_use_the_camel_case_of_a_name(self) -> None:
        entries = {"NAPT": "Network Address and Port Translation", "RFC": "Request for Comments",
                   "JSON": "JavaScript Object Notation", "ID": "IDentifier", "SYN": "SYNchronize",
                   "CSSOM": "CSS Object Model", "REST": "REpresentational State Transfer",
                   "HSTS": "HTTP Strict Transport Security", "CSDL": "cơ sở dữ liệu",
                   "CSS": "Cascading Style Sheets", "HTTP": "HyperText Transfer Protocol",
                   "gRPC": "gRPC Remote Procedure Calls", "IPv4": "Internet Protocol version 4",
                   "mTLS": "mutual Transport Layer Security"}
        glossary = "".join(f"- **{abbreviation}** ({full}) — giải thích cho người mới học.\n"
                           for abbreviation, full in entries.items())
        self.lesson(" ".join(entries), glossary=glossary)
        self.assertEqual([], self.problems())

    def test_a_mixed_case_term_needs_a_glossary_bullet_too(self) -> None:
        self.lesson("Dịch vụ dùng gRPC.", glossary=None)
        self.assertProblem("uses the abbreviation(s) gRPC")

    def test_the_first_letter_of_the_full_form_must_be_the_first_of_the_abbreviation(self) -> None:
        self.assertFalse(check.spells("ML", "Large Machine Learning"))
        self.assertTrue(check.spells("ML", "Machine Learning"))

    def test_the_initials_must_be_exactly_the_abbreviation(self) -> None:
        for abbreviation, full in {"API": "Application Broken Programming Interface",
                                   "DNS": "Domain Wrong Name System", "LLM": "Large Language Model Meta",
                                   "TCP": "Transmission Control", "SQL": "Structured Query Language Server"}.items():
            with self.subTest(full=full):
                self.assertFalse(check.spells(abbreviation, full))
        self.assertTrue(check.spells("API", "Application Programming Interface"))

    def test_only_the_little_words_may_be_left_out(self) -> None:
        self.assertTrue(check.spells("NAPT", "Network Address and Port Translation"))
        self.assertTrue(check.spells("RFC", "Request for Comments"))
        self.assertTrue(check.spells("TTL", "Time To Live"))
        self.assertTrue(check.spells("HKDF", "HMAC-based Key Derivation Function"))
        self.assertTrue(check.spells("RBAC", "Role-Based Access Control"))
        self.assertFalse(check.spells("NAPT", "Network Address Elsewhere Port Translation"))

    def test_an_all_caps_word_gives_its_run_or_its_first_letter(self) -> None:
        self.assertTrue(check.spells("CSSOM", "CSS Object Model"))
        self.assertTrue(check.spells("HSTS", "HTTP Strict Transport Security"))
        self.assertTrue(check.spells("QUIC", "Quick UDP Internet Connections"))

    def test_a_unit_symbol_is_explained_by_the_name_of_the_unit(self) -> None:
        self.assertTrue(check.spells("MiB", "Mebibyte"))
        self.assertTrue(check.spells("GiB", "Gibibyte"))
        self.assertFalse(check.spells("MiB", "Megabyte"))
        self.assertFalse(check.spells("MiB", "Mebibyte Extra"))
        self.assertTrue(check.spells("HPACK", "Header Compression for HTTP/2"))
        self.assertFalse(check.spells("HPACK", "Header Compression"))
        self.assertTrue(check.spells("SLSA", "Supply-chain Levels for Software Artifacts"))
        self.assertFalse(check.spells("SLSA", "Supply-chain Levels"))
        self.assertTrue(check.spells("W3C", "World Wide Web Consortium"))
        self.assertTrue(check.spells("SELinux", "Security-Enhanced Linux"))
        self.assertTrue(check.spells("WebAuthn", "Web Authentication"))
        self.assertTrue(check.spells("OpenID", "Open IDentity"))
        self.assertTrue(check.spells("DevOps", "Development and Operations"))
        self.assertTrue(check.spells("DevSecOps", "Development, Security and Operations"))
        self.assertFalse(check.spells("DevSecOps", "Development and Operations"))
        self.assertFalse(check.spells("OpenID", "Open Identity Provider"))
        self.assertFalse(check.spells("W3C", "World Wide Web"))
        self.assertTrue(check.spells("PaaS", "Platform as a Service"))
        self.assertTrue(check.spells("UTC", "Coordinated Universal Time"))
        self.assertFalse(check.spells("UTC", "Universal Time"))
        self.assertTrue(check.spells("EdDSA", "Edwards-curve Digital Signature Algorithm"))
        self.assertFalse(check.spells("EdDSA", "Edwards Digital Signature Algorithm"))
        self.assertTrue(check.spells("NetBIOS", "Network Basic Input/Output System"))
        self.assertFalse(check.spells("NetBIOS", "Network Input/Output System"))
        self.lesson("Bộ nhớ tối thiểu 19 MiB.", glossary=None)
        self.assertProblem("uses the abbreviation(s) MiB")
        self.lesson("Bộ nhớ tối thiểu 19 MiB.", glossary="- **MiB** (Mebibyte) — mebibyte: đơn vị dung lượng bằng 1.048.576 byte.\n")
        self.assertEqual([], self.problems())

    def test_a_recursive_name_gives_its_first_letter(self) -> None:
        self.assertTrue(check.spells("gRPC", "gRPC Remote Procedure Calls"))

    def test_accents_are_dropped_and_dj_is_read_as_d(self) -> None:
        self.assertTrue(check.spells("DV", "đơn vị"))
        self.assertTrue(check.spells("CSDL", "cơ sở dữ liệu"))

    def test_an_entry_with_no_real_explanation_is_reported(self) -> None:
        self.lesson("Về LLM.", glossary="- **LLM** (Large Language Model) — mô hình\n")
        self.assertProblem("glossary entry LLM has no explanation after the dash")

    def test_an_abbreviation_explained_twice_is_reported(self) -> None:
        self.lesson("Về LLM.", glossary=LLM_ENTRY + LLM_ENTRY)
        self.assertProblem("glossary explains LLM twice")

    def test_a_glossary_with_no_bullet_is_reported(self) -> None:
        self.lesson("Nội dung.", glossary="Chưa có gì.\n")
        self.assertProblem("has no bullets")

    def test_a_bullet_may_run_onto_the_next_line(self) -> None:
        self.lesson("Về LLM.", glossary="- **LLM** (Large Language Model) — mô hình\n  ngôn ngữ lớn, sinh văn bản.\n")
        self.assertEqual([], self.problems())

    def test_what_a_glossary_entry_says_is_read_for_abbreviations_too(self) -> None:
        self.lesson("Về LLM.", glossary="- **LLM** (Large Language Model) — mô hình chạy trên GPU.\n")
        self.assertProblem("uses the abbreviation GPU but the glossary does not explain it")

    def test_the_lead_in_of_a_bullet_that_is_not_in_the_form_is_not_also_a_use(self) -> None:
        self.lesson("Nội dung.", glossary="- **LLM** Large Language Model — mô hình ngôn ngữ lớn: chương trình sinh văn bản.\n")
        self.assertProblem("is not in the form")
        self.assertFalse(any("uses the abbreviation" in line for line in self.problems()))

    def test_a_wrapped_line_does_not_glue_an_abbreviation_to_the_next_word(self) -> None:
        for name, intro in {"a soft break": "Bài này nói về LLM\nrất hay.", "a hard break": "Bài này nói về LLM  \nrất hay.",
                            "a break before it": "Bài này nói về\nLLM rất hay.", "an image beside it": "Nói về LLM![hình](../../diagrams/sd-01-001-main.svg)rất hay."}.items():
            with self.subTest(name=name):
                self.lesson(intro, glossary=None)
                self.assertProblem("uses the abbreviation(s) LLM")

    def test_an_address_is_not_prose_but_the_label_of_a_link_is(self) -> None:
        for name, intro in {"an autolink": "Xem <https://example.com/API/TLS> nhé.",
                            "an address in the text": "Xem https://example.org/DNS/SSE nhé.",
                            "an address after a break": "Xem\nhttps://example.org/DNS/SSE\nnhé.",
                            "an address with an uppercase scheme": "Xem HTTPS://example.org/API/TLS nhé.",
                            "an address with a mixed-case scheme": "Xem Ftp://example.org/DNS/SSE nhé.",
                            "an autolink of another scheme": "Xem <irc://example.org/API/TLS> nhé.",
                            "an autolink of a mail address": "Viết tới <API.TLS@example.com> nhé."}.items():
            with self.subTest(name=name):
                self.lesson(intro, glossary=None)
                self.assertEqual([], self.problems())
        self.lesson("Xem [bài về LLM](https://example.com/API/TLS) nhé.", glossary=None)
        self.assertProblem("uses the abbreviation(s) LLM")
        self.assertFalse(any("API" in line or "TLS" in line for line in self.problems()))

    def test_an_address_is_not_prose_in_html_an_image_or_a_figure_either(self) -> None:
        figure = "../../diagrams/sd-01-001-main.svg"
        for name, intro in {"an html block": "<details>HTTPS://example.org/API/TLS</details>",
                            "an html block over lines": "<details>\nXem https://example.org/DNS/SSE nhé.\n</details>",
                            "the alt text of an html image": f'<img src="{figure}" alt="HTTPS://example.org/API/TLS">',
                            "the alt text of an inline html image": f'Xem <img src="{figure}" alt="https://example.org/API"> nhé.',
                            "the alt text of a markdown image": f"![HTTPS://example.org/API/TLS]({figure})"}.items():
            with self.subTest(name=name):
                self.lesson(intro, glossary=None)
                self.assertEqual([], self.problems())
        self.lesson('<details>Xem <a href="https://example.com/API/TLS">bài về LLM</a></details>', glossary=None)
        self.assertProblem("uses the abbreviation(s) LLM")
        self.assertFalse(any("API" in line or "TLS" in line for line in self.problems()))
        self.lesson(glossary=None, figure=svg_with("Gọi https://example.org/API/TLS nhé."))
        self.assertEqual([], self.problems())
        self.lesson(glossary=None, figure=svg_with("LLM tại https://example.org/API/TLS."))
        self.assertProblem("uses the abbreviation(s) LLM")
        self.assertFalse(any("API" in line or "TLS" in line for line in self.problems()))

    def test_an_address_of_any_scheme_is_not_prose(self) -> None:
        figure = "../../diagrams/sd-01-001-main.svg"
        for address in ("wss://example.com/API/TLS", "ssh://host/API", "git+ssh://host/API/TLS.git", "s3://bucket/API/TLS",
                        "file:///API/TLS", "WSS://example.com/API/TLS", "Irc://example.org/DNS/SSE", "tcp://10.0.0.1:80/API"):
            with self.subTest(address=address):
                for name, intro in {"the text": f"Xem {address} nhé.", "an html block": f"<details>{address}</details>",
                                    "the alt text of an html image": f'<img src="{figure}" alt="{address}">',
                                    "the alt text of a markdown image": f"![{address}]({figure})"}.items():
                    with self.subTest(name=name):
                        self.lesson(intro, glossary=None)
                        self.assertEqual([], self.problems())
                self.lesson(glossary=None, figure=svg_with(f"Gọi {address} nhé."))
                self.assertEqual([], self.problems())
                self.lesson(glossary=None, figure=svg_with(address.upper()))  # a label set in capitals, address and all
                self.assertEqual([], self.problems())
        # a colon alone makes no address, and the words around an address are still read
        self.lesson("Note:LLM và wss://example.com/API.", glossary=None)
        self.assertProblem("uses the abbreviation(s) LLM")
        self.assertFalse(any("API" in line for line in self.problems()))

    def test_an_acronym_in_a_capitals_only_label_is_read_when_it_cannot_be_a_word(self) -> None:
        jwt = ("- **JSON** (JavaScript Object Notation) — định dạng văn bản gồm các cặp tên và giá trị.\n"
               "- **JWT** (JSON Web Token) — chuỗi ký tên chứa thông tin người dùng.\n")
        for name, label in {"standalone": "JWT", "among Vietnamese words": "HAI MÁY · JWT", "in a longer label": "JWT HẾT HẠN"}.items():
            with self.subTest(name=name):
                self.lesson(glossary=None, figure=svg_with(label))
                self.assertProblem("uses the abbreviation(s) JWT")
                self.lesson(glossary=jwt, figure=svg_with(label))
                self.assertEqual([], self.problems())
        self.lesson(glossary=None, figure=svg_with("DNS", "LB", "HTTP/2", "SMTP"))
        self.assertProblem("uses the abbreviation(s) DNS, HTTP, LB, SMTP")
        for word in ("HAI MÁY · TIN · HAY · THEO · TRANG · RA", "COOKIE · BALANCER · REQUEST · SESSION · NHANH · CHO",
                     unicodedata.normalize("NFD", "KHÔNG ĐƯỢC · MẠNG CHẬM · TRẠNG THÁI")):  # accents as separate marks
            with self.subTest(words=word):
                self.lesson(glossary=None, figure=svg_with(word))
                self.assertEqual([], self.problems())

    def test_a_plural_or_a_digit_shows_that_a_word_in_capitals_is_an_acronym(self) -> None:
        for label, read in {"APIs": "API", "HAI MÁY · LLMs": "LLM", "2FA": "2FA", "HAI MÁY · 3DES": "3DES", "POP3": "POP",
                            "SHA256": "SHA", "DHCPv4 · HAI MÁY": "DHCP"}.items():
            with self.subTest(label=label):
                self.lesson(glossary=None, figure=svg_with(label))
                self.assertProblem(f"uses the abbreviation(s) {read} but has no")
        self.assertEqual({"API"}, check.label_acronyms(["APIs"]))
        self.assertEqual(set(), check.label_acronyms(["API"]))  # the same letters alone may be a Vietnamese word
        self.assertEqual({"API"}, check.label_acronyms(["API"], frozenset({"API"})))
        self.lesson(glossary="- **2FA** (Two-Factor Authentication) — đăng nhập bằng hai bước.\n", figure=svg_with("2FA · HAI MÁY"))
        self.assertEqual([], self.problems())

    def test_an_acronym_the_store_explains_elsewhere_is_read_in_a_capitals_only_label(self) -> None:
        figure = svg_with("API", "HAI MÁY")
        api = "- **API** (Application Programming Interface) — cách để chương trình này gọi chương trình kia.\n"
        self.lesson(glossary=None, figure=figure)
        self.assertEqual([], self.problems())  # nothing in the store says that API is an acronym
        self.write_lesson("sd-01-002", body=f"# Bài hai\n\n![Sơ đồ của bài](../../diagrams/sd-01-002-main.svg)\n\n"
                                            f"## Từ viết tắt\n\n{api}\n## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n")
        self.assertProblem("sd-01-001: uses the abbreviation(s) API but has no")
        self.assertFalse(any("sd-01-001: uses the abbreviation" in line and "HAI" in line for line in self.problems()))
        self.lesson(glossary=api, figure=figure)
        self.assertFalse(any(line.startswith("sd-01-001: uses the abbreviation") for line in self.problems()))

    def test_a_plain_word_in_a_capitals_only_label_is_not_taken_for_what_another_lesson_explains(self) -> None:
        tin = "- **TIN** (Taxpayer Identification Number) — mã số thuế của một người hay một tổ chức.\n"
        cpu = "- **CPU** (Central Processing Unit) — bộ xử lý trung tâm của máy tính.\n"
        other = (f"# Bài hai\n\n![Sơ đồ của bài](../../diagrams/sd-01-002-main.svg)\n\n## Từ viết tắt\n\n{{entry}}\n"
                 f"## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n")
        self.lesson(glossary=None, figure=svg_with("ĐƠN HÀNG CÓ TIN MỚI", "CPU"))
        self.write_lesson("sd-01-002", body=other.format(entry=tin))
        # TIN is "news" here: the glossary of another lesson does not make it an abbreviation
        self.assertFalse(any(line.startswith("sd-01-001") for line in self.problems()))
        self.write_lesson("sd-01-002", body=other.format(entry=tin + cpu))
        # while a word outside the list is read once another lesson explains it
        self.assertProblem("sd-01-001: uses the abbreviation(s) CPU but has no")
        self.assertFalse(any(line.startswith("sd-01-001") and "TIN" in line for line in self.problems()))
        # the report says how to stop it, whether the lesson has a glossary or not, and only for a word that can be a word
        self.assertProblem("if it is an ordinary word there, add it to PLAIN_LABEL_WORDS")
        self.lesson(glossary=LLM_ENTRY, figure=svg_with("ĐƠN HÀNG CÓ TIN MỚI", "CPU"))
        self.assertProblem("sd-01-001: uses the abbreviation CPU but the glossary does not explain it (it stands in a figure label")
        self.lesson(glossary=None, figure=svg_with("JWT"))
        self.assertProblem("sd-01-001: uses the abbreviation(s) JWT but has no")
        self.assertFalse(any("PLAIN_LABEL_WORDS" in line for line in self.problems()))
        self.assertTrue(all(word.isascii() and word.isalpha() and word.isupper() and set(word) & check.VOWELS
                            for word in check.PLAIN_LABEL_WORDS))  # a word that cannot be taken for an acronym needs no entry

    def test_a_number_word_of_another_number_does_not_stand_for_the_leading_digit(self) -> None:
        for abbreviation, full_form, spelled in (
                ("2FA", "Four Authentication", False), ("3DES", "Double Encryption Standard", False),
                ("2FA", "Fifteen Authentication", False), ("3DES", "Third Data Encryption Standard", True),
                ("2FA", "Fifth Factor Authentication", False), ("3PC", "Triple Phase Commit", True),
                ("2FA", "Two-Factor Authentication", True), ("2FA", "Second Factor Authentication", True),
                ("2PC", "Two-Phase Commit", True), ("3DES", "Triple DES", True),
                ("3DES", "Triple Data Encryption Standard", True),
                # a trailing digit is no stand-in: "Double Data Rate" is a name, and a word without digits is a word
                ("DDR4", "Double Data Rate 4", True), ("DDR4", "Double Data Rate", True),
                ("OTP", "One-Time Password", True), ("IPv4", "Internet Protocol version four", True)):
            with self.subTest(abbreviation=abbreviation, full_form=full_form):
                self.assertEqual(spelled, check.spells(abbreviation, full_form))
        self.lesson("Đăng nhập bằng 2FA.", glossary="- **2FA** (Four Authentication) — đăng nhập bằng hai bước.\n")
        self.assertProblem("glossary spells 2FA out as 'Four Authentication'")

    def test_the_number_inside_an_abbreviation_must_be_the_number_in_its_full_form(self) -> None:
        for abbreviation, full_form, spelled in (
                ("IPv4", "Internet Protocol version 4", True), ("IPv6", "Internet Protocol version 6", True),
                ("IPv4", "Internet Protocol version 6", False), ("IPv6", "Internet Protocol version 4", False),
                ("IPv4", "Internet Protocol version four", True), ("IPv4", "Internet Protocol version six", False),
                ("IPv4", "Internet Protocol version", True), ("IPv4", "Internet Protocol", False),
                ("2FA", "2-Factor Authentication", True), ("2FA", "3-Factor Authentication", False),
                ("2FA", "Two-Factor Authentication", True), ("3DES", "Triple DES", True)):
            with self.subTest(abbreviation=abbreviation, full_form=full_form):
                self.assertEqual(spelled, check.spells(abbreviation, full_form))
        self.lesson("Gửi qua IPv4.", glossary="- **IPv4** (Internet Protocol version 6) — địa chỉ 32 bit.\n")
        self.assertProblem("glossary spells IPv4 out as 'Internet Protocol version 6'")
        self.lesson("Gửi qua IPv4.", glossary="- **IPv4** (Internet Protocol version 4) — địa chỉ 32 bit.\n")
        self.assertEqual([], self.problems())

    def test_an_abbreviation_inside_a_full_form_needs_a_bullet_of_its_own(self) -> None:
        hkdf = "- **HKDF** (HMAC-based Key Derivation Function) — hàm sinh thêm khóa từ một khóa gốc, để mở rộng nó.\n"
        hmac = "- **HMAC** (Hash-based Message Authentication Code) — mã kiểm tra dữ liệu tính từ một khóa bí mật.\n"
        self.lesson("Nói về HKDF.", glossary=hkdf)
        self.assertProblem("sd-01-001: uses the abbreviation HMAC but the glossary does not explain it "
                           "(it stands in the full form of HKDF)")
        self.lesson("Nói về HKDF.", glossary=hmac + hkdf)
        self.assertEqual([], self.problems())
        self.lesson("Nói về HKDF và HMAC.", glossary=hkdf)  # used elsewhere too: the plain message, no pointer to the entry
        self.assertProblem("sd-01-001: uses the abbreviation HMAC but the glossary does not explain it")
        self.assertFalse(any("stands in the full form" in line for line in self.problems()))
        # the entry's own abbreviation, a letter run that spells part of it and a word in capitals are not abbreviations to explain
        self.lesson("Nói về gRPC, SYN và SIGKILL.", glossary=(
            "- **gRPC** (gRPC Remote Procedure Calls) — gọi hàm trên máy khác như gọi hàm trong máy mình.\n"
            "- **SYN** (SYNchronize) — gói đầu của bắt tay, báo muốn mở kết nối.\n"
            "- **SIGKILL** (SIGnal KILL) — tín hiệu buộc dừng tiến trình ngay, tiến trình không kịp dọn dẹp.\n"))
        self.assertEqual([], self.problems())

    def test_a_number_the_full_form_writes_stands_where_the_abbreviation_puts_its_digits(self) -> None:
        for abbreviation, full_form, spelled in (
                ("2FA", "Factor Authentication 2", False), ("2FA", "Factor Two Authentication", False),
                ("IPv4", "4 Internet Protocol version", False), ("IPv4", "Internet 4 Protocol version", False),
                ("3DES", "Data Encryption Standard Triple", False), ("DDR4", "4 Double Data Rate", False),
                ("P2P", "Peer Peer 2", False), ("P2P", "2 Peer Peer", False), ("2FA", "Two-Factor Authentication 2", False),
                ("2FA", "Two-Factor Authentication", True), ("2FA", "2-Factor Authentication", True),
                ("2FA", "Factor Authentication", True), ("IPv4", "Internet Protocol version 4", True),
                ("IPv4", "Internet Protocol version four", True), ("3DES", "Triple Data Encryption Standard", True),
                ("DDR4", "Double Data Rate 4", True), ("P2P", "Peer 2 Peer", True), ("P2P", "Peer-to-Peer", True),
                # an abbreviation with no digits takes no number either, whatever the number
                ("API", "Application Programming Interface 6", False), ("LLM", "Large 99 Language Model", False),
                ("RFC", "Request for Comments 2616", False), ("RFC", "Request for Comments", True),
                ("HPACK", "Header Compression for HTTP/2", True)):  # a name with a full form of its own is read as it is
            with self.subTest(abbreviation=abbreviation, full_form=full_form):
                self.assertEqual(spelled, check.spells(abbreviation, full_form))
        self.assertFalse(check.spells("A" + "1A" * 9, "Alpha " * 10))  # a key with many numbers is refused, not expanded
        self.lesson("Đăng nhập bằng 2FA.", glossary="- **2FA** (Factor Two Authentication) — đăng nhập bằng hai bước.\n")
        self.assertProblem("glossary spells 2FA out as 'Factor Two Authentication'")
        self.lesson("Nói về API.", glossary="- **API** (Application Programming Interface 6) — cách để chương trình này gọi chương trình kia.\n")
        self.assertProblem("glossary spells API out as 'Application Programming Interface 6'")

    def test_a_figure_link_with_a_fragment_a_query_or_an_encoded_name_is_still_the_figure(self) -> None:
        tail = f"## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n"
        for source in ("../../diagrams/sd-01-001-main.svg#view", "../../diagrams/sd-01-001-main.svg?raw=1",
                       "../../diagrams/sd%2D01%2D001-main.svg", "../../diagrams/sd-01-001-main.svg?v=2#top"):
            with self.subTest(source=source):
                self.write_lesson("sd-01-001", body=f"# Bài\n\n![Sơ đồ của bài]({source})\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n{tail}")
                self.assertEqual([], self.problems())
                self.write_lesson("sd-01-001", body=f'# Bài\n\n<img src="{source}" alt="Sơ đồ của bài">\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n{tail}')
                self.assertEqual([], self.problems())
                self.write_lesson("sd-01-001", body=f"# Bài\n\n![Sơ đồ của bài][fig]\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n{tail}\n[fig]: {source}\n")
                self.assertEqual([], self.problems())
                self.write_lesson("sd-01-001", body=f"# Bài\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n![Sơ đồ của bài]({source})\n\n{tail}")
                self.assertProblem("must come after the figure diagrams/sd-01-001-main.svg")

    def test_the_glossary_comes_after_the_figure_not_before_it(self) -> None:
        figure = "![Sơ đồ của bài](../../diagrams/sd-01-001-main.svg)"
        tail = f"## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n"
        self.write_lesson("sd-01-001", body=f"# Bài\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n{figure}\n\n{tail}")
        self.assertProblem("must come after the figure diagrams/sd-01-001-main.svg")
        self.write_lesson("sd-01-001", body=f"# Bài\n\n{figure}\n\nNội dung.\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n{tail}")
        self.assertEqual([], self.problems())
        html = '<img src="../../diagrams/sd-01-001-main.svg" alt="Sơ đồ của bài">'
        self.write_lesson("sd-01-001", body=f"# Bài\n\n{html}\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n{tail}")
        self.assertEqual([], self.problems())

    def test_a_reference_style_figure_is_found_wherever_its_definition_is(self) -> None:
        definition = "[fig]: ../../diagrams/sd-01-001-main.svg\n"
        tail = f"## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n\n{definition}"
        self.write_lesson("sd-01-001", body=f"# Bài\n\n![Sơ đồ của bài][fig]\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n{tail}")
        self.assertEqual([], self.problems())
        self.write_lesson("sd-01-001", body=f"# Bài\n\n{definition}\n![Sơ đồ của bài][fig]\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n"
                                            f"## Liên hệ nguồn\n\n[bài nguồn]({SNAPSHOT}).\n")
        self.assertEqual([], self.problems())
        self.write_lesson("sd-01-001", body=f"# Bài\n\n## Từ viết tắt\n\n{LLM_ENTRY}\n![Sơ đồ của bài][fig]\n\n{tail}")
        self.assertProblem("must come after the figure diagrams/sd-01-001-main.svg")

    def test_words_that_only_look_like_abbreviations_need_no_entry(self) -> None:
        self.lesson("Gửi GET /phone, dùng LEFT JOIN, kiểm tra NULL và trả OK; mở README.", glossary=None)
        self.assertEqual([], self.problems())
        self.lesson("Dockerfile: COPY, RUN, EXPOSE và STOPSIGNAL; kubectl: READY, RESTARTS, STATUS; log: ERROR, END; "
                    "khung GOAWAY.", glossary=None)
        self.assertEqual([], self.problems())

    def test_a_code_span_a_code_block_a_link_and_a_comment_are_not_read(self) -> None:
        intro = ("Gõ `LLM`, xem [trang này](https://example.com/DNS/TLS) hoặc <!-- GPU -->.\n\n"
                 "```\nSELECT * FROM LLM;\nDNS\n```")
        self.lesson(intro, glossary=None)
        self.assertEqual([], self.problems())

    def test_the_sources_section_names_organisations_and_is_not_read(self) -> None:
        self.lesson("Nội dung.", glossary=None, after="## Nguồn đối chiếu\n\nRFC 6202, MDN và WHATWG.\n\n")
        self.assertEqual([], self.problems())

    def test_a_html_block_in_the_sources_section_is_not_read_either(self) -> None:
        sources = "## Nguồn đối chiếu\n\n<details>\n<summary>RFC 6202</summary>\n\nMDN và WHATWG.\n\n</details>\n\n"
        self.lesson("Nội dung.", glossary=None, after=sources)
        self.assertEqual([], self.problems())

    def test_the_forms_an_abbreviation_takes(self) -> None:
        found = check.abbreviations_in("APIs, HTTP/2, REST/JSON, TCP/UDP, (SSE), \"DNS\", HTTPS.")
        self.assertEqual({"API", "HTTP", "REST", "JSON", "TCP", "UDP", "SSE", "DNS", "HTTPS"}, found)
        self.assertEqual({"gRPC", "IPv4", "mTLS", "IaC", "MoE", "MiB"}, check.abbreviations_in("gRPC qua IPv4 và mTLS, IaC cùng MoE, 19 MiB."))
        self.assertEqual({"PaaS", "IaaS", "SaaS", "FaaS", "BaaS", "W3C", "SELinux", "WebAuthn", "OpenID", "DevOps", "DevSecOps",
                          "GitOps", "NoOps"},
                         check.abbreviations_in("PaaS, IaaS, SaaS, FaaS và BaaS; chuẩn W3C; SELinux cùng WebAuthn; OpenID Connect; "
                                                "DevOps, DevSecOps, GitOps và NoOps."))
        self.assertEqual({"vCPU", "MiB", "OAuth", "gRPC", "IPv4", "NoSQL", "API"},
                         check.abbreviations_in("16 vCPUs, 4 MiBs, OAuth2, gRPCs, IPv4s, NoSQLs và API2."))
        self.assertEqual({"EdDSA", "NetBIOS"}, check.abbreviations_in("Ký bằng EdDSA, chia sẻ qua NetBIOS."))
        self.assertEqual({"DHCP", "TLS", "SHA"}, check.abbreviations_in("DHCPv4 và DHCPv6, TLSv1.3, SHA256."))
        for text in ("MAX_SIZE", "A80", "WebSocket", "I", "ĐƠN HÀNG", "TÓM", "myIPv4", "JavaScript", "GitHub",
                     "OAuthority", "vCPUx", "gRPCsx"):
            with self.subTest(text=text):
                self.assertEqual(set(), check.abbreviations_in(text))

    def test_a_name_that_carries_an_abbreviation_is_read_as_that_abbreviation(self) -> None:
        self.assertEqual({"AI", "LLM"}, check.abbreviations_in("OpenAI và LLMWare."))
        self.assertEqual({"AI", "SQL", "OS", "OOM", "DB", "GPT"},
                         check.abbreviations_in("OpenAI's, MySQL8, macOS, OOMKilled, TimescaleDBs và ChatGPT."))
        for text in ("myOpenAI", "OpenAIX", "OpenAi", "MacOS", "Github"):  # a longer word is not the name
            with self.subTest(text=text):
                self.assertEqual(set(), check.abbreviations_in(text))
        self.assertEqual({"AI"}, check.abbreviations_in("HAI MÁY · OpenAI", capitals=False))
        self.assertEqual({"AI"}, check.abbreviations_in("HAI MÁY · OPENAI", capitals=False))
        self.assertEqual(set(), check.abbreviations_in("HAI MÁY · OPENAIX", capitals=False))
        for where, figure in {"a drawn label": svg_with("Gọi OpenAI qua mạng"),
                              "the description": svg_with("Gọi OpenAI qua mạng", tag="desc")}.items():
            with self.subTest(where=where):
                self.lesson("Nội dung.", glossary=None, figure=figure)
                self.assertProblem("uses the abbreviation(s) AI")
        entry = "- **AI** (Artificial Intelligence) — trí tuệ nhân tạo: máy làm việc cần trí thông minh của người."
        self.lesson("Bài nói về OpenAI.", glossary=None)
        self.assertProblem("uses the abbreviation(s) AI")
        self.lesson("Bài nói về OpenAI.")
        self.assertProblem("uses the abbreviation AI but the glossary does not explain it")
        self.lesson("Bài nói về OpenAI.", glossary=entry)
        self.assertEqual([], self.problems())

    def test_a_configured_term_in_capitals_is_the_term(self) -> None:
        self.assertEqual({"OAuth"}, check.abbreviations_in("OAUTH 2.0", capitals=False))
        self.assertEqual({"OAuth", "SQL", "IPv4", "W3C"}, check.abbreviations_in("Dùng OAUTH2, MYSQL's, IPV4 và W3C."))
        self.assertEqual({"AI"}, check.abbreviations_in("HAI MÁY · OPENAI", capitals=False))
        self.assertEqual(set(), check.abbreviations_in("OAUTHORITY", capitals=False))
        self.assertEqual(set(), check.abbreviations_in("XOAUTH", capitals=False))
        self.assertEqual({"OAUTHORITY", "MYSQLX"}, check.abbreviations_in("OAUTHORITY và MYSQLX"))
        entry = "- **OAuth** (Open AUTHorization) — chuẩn ủy quyền mở: cho ứng dụng làm việc thay bạn."
        self.lesson(glossary=None, figure=svg_with("OAUTH 2.0:"))
        self.assertProblem("uses the abbreviation(s) OAuth")
        self.lesson(glossary=entry, figure=svg_with("OAUTH 2.0:"))
        self.assertEqual([], self.problems())

    def test_an_abbreviation_that_begins_with_a_digit_is_read_and_explained(self) -> None:
        self.assertEqual({"2FA", "3DES", "2PC", "3PC"}, check.abbreviations_in("Bật 2FA, mã hoá 3DES, commit 2PC hoặc 3PC (2FAs)."))
        for text in ("2fa, 5xx", "A80 và 4K", "10 GB"):
            with self.subTest(text=text):
                self.assertNotIn("2FA", check.abbreviations_in(text))
        self.assertEqual({"GB"}, check.abbreviations_in("10 GB"))
        entry = "- **2FA** (Two-Factor Authentication) — xác thực bằng hai yếu tố khác nhau."
        self.lesson("Bật 2FA cho tài khoản.", glossary=None)
        self.assertProblem("uses the abbreviation(s) 2FA")
        self.lesson("Bật 2FA cho tài khoản.")
        self.assertProblem("uses the abbreviation 2FA but the glossary does not explain it")
        self.lesson("Bật 2FA cho tài khoản.", glossary=entry)
        self.assertEqual([], self.problems())
        self.lesson("Bật 2FA cho tài khoản.", glossary=entry.replace("Two-Factor", "Two Wrong"))
        self.assertProblem("whose initials do not give exactly 2FA")

    def test_the_digit_of_an_abbreviation_stands_for_a_number_word(self) -> None:
        for abbreviation, full_form, spelled in (("2FA", "Two-Factor Authentication", True),
                                                 ("2FA", "Factor Authentication", True),
                                                 ("3DES", "Triple Data Encryption Standard", True),
                                                 ("3DES", "Triple DES", True),
                                                 ("2PC", "Two-Phase Commit", True),
                                                 ("2PC", "Second Phase Commit", True),
                                                 ("2FA", "Two Wrong Authentication", False),
                                                 ("2FA", "Triple Factor Authentication", False),
                                                 ("3DES", "Two Data Encryption Standard", False),
                                                 ("2PC", "Nine Phase Commit", False),
                                                 ("FA", "Two Factor Authentication", False)):
            with self.subTest(abbreviation=abbreviation, full_form=full_form):
                self.assertEqual(spelled, check.spells(abbreviation, full_form))

    def test_the_text_nodes_of_a_figure_label_are_separate_words(self) -> None:
        for name, label in {"lines": '<tspan x="1" dy="1">LLM</tspan><tspan x="1" dy="14">máy chủ</tspan>',
                            "styled runs": 'Gọi <tspan font-weight="bold">LLM</tspan><tspan>máy chủ</tspan>.'}.items():
            with self.subTest(name=name):
                self.lesson(glossary=None, figure=svg_with(label))
                self.assertProblem("uses the abbreviation(s) LLM")
                self.lesson(figure=svg_with(label))
                self.assertEqual([], self.problems())


class RobustnessTests(StoreCase):
    """Whatever an author types, the checker reports problems and keeps going; it never raises."""

    ODD_VALUES = [None, True, 0, 1.5, "", " ", "draft", "x" * 400, [], ["draft"], [[1]], {}, {"a": 1}, [{"a": 1}],
                  "2026-10-12", "sd-01-001", 10**30]

    def run_checker(self, data: object = None, *, raw: str | bytes | None = None) -> list[str]:
        self.write_lesson("sd-01-001")
        content = raw if raw is not None else json.dumps(data, ensure_ascii=False)
        (self.store / "metadata" / "sd-01-001.json").write_bytes(content.encode() if isinstance(content, str) else content)
        return self.problems()

    def test_an_odd_value_for_any_metadata_field_is_reported_not_raised(self) -> None:
        for key in sorted(check.METADATA_REQUIRED | check.METADATA_OPTIONAL):
            for value in self.ODD_VALUES:
                with self.subTest(key=key, value=value):
                    self.run_checker(self.meta(**{key: value}))

    def test_an_odd_value_inside_a_nested_record_is_reported_not_raised(self) -> None:
        verification = all_happened()
        snapshot = {**self.meta()["source_snapshot"], "snapshot_url": SNAPSHOT, "blob_identity_status": "x", "note": "x",
                    "retrieved_body_sha256": "c" * 64, "retrieved_body_bytes": 5}
        related = {"lesson_id": "sd-01-002", "relation": "x", "reason_vi": "y"}
        migration = {"source_repository": "a/b", "source_commit_sha": "c" * 40, "destination_repository": "a/c",
                     "imported_on": "2026-10-13"}
        for value in self.ODD_VALUES:
            for step in verification:
                for key in sorted(verification[step]) + ["extra"]:
                    with self.subTest(step=step, key=key, value=value):
                        self.run_checker(self.meta(verification={**verification, step: {**verification[step], key: value}}))
                with self.subTest(step=step, value=value):
                    self.run_checker(self.meta(verification={**verification, step: value}))
            for key in sorted(snapshot):
                with self.subTest(snapshot=key, value=value):
                    self.run_checker(self.meta(source_snapshot={**snapshot, key: value}))
            for key in sorted(GOOD_CLAIM) + ["sources", "id"]:
                with self.subTest(claim=key, value=value):
                    self.run_checker(self.meta(claims=[{**GOOD_CLAIM, key: value}]))
            for key in sorted(related):
                with self.subTest(related=key, value=value):
                    self.run_checker(self.meta(related=[{**related, key: value}]))
            for key in sorted(migration):
                with self.subTest(migration=key, value=value):
                    self.run_checker(self.meta(migration={**migration, key: value}))
            for key in sorted(check.IMAGE_EVIDENCE_KEYS):
                with self.subTest(evidence=key, value=value):
                    self.run_checker(self.meta(image_evidence=[{**GOOD_EVIDENCE, key: value}]))
            for key in ("claims", "prerequisites", "related", "source_deviations", "source_only_trivia", "prior_reviews",
                        "image_evidence"):
                with self.subTest(list=key, item=value):
                    self.run_checker(self.meta(**{key: [value]}))

    def test_a_lesson_yaml_that_is_not_a_mapping_or_has_odd_keys_is_reported_not_raised(self) -> None:
        for name, raw in {"a list": "- a\n- b\n", "a string": "hello\n", "empty": "", "a number": "3\n",
                          "mixed key types": "1: a\nid: x\n", "a null key": "null: a\nid: x\n",
                          "a boolean key": "true: a\n", "a date key": "2026-10-12: a\n"}.items():
            with self.subTest(file=name):
                self.write_lesson("sd-01-001")
                (self.store / "lessons" / "sd-01-001" / "lesson.yaml").write_text(raw, encoding="utf-8")
                self.assertIsInstance(self.problems(), list)

    def test_a_malformed_evidence_url_is_a_problem(self) -> None:
        for url in ["https://[", "http://[::1", "https://[x]/a.png", "https://a b/c", "//", ":", "http://exa\x00mple.com"]:
            with self.subTest(url=url):
                data = self.meta(image_evidence=[{"url": url, "sha256": "a" * 64, "retrieved_on": "2026-10-12"}])
                self.assertTrue(any("image_evidence" in line for line in self.run_checker(data)))

    def test_odd_json_text_is_reported_not_raised(self) -> None:
        odd = {"very deep nesting": "[" * 200_000, "deep objects": '{"a":' * 50_000, "a null byte": '{"id": "\x00"}',
               "a huge number": '{"retrieved_body_bytes": ' + "9" * 5000 + "}", "a lone surrogate": '{"id": "\\ud800"}',
               "nan": '{"id": NaN}', "a bom": "﻿{}"}
        for name, raw in odd.items():
            with self.subTest(file=name):
                self.run_checker(raw=raw)
                self.write_lesson("sd-01-001")
                self.sync_progress()
                (self.store / "progress.json").write_text(raw, encoding="utf-8")
                self.assertIsInstance(self.check_now(), list)
                self.source_map.write_text(raw, encoding="utf-8")
                self.assertIsInstance(self.check_now(), list)
                self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT)})

    def check_now(self) -> list[str]:
        return [str(problem) for problem in check.check_store(self.store, self.source_map)]

    def test_odd_svg_files_are_reported_not_raised(self) -> None:
        laughs = ('<?xml version="1.0"?><!DOCTYPE l [<!ENTITY a "aaaaaaaaaa"><!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">'
                  '<!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;"><!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;">]><svg>&d;</svg>')
        odd = {"invalid utf-8": b"\xff\xfe<svg/>", "a latin-1 declaration": b'<?xml version="1.0" encoding="latin-1"?><svg>\xe9</svg>',
               "unknown encoding": b'<?xml version="1.0" encoding="nope"?><svg/>',
               "entity expansion": laughs.encode(), "deep nesting": b"<svg>" + b"<g>" * 3000 + b"</g>" * 3000 + b"</svg>",
               "a null byte": b"<svg>\x00</svg>", "a bom": b"\xef\xbb\xbf<svg/>", "only a comment": b"<!-- x -->"}
        for name, content in odd.items():
            with self.subTest(file=name):
                self.write_figure("sd-01-001", content)
                self.assertIsInstance(self.problems(), list)

    def test_a_store_file_that_is_a_directory_is_reported_not_raised(self) -> None:
        lesson_dir = self.write_lesson("sd-01-001")
        for path, fragment in {lesson_dir / "lesson.md": "lesson.md is missing", lesson_dir / "lesson.yaml": "lesson.yaml is missing",
                               self.store / "metadata" / "sd-01-001.json": "metadata/sd-01-001.json is missing",
                               self.store / "diagrams" / "sd-01-001-main.svg": "diagrams/sd-01-001-main.svg is missing",
                               self.store / "progress.json": "progress.json: is missing"}.items():
            with self.subTest(name=path.name):
                self.write_lesson("sd-01-001")
                self.sync_progress()
                path.unlink()
                path.mkdir()
                self.auto_progress = False
                try:
                    self.assertProblem(fragment)
                finally:
                    self.auto_progress = True
                path.rmdir()

    def test_a_lesson_yaml_that_is_a_directory_is_only_missing(self) -> None:
        lesson_dir = self.write_lesson("sd-01-001")
        (lesson_dir / "lesson.yaml").unlink()
        (lesson_dir / "lesson.yaml").mkdir()
        found = self.problems()
        self.assertTrue(any("lesson.yaml is missing" in line for line in found), found)
        self.assertFalse(any("does not parse" in line for line in found), found)

    def test_pathological_markdown_is_reported_not_raised(self) -> None:
        deep = {"nested quotes": "> " * 3000 + "x", "nested lists": "".join("  " * i + "- a\n" for i in range(400)),
                "unmatched brackets": "[" * 20000, "unmatched emphasis": "*_" * 20000, "a long line": "a" * 200_000,
                "many fences": "```\n" * 5000, "many tags": "<details>" * 5000, "nul bytes": "a\x00b\x00",
                "empty": "", "only whitespace": " \n\t\n", "crlf": "# a\r\n\r\n```\r\nx\r\n```\r\n"}
        for name, body in deep.items():
            with self.subTest(markdown=name):
                self.write_lesson("sd-01-001", body=body)
                self.write_readme(body)
                for page in check.STORE_PAGES[1:]:
                    (self.store / page).write_text(body, encoding="utf-8")
                self.assertIsInstance(self.problems(), list)

    def test_a_readme_that_is_a_directory_is_reported_not_raised(self) -> None:
        (self.store / "README.md").unlink()
        (self.store / "README.md").mkdir()
        self.assertProblem("README.md: is missing")

    def test_odd_links_and_paths_in_lesson_md_and_the_pages_are_reported_not_raised(self) -> None:
        destinations = ["a" * 300 + ".md", "x/" + "b" * 300 + ".svg", "%00", "a%00b.md", "..", "../..", "/", "//",
                        "http://[", "mailto:", "#", "?x", "<>", " ", "\\"]
        for destination in destinations:
            with self.subTest(destination=destination):
                self.write_lesson("sd-01-001", body=BODY + f"\n[x](<{destination}>) ![y](<{destination}>)\n"
                                  f'<a href="{destination}">z</a> <img src="{destination}" srcset="{destination} 1x">\n')
                self.write_readme(README + f"\n[x](<{destination}>)\n")
                (self.store / "PROGRESS.md").write_text(f"[x](<{destination}>) ![y](<{destination}>)\n", encoding="utf-8")
                (self.store / "lessons" / "sd-01-001.md").write_text(f"[x](<{destination}>)\n", encoding="utf-8")
                self.assertIsInstance(self.problems(), list)

    def test_odd_values_in_progress_json_are_reported_not_raised(self) -> None:
        self.write_lesson("sd-01-001")
        for key in sorted(check.PROGRESS_REQUIRED | {"active_batch_ids", "prior_repository_reviewed_ids", "updated_on"}):
            for value in self.ODD_VALUES:
                with self.subTest(key=key, value=value):
                    self.sync_progress(**{key: value})
                    self.assertIsInstance(self.check_now(), list)
        for raw in ("[]", '"x"', "null", "3", "{"):
            with self.subTest(raw=raw):
                (self.store / "progress.json").write_text(raw, encoding="utf-8")
                self.assertIsInstance(self.check_now(), list)

    def test_odd_source_map_entries_do_not_break_the_checks_that_follow_them(self) -> None:
        for key in ("title_vi", "source_path", "source_blob_sha", "source_snapshot_url", "same_source_as"):
            for value in self.ODD_VALUES:
                with self.subTest(key=key, value=value):
                    data = {**PIN, "categories": [{"id": "sd-01", "lessons": [source_entry(**{key: value})]}]}
                    self.source_map.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                    self.write_lesson("sd-01-001", meta=self.meta(source_ref="sd-01-001"))
                    self.assertIsInstance(self.problems(), list)
                    self.write_lesson("sd-01-001", meta=self.meta(source_ref="sd-01-002"))
                    self.assertIsInstance(self.problems(), list)


class SourceMapRuleTests(StoreCase):
    """A hand-edited source-map.json that is wrong is a problem to report, not a traceback."""

    def test_a_source_map_that_cannot_be_read_is_reported_not_raised(self) -> None:
        unreadable, no_categories = "source map: cannot be read", "source map: has no 'categories' list"
        cases = {"invalid json": (b"{", unreadable), "invalid utf-8": (b"\xff\xfe{}", unreadable), "empty": (b"", unreadable),
                 "a list": (b"[]", no_categories), "a string": (b'"x"', no_categories), "null": (b"null", no_categories),
                 "no categories": (b"{}", no_categories), "categories is an object": (b'{"categories": {}}', no_categories),
                 "categories is null": (b'{"categories": null}', no_categories)}
        for name, (content, fragment) in cases.items():
            with self.subTest(source_map=name):
                self.source_map.write_bytes(content)
                self.assertProblem(fragment)

    def test_a_missing_source_map_is_reported_not_raised(self) -> None:
        self.source_map.unlink()
        self.assertProblem("source map: cannot be read")

    def test_a_malformed_category_or_lesson_entry_is_reported_not_raised(self) -> None:
        good = source_entry()
        no_lessons, no_id = "has no 'lessons' list", "has no string 'id'"
        cases = {"a category that is not an object": ([1], no_lessons), "a category with no lessons": ([{"id": "sd-01"}], no_lessons),
                 "lessons that are not a list": ([{"lessons": {}}], no_lessons),
                 "a lesson that is not an object": ([{"lessons": [5]}], no_id),
                 "a lesson without an id": ([{"lessons": [{"title_vi": "x"}]}], no_id),
                 "an id that is null": ([{"lessons": [{"id": None}]}], no_id),
                 "an id that is a number": ([{"lessons": [{"id": 5}]}], no_id),
                 "an id that is a list": ([{"lessons": [{"id": ["sd-01-001"]}]}], no_id),
                 "a lesson listed twice": ([{"lessons": [good, good]}], "sd-01-001 is listed twice"),
                 "a lesson listed in two categories": ([{"lessons": [good]}, {"lessons": [good]}], "sd-01-001 is listed twice")}
        for name, (categories, fragment) in cases.items():
            with self.subTest(entry=name):
                self.source_map.write_text(json.dumps({**PIN, "categories": categories}), encoding="utf-8")
                self.assertProblem(fragment)

    def test_the_rest_of_the_store_is_still_checked_when_the_source_map_is_malformed(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n```\nopen\n")
        self.source_map.write_text("{", encoding="utf-8")
        found = self.problems()
        self.assertTrue(any(line.startswith("source map: ") for line in found), found)
        self.assertTrue(any("unclosed code fence" in line for line in found), found)

    def test_a_good_source_map_with_two_categories_is_fine(self) -> None:
        data = {**PIN, "categories": [{"id": "a", "lessons": [source_entry()]}, {"id": "b", "lessons": []}]}
        self.source_map.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.assertEqual([], self.problems())


class ReadmeRuleTests(StoreCase):
    def test_a_lesson_missing_from_the_readme_is_reported(self) -> None:
        self.write_readme("# Kho\n")
        self.assertProblem("does not link lessons/sd-01-001/lesson.md")

    def three_lessons(self) -> None:
        self.write_source_map({lesson_id: (title, SNAPSHOT) for lesson_id, title in TITLES.items()})
        for lesson_id in TITLES:
            self.write_lesson(lesson_id)

    def row(self, lesson_id: str) -> str:
        return f"| [{lesson_id}](lessons/{lesson_id}/lesson.md) | Bài |\n"

    def readme_of(self, *rows: str) -> str:
        return "# Kho\n\n| ID | Bài |\n|---|---|\n" + "".join(rows)

    def test_lessons_listed_in_source_order_are_accepted(self) -> None:
        self.three_lessons()
        self.write_readme(self.readme_of(*(self.row(f"sd-01-00{n}") for n in (1, 2, 3))))
        self.assertEqual([], self.problems())

    def test_lessons_listed_out_of_source_order_are_reported(self) -> None:
        self.three_lessons()
        for order in ((2, 1, 3), (1, 3, 2), (3, 2, 1)):
            with self.subTest(order=order):
                self.write_readme(self.readme_of(*(self.row(f"sd-01-00{n}") for n in order)))
                self.assertProblem("lists the lessons out of source order")

    def test_source_order_holds_across_markdown_html_and_reference_links(self) -> None:
        self.three_lessons()
        self.write_readme(self.readme_of(
            '| <a href="lessons/sd-01-002/lesson.md">sd-01-002</a> | Bài |\n', "| [sd-01-001][one] | Bài |\n",
            self.row("sd-01-003")) + "\n[one]: lessons/sd-01-001/lesson.md\n")
        self.assertProblem("lists the lessons out of source order")
        self.write_readme(self.readme_of("| [sd-01-001][one] | Bài |\n",
                                         '| <a href="lessons/sd-01-002/lesson.md">sd-01-002</a> | Bài |\n',
                                         self.row("sd-01-003")) + "\n[one]: lessons/sd-01-001/lesson.md\n")
        self.assertEqual([], self.problems())
        self.write_readme(self.readme_of("| [sd-01-002](./lessons/sd-01-002/lesson.md) | Bài |\n", self.row("sd-01-001"),
                                         self.row("sd-01-003")))
        self.assertProblem("lists the lessons out of source order")

    def test_a_lesson_linked_twice_counts_where_it_is_first_linked(self) -> None:
        self.three_lessons()
        self.write_readme(self.readme_of(*(self.row(f"sd-01-00{n}") for n in (1, 2, 3))) + "\n[lại](lessons/sd-01-001/lesson.md#a)\n")
        self.assertEqual([], self.problems())

    def test_a_missing_lesson_is_reported_as_missing_not_as_out_of_order(self) -> None:
        self.three_lessons()
        self.write_readme(self.readme_of(self.row("sd-01-001"), self.row("sd-01-003")))
        found = self.problems()
        self.assertTrue(any("does not link lessons/sd-01-002/lesson.md" in line for line in found), found)
        self.assertFalse(any("out of source order" in line for line in found), found)

    def test_a_readme_row_left_behind_for_a_deleted_lesson_is_reported(self) -> None:
        self.write_readme(README + "| [sd-01-009](lessons/sd-01-009/lesson.md) | Bài đã xóa |\n")
        self.assertProblem("relative link 'lessons/sd-01-009/lesson.md' does not resolve")
        self.write_readme(README + "[x][ref]\n\n[ref]: lessons/sd-01-009/lesson.md#phan-1\n")
        self.assertProblem("relative link 'lessons/sd-01-009/lesson.md#phan-1' does not resolve")
        self.write_readme(README + '<a href="lessons/sd-01-009/lesson.md">x</a>\n')
        self.assertProblem("'lessons/sd-01-009/lesson.md' does not resolve")
        self.assertFalse(any("out of source order" in line for line in self.problems()), self.problems())

    def test_readme_links_that_are_not_relative_paths_are_not_looked_up(self) -> None:
        self.write_readme(README + "[web](https://example.com/x) [mail](mailto:a@b.c) [top](#kho)\n"
                          "[again](lessons/sd-01-001/lesson.md#phan-1)\n")
        self.assertEqual([], self.problems())

    def test_the_store_holds_only_its_documented_entries(self) -> None:
        for name in ("copied-source.png", "notes.md", ".DS_Store", "figure.svg", "progress.yaml", "lesson.md"):
            with self.subTest(file=name):
                (self.store / name).write_bytes(b"x")
                self.assertProblem(f"{name}: is not allowed in the store")
                (self.store / name).unlink()
        (self.store / "images").mkdir()
        self.assertProblem("images: is not allowed in the store")

    def test_raw_html_outside_the_allow_list_in_the_readme_is_reported(self) -> None:
        for name, html in {"a table": "<table><tr><td>draft</td></tr></table>", "a div": "<div>draft</div>",
                           "a closing tag": "</table>", "a span": "<span>draft</span>"}.items():
            with self.subTest(html=name):
                self.write_readme(README + "\n" + html + "\n")
                self.assertProblem("README.md: uses <")

    def test_the_allowed_raw_html_in_the_readme_is_fine(self) -> None:
        self.write_readme(README + '\n<details><summary>Thêm</summary>\n\nchữ<br/>\n\n</details>\n'
                          '<a href="lessons/sd-01-001/lesson.md">x</a>\n')
        self.assertEqual([], self.problems())

    def test_the_readme_embeds_no_image(self) -> None:
        (self.store / "copied-source.png").write_bytes(b"x")
        (self.store / "figure.svg").write_text("<svg/>", encoding="utf-8")
        forms = {"inline png": "![source](copied-source.png)", "inline svg": "![f](figure.svg)",
                 "reference": "![f][i]\n\n[i]: figure.svg", "html img": '<img src="figure.svg" alt="f">',
                 "html srcset": '<img srcset="figure.svg 1x" alt="f">', "html img without a source": "<img alt='f'>"}
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_readme(README + "\n" + form + "\n")
                self.assertProblem("README.md: embeds the image")

    def test_a_readme_may_link_to_an_image_without_embedding_it(self) -> None:
        (self.store / "figure.svg").write_text("<svg/>", encoding="utf-8")
        self.write_readme(README + "\n[hình](figure.svg)\n")
        self.assertFalse(any("embeds the image" in line for line in self.problems()), self.problems())

    def test_a_link_that_climbs_out_of_the_store_is_reported(self) -> None:
        outside = self.root / "exists.md"
        outside.write_text("x", encoding="utf-8")
        self.write_lesson("sd-01-001", body=BODY + "\n[x](../../../exists.md)\n")
        self.assertProblem("relative link '../../../exists.md' does not resolve")
        self.write_readme(README + "\n[x](../exists.md)\n")
        self.assertProblem("README.md: relative link '../exists.md' does not resolve")

    def test_a_link_that_climbs_far_out_of_the_store_is_reported_even_if_the_file_exists(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n[x](" + "../" * 40 + "etc/hostname)\n")
        self.assertProblem("does not resolve")

    def test_a_link_that_climbs_and_comes_back_into_the_store_is_fine(self) -> None:
        self.write_lesson("sd-01-001", body=BODY + "\n[x](../../lessons/sd-01-001/lesson.yaml)\n")
        self.write_readme(README + "\n[x](lessons/../README.md)\n")
        self.assertEqual([], self.problems())

    def test_a_root_relative_readme_link_is_reported(self) -> None:
        (self.root / "exists.md").write_text("x", encoding="utf-8")
        for destination in (self.root / "exists.md", self.store / "lessons" / "sd-01-001" / "lesson.md"):
            with self.subTest(destination=str(destination)):
                self.write_readme(README + f"\n[x]({destination})\n")
                self.assertProblem("README.md: relative link")

    def test_a_missing_readme_is_reported(self) -> None:
        (self.store / "README.md").unlink()
        self.assertProblem("README.md: is missing")

    def test_a_status_word_in_a_readme_row_is_reported(self) -> None:
        row = "| [sd-01-001](lessons/sd-01-001/lesson.md) | Bài một | draft |\n"
        self.write_readme("# Kho\n\n| ID | Bài | Trạng thái |\n|---|---|---|\n" + row)
        self.assertProblem("repeats a lesson status")

    def test_a_status_word_in_the_header_row_is_reported(self) -> None:
        self.write_readme("# Kho\n\n| ID | Bài | draft |\n|---|---|---|\n| [sd-01-001](lessons/sd-01-001/lesson.md) | Bài một | x |\n")
        self.assertProblem("repeats a lesson status")

    def test_the_old_status_words_are_not_the_statuses_any_more(self) -> None:
        for cell in ("planned", "drafted", "approved"):
            with self.subTest(cell=cell):
                row = f"| [sd-01-001](lessons/sd-01-001/lesson.md) | Bài một | {cell} |\n"
                self.write_readme("# Kho\n\n| ID | Bài | Ghi chú |\n|---|---|---|\n" + row)
                self.assertEqual([], self.problems())

    def test_a_formatted_or_capitalised_status_in_a_readme_row_is_reported(self) -> None:
        forms = {"bold": "**done**", "code": "`draft`", "capital": "Done", "html": "<b>review</b>",
                 "trailing dot": "draft.", "emphasis": "_draft_", "link": "[draft](https://example.com)",
                 "bold link": "[**done**](lessons/sd-01-001/lesson.md)", "reference link": "[review][s]",
                 "entity": "&#100;raft", "image alt": "![x](a.svg) draft",
                 "strikethrough": "~~draft~~", "escaped asterisks": "\\*done\\*"}
        for name, cell in forms.items():
            with self.subTest(form=name):
                row = f"| [sd-01-001](lessons/sd-01-001/lesson.md) | Bài một | {cell} |\n"
                self.write_readme("# Kho\n\n| ID | Bài | Ghi chú |\n|---|---|---|\n" + row
                                  + "\n[s]: https://example.com\n")
                self.assertProblem("repeats a lesson status")

    def test_a_status_in_a_row_whose_lesson_link_is_a_reference_is_reported(self) -> None:
        row = "| [sd-01-001][one] | Bài một | draft |\n\n[one]: lessons/sd-01-001/lesson.md\n"
        self.write_readme("# Kho\n\n| ID | Bài | Ghi chú |\n|---|---|---|\n" + row)
        found = self.problems()
        self.assertTrue(any("repeats a lesson status" in line for line in found), found)
        self.assertFalse(any("does not link" in line for line in found), found)

    def test_an_html_anchor_whose_title_mentions_the_path_is_not_a_readme_link(self) -> None:
        path = "lessons/sd-01-001/lesson.md"
        self.write_readme(f"# Kho\n\n<a title='href=\"{path}\"'>bài một</a>\n")
        self.assertProblem("does not link lessons/sd-01-001/lesson.md")

    def test_a_table_without_outer_pipes_or_with_an_indented_row_is_still_inspected(self) -> None:
        link = "[sd-01-001](lessons/sd-01-001/lesson.md)"
        forms = {"no outer pipes": f"ID | Bài | Ghi chú\n--- | --- | ---\n{link} | Bài một | draft",
                 "indented rows": f"  | ID | Bài | Ghi chú |\n  |---|---|---|\n  | {link} | Bài một | draft |"}
        for name, table in forms.items():
            with self.subTest(table=name):
                self.write_readme(f"# Kho\n\n{table}\n")
                self.assertProblem("repeats a lesson status")

    def test_a_table_shown_inside_a_code_block_is_not_a_readme_table(self) -> None:
        self.write_readme(README + "\n```\n| ID | Ghi chú |\n|---|---|\n| sd-01-001 | draft |\n```\n")
        self.assertEqual([], self.problems())

    def test_a_readme_link_with_a_fragment_a_query_or_encoding_still_links_the_lesson(self) -> None:
        forms = {"fragment": "lessons/sd-01-001/lesson.md#vi-du", "query": "lessons/sd-01-001/lesson.md?x=1",
                 "encoded": "lessons/sd%2D01%2D001/lesson.md"}
        for name, target in forms.items():
            with self.subTest(link=name):
                self.write_readme(f"# Kho\n\n[bài một]({target})\n")
                self.assertEqual([], self.problems())

    def test_a_status_word_inside_a_longer_cell_is_a_status(self) -> None:
        for cell in ["Bài đã draft xong", "Trạng thái: draft", "draft!", "(done)", "status=review", "[draft]",
                     "đang REVIEW", "Done/Draft", "_draft_", "\\_done\\_", "draft, done", "tiếng draft"]:
            with self.subTest(cell=cell):
                row = f"| [sd-01-001](lessons/sd-01-001/lesson.md) | {cell} |\n"
                self.write_readme("# Kho\n\n| ID | Bài |\n|---|---|\n" + row)
                self.assertProblem("repeats a lesson status")

    def test_a_word_that_merely_contains_a_status_word_is_not_a_status(self) -> None:
        for cell in ["undraft", "redraft", "undone", "overdone", "review2", "2review", "reviewer", "reviewed",
                     "drafting", "abandoned", "preview", "Bài về kế hoạch", "done2"]:
            with self.subTest(cell=cell):
                row = f"| [sd-01-001](lessons/sd-01-001/lesson.md) | {cell} |\n"
                self.write_readme("# Kho\n\n| ID | Bài |\n|---|---|\n" + row)
                self.assertEqual([], self.problems())

    def test_a_status_word_outside_a_table_is_not_checked(self) -> None:
        self.write_readme(README + "\nMọi bài ở trạng thái draft, review hoặc done được ghi trong metadata.\n")
        self.assertEqual([], self.problems())

    def test_a_readme_path_in_a_comment_a_code_block_or_prose_is_not_a_link(self) -> None:
        path = "lessons/sd-01-001/lesson.md"
        forms = {"html comment": f"<!-- [x]({path}) -->", "code block": f"```\n[x]({path})\n```",
                 "plain prose": f"Xem {path} nhé."}
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_readme(f"# Kho\n\n{form}\n")
                self.assertProblem("does not link lessons/sd-01-001/lesson.md")

    def test_a_readme_link_as_an_html_anchor_or_a_reference_or_with_dot_slash_counts(self) -> None:
        path = "lessons/sd-01-001/lesson.md"
        forms = {"html anchor": f'<a href="{path}">bài một</a>', "reference": f"[bài một][s]\n\n[s]: {path}",
                 "dot slash": f"[bài một](./{path})"}
        for name, form in forms.items():
            with self.subTest(form=name):
                self.write_readme(f"# Kho\n\n{form}\n")
                self.assertEqual([], self.problems())


class OtherPageRuleTests(StoreCase):
    """PROGRESS.md and MIGRATION.md are prose pages: no figures, allowed HTML only, links that land."""

    def test_the_pages_may_be_absent_or_plain(self) -> None:
        self.assertEqual([], self.problems())
        for name in check.STORE_PAGES[1:]:
            with self.subTest(page=name):
                (self.store / name).write_text(
                    "# Tiến độ\n\n| Bài | Trạng thái |\n|---|---|\n| sd-01-009 | draft |\n\nXem [README](README.md) và "
                    "[repo cũ](https://github.com/o/r/tree/abc).\n\nsd-01-002 trước sd-01-001.\n", encoding="utf-8")
                self.assertEqual([], self.problems())

    def test_each_page_is_held_to_the_shared_page_rules(self) -> None:
        for name in check.STORE_PAGES[1:]:
            cases = {
                "an embedded image": ("![x](figure.svg)", f"{name}: embeds the image"),
                "an html image": ('<img src="https://example.com/a.png" alt="x">', f"{name}: embeds the image"),
                "raw html": ("<div>x</div>", f"{name}: uses <div>"),
                "a broken relative link": ("[x](missing.md)", f"{name}: relative link 'missing.md' does not resolve"),
                "a link out of the store": ("[x](../../README.md)", f"{name}: relative link '../../README.md' does not resolve"),
                "the source image host": ("assets.bytebytego.com", f"{name}: contains assets.bytebytego.com"),
                "the source image host in capitals": ("ASSETS.BYTEBYTEGO.COM", f"{name}: contains assets.bytebytego.com"),
            }
            for case, (text, fragment) in cases.items():
                with self.subTest(page=name, case=case):
                    (self.store / name).write_text(f"# Trang\n\n{text}\n", encoding="utf-8")
                    self.assertProblem(fragment)

    def test_a_page_that_is_not_utf8_is_reported_not_raised(self) -> None:
        (self.store / "PROGRESS.md").write_bytes(b"# x\n\xff\xfe")
        self.assertProblem("PROGRESS.md: is not valid UTF-8 text")

    def test_a_page_that_is_a_directory_or_a_link_is_reported(self) -> None:
        (self.store / "MIGRATION.md").mkdir()
        self.assertProblem("MIGRATION.md: is not a file")
        if hasattr(os, "symlink"):
            (self.store / "MIGRATION.md").rmdir()
            real = self.root / "migration.real"
            real.write_text("# x\n", encoding="utf-8")
            (self.store / "MIGRATION.md").symlink_to(real)
            self.assertProblem("MIGRATION.md: is a symbolic link")


class ProgressRuleTests(StoreCase):
    """progress.json coordinates the work; what it says about the store must agree with the store."""

    auto_progress = False

    def setUp(self) -> None:
        super().setUp()
        self.sync_progress()

    def three_lessons(self) -> None:
        self.write_source_map({lesson_id: (title, SNAPSHOT) for lesson_id, title in TITLES.items()})
        for lesson_id in TITLES:
            self.write_lesson(lesson_id)
        self.write_readme("# Kho\n\n" + "".join(f"[{i}](lessons/{i}/lesson.md)\n\n" for i in TITLES))

    def test_a_progress_record_that_matches_the_store_is_fine(self) -> None:
        self.assertEqual([], self.problems())
        self.three_lessons()
        self.sync_progress()
        self.assertEqual([], self.problems())

    def test_a_missing_or_unreadable_progress_file_is_reported(self) -> None:
        path = self.store / "progress.json"
        path.unlink()
        self.assertProblem("progress.json: is missing")
        for name, content in {"invalid json": b"{", "not utf-8": b"\xff\xfe{}", "empty": b""}.items():
            with self.subTest(file=name):
                path.write_bytes(content)
                self.assertProblem("progress.json: cannot be read")
        path.write_text('{"language": "vi", "language": "vi"}', encoding="utf-8")
        self.assertProblem("duplicate key")
        for content in ("[]", '"x"', "null", "3"):
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                self.assertProblem("progress.json: is not a JSON object")
        path.write_text("{", encoding="utf-8")
        self.assertEqual(["progress.json"], sorted({line.split(":")[0] for line in self.problems()
                                                    if line.startswith("progress.json")}))
        self.assertFalse(any("is not a JSON object" in line for line in self.problems()), self.problems())

    def test_the_required_keys_and_the_language_are_checked(self) -> None:
        for key in sorted(check.PROGRESS_REQUIRED):
            with self.subTest(missing=key):
                self.sync_progress()
                data = json.loads((self.store / "progress.json").read_text(encoding="utf-8"))
                del data[key]
                (self.store / "progress.json").write_text(json.dumps(data), encoding="utf-8")
                self.assertProblem(f"progress.json: is missing {key}")
        self.sync_progress(language="en")
        self.assertProblem("progress.json: language must be 'vi'")

    def test_the_totals_are_the_source_maps(self) -> None:
        for key, wrong in {"total_occurrences": [0, 2, "1", True, None], "total_source_documents": [0, 2, "1", True, None]}.items():
            for value in wrong:
                with self.subTest(key=key, value=value):
                    self.sync_progress(**{key: value})
                    self.assertProblem(f"progress.json: {key} is {value!r}, but the source map has 1")
        self.three_lessons()
        self.sync_progress()
        self.assertEqual([], self.problems())
        self.sync_progress(total_occurrences=1)
        self.assertProblem("total_occurrences is 1, but the source map has 3")

    def test_the_source_documents_are_counted_by_distinct_path(self) -> None:
        other = f"https://github.com/ByteByteGoHq/system-design-101/blob/{COMMIT}/data/guides/two.md"
        self.source_map.write_text(json.dumps({**PIN, "categories": [{"id": "sd-01", "lessons": [
            source_entry(), source_entry("sd-01-002", "Bài hai", other, source_path="data/guides/two.md")]}]}), encoding="utf-8")
        self.sync_progress()
        self.assertEqual(2, json.loads((self.store / "progress.json").read_text(encoding="utf-8"))["total_source_documents"])
        self.assertEqual([], [line for line in self.problems() if "total_" in line])
        self.sync_progress(total_source_documents=1)
        self.assertProblem("total_source_documents is 1, but the source map has 2")

    def test_written_ids_are_the_lessons_on_disk_in_source_order(self) -> None:
        self.three_lessons()
        for name, value in {"one missing": ["sd-01-001", "sd-01-002"], "none": [], "out of order": ["sd-01-002", "sd-01-001", "sd-01-003"],
                            "an id with no lesson": ["sd-01-001", "sd-01-002", "sd-01-003", "sd-01-004"],
                            "a repeat": ["sd-01-001", "sd-01-001", "sd-01-002", "sd-01-003"], "not a list": "sd-01-001",
                            "null": None}.items():
            with self.subTest(written_ids=name):
                self.sync_progress(written_ids=value)
                self.assertProblem("progress.json: written_ids is")

    def test_written_ids_follow_the_source_map_order_not_the_alphabet(self) -> None:
        self.write_source_map({"sd-01-002": ("Bài hai", SNAPSHOT), "sd-01-001": ("Bài một", SNAPSHOT)})
        self.write_lesson("sd-01-002")
        self.write_readme("# Kho\n\n[2](lessons/sd-01-002/lesson.md)\n\n[1](lessons/sd-01-001/lesson.md)\n")
        self.sync_progress()
        self.assertEqual(["sd-01-002", "sd-01-001"],
                         json.loads((self.store / "progress.json").read_text(encoding="utf-8"))["written_ids"])
        self.assertEqual([], self.problems())
        self.sync_progress(written_ids=["sd-01-001", "sd-01-002"])
        self.assertProblem("progress.json: written_ids is")

    def test_a_lesson_written_without_updating_progress_is_reported(self) -> None:
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT), "sd-01-002": ("Bài hai", SNAPSHOT)})
        self.write_lesson("sd-01-002")
        self.write_readme(README + "| [sd-01-002](lessons/sd-01-002/lesson.md) | Bài hai |\n")
        found = self.problems()
        self.assertTrue(any("written_ids is ['sd-01-001'], but the lessons on disk are ['sd-01-001', 'sd-01-002']" in line
                            for line in found), found)
        self.assertTrue(any("total_occurrences is 1, but the source map has 2" in line for line in found), found)

    def test_next_id_is_the_first_source_map_id_not_yet_written(self) -> None:
        self.write_source_map({lesson_id: (title, SNAPSHOT) for lesson_id, title in TITLES.items()})
        self.sync_progress()
        self.assertEqual("sd-01-002", json.loads((self.store / "progress.json").read_text(encoding="utf-8"))["next_id"])
        self.assertEqual([], self.problems())
        for value in ("sd-01-003", "sd-01-001", None, "", 2, ["sd-01-002"], "sd-99-999"):
            with self.subTest(next_id=value):
                self.sync_progress(next_id=value)
                self.assertProblem(f"progress.json: next_id is {value!r}, but the first source-map id not yet written is 'sd-01-002'")
        self.three_lessons()
        self.sync_progress()
        self.assertIsNone(json.loads((self.store / "progress.json").read_text(encoding="utf-8"))["next_id"])
        self.assertEqual([], self.problems())
        self.sync_progress(next_id="sd-01-004")
        self.assertProblem("next_id is 'sd-01-004', but the first source-map id not yet written is None")

    def test_the_id_lists_name_written_lessons(self) -> None:
        for key in check.PROGRESS_ID_LISTS:
            with self.subTest(key=key, value="a lesson that is written"):
                self.sync_progress(**{key: ["sd-01-001"]})
                self.assertEqual([], self.problems())
            for value in (["sd-01-002"], ["sd-99-999"], [5], [["sd-01-001"]], [None]):
                with self.subTest(key=key, value=value):
                    self.sync_progress(**{key: value})
                    self.assertTrue([line for line in self.problems() if line.startswith(f"progress.json: {key} names ")])
            for value in ("sd-01-001", None, 5, {}, "sd-01-002"):
                with self.subTest(key=key, value=value):
                    self.sync_progress(**{key: value})
                    self.assertTrue([line for line in self.problems() if line == f"progress.json: {key} must be a list of lesson ids"])

    def test_the_orchestration_fields_are_free(self) -> None:
        self.sync_progress(active_pr=40, active_branch="x", integration_review_pending=True, adopted_main_sha="y",
                           updated_on="2026-10-13")
        self.assertEqual([], self.problems())
        self.sync_progress(updated_on="2026-02-30")
        self.assertProblem("progress.json: updated_on must be a YYYY-MM-DD date")
        for value in (None, 20261013, "13/10/2026", "2026-10-13T00:00:00Z"):
            with self.subTest(updated_on=value):
                self.sync_progress(updated_on=value)
                self.assertProblem("updated_on must be a YYYY-MM-DD date")

    def test_without_a_readable_source_map_only_the_file_itself_is_checked(self) -> None:
        self.write_source_map({"sd-01-001": ("Bài một", SNAPSHOT), "sd-01-002": ("Bài hai", SNAPSHOT)})
        self.sync_progress()
        self.assertEqual("sd-01-002", json.loads((self.store / "progress.json").read_text(encoding="utf-8"))["next_id"])
        self.source_map.write_text("{", encoding="utf-8")
        found = self.problems()
        self.assertFalse(any("total_" in line or "next_id" in line for line in found), found)


class CommandLineTests(StoreCase):
    def run_main(self) -> tuple[int, str]:
        self.sync_progress()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check.main(["--store", str(self.store), "--source-map", str(self.source_map)])
        return code, out.getvalue()

    def test_a_clean_store_exits_zero_and_says_how_many_lessons(self) -> None:
        code, output = self.run_main()
        self.assertEqual(0, code)
        self.assertIn("1 lesson(s), 0 problem(s)", output)

    def test_a_pointer_file_is_not_counted_as_a_lesson(self) -> None:
        (self.store / "lessons" / "sd-01-001.md").write_text("[x](sd-01-001/lesson.md)\n", encoding="utf-8")
        code, output = self.run_main()
        self.assertEqual(0, code)
        self.assertIn("1 lesson(s), 0 problem(s)", output)

    def test_a_broken_store_exits_one_and_prints_the_problem(self) -> None:
        self.write_metadata("sd-01-001", self.meta(content_status="approved"))
        code, output = self.run_main()
        self.assertEqual(1, code)
        self.assertIn("metadata/sd-01-001.json: content_status", output)

    def test_a_store_that_does_not_exist_is_reported_not_raised(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check.main(["--store", str(self.root / "nowhere"), "--source-map", str(self.source_map)])
        self.assertEqual(1, code)
        self.assertIn("README.md: is missing", out.getvalue())
        self.assertIn("0 lesson(s)", out.getvalue())


class DeclaredDependencyTests(unittest.TestCase):
    """A fresh checkout installs requirements.txt (README), so the checker may import nothing that is not there."""

    def test_every_third_party_module_the_checker_imports_is_in_requirements_txt(self) -> None:
        tree = ast.parse(Path(check.__file__).read_text(encoding="utf-8"))
        modules = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        modules |= {node.module.split(".")[0] for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module}
        third_party = {name for name in modules if name not in sys.stdlib_module_names}
        self.assertTrue({"yaml", "markdown_it"} <= third_party, third_party)
        lines = (check.ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        declared = {re.split(r"[<>=!~\[ ;]", line.strip(), maxsplit=1)[0].lower().replace("_", "-")
                    for line in lines if line.strip() and not line.startswith(("#", "-"))}
        distributions = importlib.metadata.packages_distributions()
        for module in sorted(third_party):
            names = {name.lower().replace("_", "-") for name in distributions.get(module, [])}
            with self.subTest(module=module):
                self.assertTrue(names & declared, f"{module} ({sorted(names)}) is not in requirements.txt")


if __name__ == "__main__":
    unittest.main()
