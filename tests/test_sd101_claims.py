"""scripts/sd101_claims.py: the claim registry, with real git repositories standing in for the sessions' containers."""

from __future__ import annotations

import contextlib
import datetime
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import sd101_claims as claims

COMMIT = "b" * 40
LESSONS = [("sd-01-001", "One"), ("sd-01-002", "Two"), ("sd-01-003", "Three"), ("sd-01-004", "Four"),
           ("sd-01-005", "Five"), ("sd-02-001", "Six")]
T0 = datetime.datetime(2026, 10, 15, 8, 0, 0, tzinfo=datetime.timezone.utc)
REGISTRY = "store/claims.jsonl"


def source_map() -> dict:
    """Two groups; sd-01-005 and sd-02-001 share one source file, as the real map's four pairs do."""
    partners = {"sd-01-005": ["sd-02-001"], "sd-02-001": ["sd-01-005"]}
    groups = {}
    for lesson_id, title in LESSONS:
        groups.setdefault(lesson_id[:5], []).append({"id": lesson_id, "title_source": title,
                                                     **({"same_source_as": partners[lesson_id]} if lesson_id in partners else {})})
    return {"source_repository": "ByteByteGoHq/system-design-101", "source_commit_sha": COMMIT,
            "categories": [{"id": group, "title_source": f"Group {group}", "lessons": lessons}
                           for group, lessons in groups.items()]}


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


class Sessions(unittest.TestCase):
    """A bare origin with main holding a fresh registry, and one clone per simulated session."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@example.com", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("CLAUDE_CODE_REMOTE_SESSION_ID", None)  # restored by the patcher above
        self.clock = T0
        for target, replacement in (("utcnow", lambda: self.clock), ("time", mock.Mock())):
            patch = mock.patch.object(claims, target, replacement) if target != "time" else mock.patch.object(claims.time, "sleep")
            patch.start()
            self.addCleanup(patch.stop)
        self.source_map = self.tmp / "source-map.json"
        self.source_map.write_text(json.dumps(source_map()), encoding="utf-8")
        self.origin = self.tmp / "origin.git"
        git(self.tmp, "init", "--quiet", "--bare", "-b", "main", str(self.origin))
        seed = self.clone("seed", branch=None)
        self.run_in(seed, "--offline", "--owner", "seed", "sync")
        (seed / "README.md").write_text("x\n", encoding="utf-8")
        git(seed, "add", "-A")
        git(seed, "commit", "--quiet", "-m", "seed")
        git(seed, "push", "--quiet", "origin", "main")

    def clone(self, name: str, branch: str | None = None) -> Path:
        path = self.tmp / name
        git(self.tmp, "clone", "--quiet", str(self.origin), str(path))
        git(path, "checkout", "--quiet", "-B", "main") if branch is None else git(path, "checkout", "--quiet", "-b", branch)
        return path

    def session(self, name: str) -> Path:
        return self.clone(name, branch=f"claude/{name}")

    def run_in(self, clone: Path, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = claims.main(["--store", str(clone / "store"), "--source-map", str(self.source_map), *args])
        return code, out.getvalue(), err.getvalue()

    def entry(self, clone: Path, lesson_id: str) -> dict:
        _, lessons, _ = claims.parse((clone / REGISTRY).read_text(encoding="utf-8"))
        return lessons[lesson_id]

    def at(self, hours: float = 0, seconds: float = 0) -> None:
        self.clock = T0 + datetime.timedelta(hours=hours, seconds=seconds)

    def write_lesson(self, clone: Path, lesson_id: str) -> None:
        (clone / "store" / "lessons" / lesson_id).mkdir(parents=True, exist_ok=True)
        (clone / "store" / "lessons" / lesson_id / "lesson.md").write_text("# x\n", encoding="utf-8")
        (clone / "store" / "lessons" / lesson_id / "lesson.yaml").write_text("id: x\n", encoding="utf-8")
        for path in (f"metadata/{lesson_id}.json", f"diagrams/{lesson_id}-main.svg"):
            (clone / "store" / path).parent.mkdir(parents=True, exist_ok=True)
            (clone / "store" / path).write_text("x\n", encoding="utf-8")


class ClaimTests(Sessions):
    def test_a_published_claim_keeps_every_other_session_off_the_lesson(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--publish")[0])
        before = (b / REGISTRY).read_text(encoding="utf-8")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("claimed by claude/a", err)
        self.assertEqual(before, (b / REGISTRY).read_text(encoding="utf-8"), "a refused claim writes nothing")

    def test_sessions_that_claim_different_lessons_do_not_collide(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.assertEqual(0, self.run_in(a, "claim", "--next", "2", "--publish")[0])
        self.assertEqual(0, self.run_in(b, "claim", "--next", "2", "--publish")[0])
        self.assertEqual("claude/a", self.entry(a, "sd-01-001")["owner"])
        self.assertEqual("claude/b", self.entry(b, "sd-01-003")["owner"])
        self.assertEqual("todo", self.entry(b, "sd-01-005")["status"])

    def test_next_adds_to_the_lessons_named_and_never_repeats_them(self) -> None:
        a = self.session("a")
        code, out, err = self.run_in(a, "claim", "sd-01-001", "sd-01-001", "--next", "2")
        self.assertEqual(0, code, err)
        self.assertIn("claimed sd-01-001, sd-01-002, sd-01-003 as claude/a", out)
        self.assertEqual(["sd-01-001", "sd-01-002", "sd-01-003"],
                         [lid for lid, _ in LESSONS if self.entry(a, lid)["status"] == "doing"])

    def test_a_claim_is_all_or_nothing(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        code, _, err = self.run_in(b, "claim", "sd-01-002", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("sd-01-001", err)
        self.assertEqual("todo", self.entry(b, "sd-01-002")["status"])

    def test_the_earlier_claim_wins_even_when_it_is_pushed_second(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(a, "claim", "sd-01-001")
        self.at(seconds=5)
        self.run_in(b, "claim", "sd-01-001")
        code, _, err = self.run_in(b, "claim", "sd-01-001", "--publish")  # b pushes first, and finds itself alone
        self.assertEqual(0, code, err)
        git(a, "add", REGISTRY)
        git(a, "commit", "--quiet", "-m", "claim")
        git(a, "push", "--quiet", "-u", "origin", "claude/a")
        self.assertEqual(0, self.run_in(a, "verify")[0], "a claimed first, so a keeps it")
        code, _, err = self.run_in(b, "verify")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/a", err)

    def test_a_copy_of_a_claim_inherited_by_another_branch_is_not_a_claim(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        c = self.clone("c", branch=None)
        git(c, "checkout", "--quiet", "-b", "claude/c", "origin/claude/a")
        git(c, "push", "--quiet", "-u", "origin", "claude/c")
        self.run_in(a, "release", "sd-01-001", "--publish")
        code, _, err = self.run_in(b, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, code, err)

    def test_a_lesson_written_on_another_branch_cannot_be_claimed(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.write_lesson(a, "sd-01-001")
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001", "--pr", "7")[0])
        git(a, "add", "-A")
        git(a, "commit", "--quiet", "-m", "lesson")
        git(a, "push", "--quiet", "origin", "claude/a")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("already written by claude/a", err)
        self.assertEqual({"id": "sd-01-001", "status": "written", "title": "One", "owner": "claude/a",
                          "done_at": "2026-10-15T08:00:00Z", "pr": 7}, self.entry(a, "sd-01-001"))

    def test_a_claim_that_reached_main_counts(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        git(a, "push", "--quiet", "origin", "claude/a:main")
        self.assertEqual(1, self.run_in(b, "claim", "sd-01-001")[0])

    def test_a_lesson_sharing_its_source_is_refused_unless_allowed(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-005", "--publish")
        code, _, err = self.run_in(b, "claim", "sd-02-001")
        self.assertEqual(1, code)
        self.assertIn("shares its source file with sd-01-005", err)
        self.assertEqual(0, self.run_in(b, "claim", "sd-02-001", "--allow-same-source")[0])

    def test_two_halves_of_a_shared_source_claimed_before_either_was_visible_are_decided_by_verify(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(a, "--offline", "claim", "sd-01-005")
        self.at(seconds=3)
        self.run_in(b, "--offline", "claim", "sd-02-001")  # neither has seen the other's claim
        for clone, name in ((a, "claude/a"), (b, "claude/b")):
            git(clone, "add", REGISTRY)
            git(clone, "commit", "--quiet", "-m", "claim")
            git(clone, "push", "--quiet", "-u", "origin", name)
        self.assertEqual(0, self.run_in(a, "verify")[0], "a claimed first")
        for command in ("verify", "touch"):
            with self.subTest(command):
                code, _, err = self.run_in(b, command)
                self.assertEqual(1, code)
                self.assertIn("shares its source file with sd-01-005, which claude/a holds", err)
        self.write_lesson(b, "sd-02-001")
        self.assertEqual(1, self.run_in(b, "finish", "sd-02-001")[0])

    def test_an_expired_claim_revived_by_a_local_renewal_does_not_beat_a_partner_taken_fairly(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-005", "--publish")
        self.at(hours=50)
        self.assertEqual(0, self.run_in(a, "touch")[0], "renewed in a's copy only")
        self.at(hours=80)  # a's published claim has expired; its local heartbeat has not
        code, _, err = self.run_in(b, "claim", "sd-02-001", "--publish")
        self.assertEqual(0, code, err)  # valid against the public state: the other half is only expired there
        before = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a")
        self.at(hours=81)
        code, _, err = self.run_in(a, "touch", "--publish")
        self.assertEqual(1, code)
        self.assertIn("shares its source file with sd-02-001, which claude/b holds", err)
        self.assertEqual(before, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"),
                         "the renewal was not pushed")
        self.assertEqual(0, self.run_in(b, "verify")[0])

    def test_touching_one_claim_does_not_push_another_claim_unjudged(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-005", "sd-01-001", "--publish")
        self.at(hours=50)
        self.assertEqual(0, self.run_in(a, "touch")[0], "both claims renewed in a's copy only")
        self.at(hours=80)  # the published heartbeats have expired; the local ones have not
        self.assertEqual(0, self.run_in(b, "claim", "sd-02-001", "--publish")[0])  # valid against the public state
        before = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a")
        self.at(hours=81)
        code, _, err = self.run_in(a, "touch", "sd-01-001", "--publish")  # names only the unrelated claim
        self.assertEqual(1, code)
        self.assertIn("nothing was pushed: sd-01-005 shares its source file with sd-02-001, which claude/b holds", err)
        self.assertIn("release sd-01-005", err)
        self.assertEqual(before, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"))
        self.assertEqual(0, self.run_in(b, "verify")[0])
        self.assertEqual(0, self.run_in(a, "release", "sd-01-005", "--publish")[0], "the lost claim can be given back")

    def test_a_claim_of_the_same_owner_is_ended_by_its_own_written_record(self) -> None:
        a1 = self.session("a")
        self.run_in(a1, "claim", "sd-01-001", "--publish")
        a2 = self.clone("a2", branch=None)  # a second container on the same branch, still holding the claim
        git(a2, "checkout", "--quiet", "-b", "claude/a", "origin/claude/a")
        self.write_lesson(a1, "sd-01-001")
        self.assertEqual(0, self.run_in(a1, "finish", "sd-01-001")[0])
        git(a1, "add", "-A")
        git(a1, "commit", "--quiet", "-m", "the lesson")
        git(a1, "push", "--quiet", "origin", "claude/a")
        pushed = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a")
        code, _, err = self.run_in(a2, "verify")
        self.assertEqual(1, code)
        self.assertIn("already written by claude/a (origin/claude/a)", err)
        code, _, err = self.run_in(a2, "touch", "--publish")
        self.assertEqual(1, code)
        self.assertEqual(pushed, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"), "nothing was pushed")

    def test_a_finished_lesson_is_not_pushed_ahead_of_its_files(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.write_lesson(a, "sd-01-001")
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001")[0])  # written in the registry, files not committed
        pushed = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a")
        for command in (("claim", "sd-01-002", "--publish"), ("touch", "--publish"), ("release", "sd-01-002", "--publish")):
            with self.subTest(command[0]):
                code, _, err = self.run_in(a, *command)
                self.assertEqual(1, code, err)
                self.assertIn("nothing was pushed: sd-01-001 is marked written but the lesson files are not committed", err)
        self.assertEqual(pushed, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"))
        git(a, "add", "-A")
        git(a, "commit", "--quiet", "-m", "the lesson with its registry record")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-002", "--publish")[0], "committed together: it may go up")

    def test_a_finished_lesson_changed_after_its_commit_is_not_pushed(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "sd-01-002", "sd-01-003", "sd-01-004", "--publish")  # sd-01-004 stays in progress
        files = ("lessons/{id}/lesson.md", "metadata/{id}.json", "diagrams/{id}-main.svg")
        for lesson_id, changed in zip(("sd-01-001", "sd-01-002", "sd-01-003"), files):
            with self.subTest(changed):
                for path in (*files, "lessons/{id}/lesson.yaml"):
                    target = a / "store" / path.format(id=lesson_id)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("a draft\n", encoding="utf-8")
                git(a, "add", "-A")
                git(a, "commit", "--quiet", "-m", "a draft")
                (a / "store" / changed.format(id=lesson_id)).write_text("the final text\n", encoding="utf-8")
                self.assertEqual(0, self.run_in(a, "finish", lesson_id)[0])
                pushed = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a")
                code, _, err = self.run_in(a, "touch", "--publish")
                self.assertEqual(1, code, err)
                self.assertIn(f"nothing was pushed: {lesson_id} is marked written but the lesson files are not committed", err)
                self.assertEqual(pushed, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"))
                git(a, "add", "-A")
                git(a, "commit", "--quiet", "-m", "the final lesson with its registry record")
                self.assertEqual(0, self.run_in(a, "touch", "--publish")[0], "committed together: it may go up")

    def test_a_finished_lesson_without_its_metadata_and_figure_is_not_pushed(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        (a / "store" / "lessons" / "sd-01-001").mkdir(parents=True)
        (a / "store" / "lessons" / "sd-01-001" / "lesson.md").write_text("# x\n", encoding="utf-8")  # nothing else was written
        git(a, "add", "-A")
        git(a, "commit", "--quiet", "-m", "the lesson text only")
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001")[0])
        code, _, err = self.run_in(a, "claim", "sd-01-002", "--publish")  # clean tree, but metadata and figure are absent
        self.assertEqual(1, code, err)
        self.assertIn("sd-01-001 is marked written but the lesson files are not committed", err)

    def test_a_written_record_committed_by_itself_is_still_judged_before_it_goes_up(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        (a / "store" / "lessons" / "sd-01-001").mkdir(parents=True)
        (a / "store" / "lessons" / "sd-01-001" / "lesson.md").write_text("# x\n", encoding="utf-8")
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001")[0])
        git(a, "add", REGISTRY)
        git(a, "commit", "--quiet", "-m", "the registry alone, by accident")
        pushed = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a")
        code, _, err = self.run_in(a, "claim", "sd-01-002", "--publish")
        self.assertEqual(1, code, err)
        self.assertIn("sd-01-001 is marked written but the lesson files are not committed", err)
        self.assertEqual(pushed, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"))

    def test_a_hidden_claim_with_a_fresh_local_heartbeat_loses_to_a_visible_replacement(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=50)
        self.assertEqual(0, self.run_in(a, "touch")[0], "renewed in a's copy only")
        git(self.tmp, "--git-dir", str(self.origin), "branch", "-D", "claude/a")  # nothing of a is visible any more
        self.at(hours=51)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--publish")[0], "free as far as anyone can see")
        code, _, err = self.run_in(a, "touch", "--publish")
        self.assertEqual(1, code, err)
        self.assertIn("lost to claude/b", err)
        self.assertEqual("", git(self.tmp, "--git-dir", str(self.origin), "branch", "--list", "claude/a"), "a was not recreated")

    def test_deleting_a_file_of_a_pushed_lesson_is_not_pushed_with_its_written_record(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.write_lesson(a, "sd-01-001")
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001")[0])
        git(a, "add", "-A")
        git(a, "commit", "--quiet", "-m", "the lesson")
        git(a, "push", "--quiet", "origin", "claude/a")
        git(a, "rm", "--quiet", "store/metadata/sd-01-001.json")
        git(a, "commit", "--quiet", "-m", "the metadata was removed, cleanly committed")
        pushed = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a")
        code, _, err = self.run_in(a, "claim", "sd-01-002", "--publish")
        self.assertEqual(1, code, err)
        self.assertIn("sd-01-001 is marked written but the lesson files are not committed", err)
        self.assertEqual(pushed, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"))

    def test_renaming_a_file_of_a_pushed_lesson_is_not_pushed_with_its_written_record(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.write_lesson(a, "sd-01-001")
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001")[0])
        git(a, "add", "-A")
        git(a, "commit", "--quiet", "-m", "the lesson")
        git(a, "push", "--quiet", "origin", "claude/a")
        git(a, "mv", "store/lessons/sd-01-001/lesson.md", "store/lessons/sd-01-001/lesson-old.md")  # git reports R100, not D
        git(a, "commit", "--quiet", "-m", "lesson.md was renamed, cleanly committed")
        pushed = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a")
        code, _, err = self.run_in(a, "claim", "sd-01-002", "--publish")
        self.assertEqual(1, code, err)
        self.assertIn("sd-01-001 is marked written but the lesson files are not committed", err)
        self.assertEqual(pushed, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"))

    def test_a_finished_lesson_that_git_ignores_is_not_pushed(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        (a / ".gitignore").write_text("store/lessons/\nstore/metadata/\nstore/diagrams/\n", encoding="utf-8")  # git status shows nothing
        git(a, "add", ".gitignore")
        git(a, "commit", "--quiet", "-m", "ignore the lessons")
        self.write_lesson(a, "sd-01-001")
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001")[0])
        code, _, err = self.run_in(a, "claim", "sd-01-002", "--publish")
        self.assertEqual(1, code, err)
        self.assertIn("sd-01-001 is marked written but the lesson files are not committed", err)

    def test_reworking_a_lesson_that_was_already_pushed_does_not_block_a_claim(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.write_lesson(a, "sd-01-001")
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001")[0])
        git(a, "add", "-A")
        git(a, "commit", "--quiet", "-m", "the lesson")
        git(a, "push", "--quiet", "origin", "claude/a")
        (a / "store" / "lessons" / "sd-01-001" / "lesson.md").write_text("# a rework in progress\n", encoding="utf-8")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-002", "--publish")[0], "its record was committed with its files")

    def test_a_shared_source_taken_on_purpose_is_not_a_conflict(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-005", "--publish")
        self.assertEqual(0, self.run_in(b, "claim", "sd-02-001", "--allow-same-source", "--publish")[0])
        self.assertIs(True, self.entry(b, "sd-02-001")["shared_source"])
        self.assertNotIn("shared_source", self.entry(a, "sd-01-005"))
        self.assertEqual(0, self.run_in(b, "verify")[0])
        self.assertEqual(0, self.run_in(a, "verify")[0], "a is not told to give up what b took knowingly")

    def test_one_session_may_hold_both_halves_of_a_shared_source(self) -> None:
        a = self.session("a")
        self.assertEqual(0, self.run_in(a, "claim", "sd-02-001", "--publish")[0])
        self.at(seconds=10)
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-005", "--publish")[0])
        self.assertEqual(0, self.run_in(a, "verify")[0], "its own earlier claim on the other half is not a rival")

    def test_claiming_again_with_allow_same_source_is_the_way_to_keep_a_half_on_purpose(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(a, "--offline", "claim", "sd-01-005")
        self.at(seconds=3)
        self.run_in(b, "--offline", "claim", "sd-02-001")  # neither saw the other
        for clone, name in ((a, "claude/a"), (b, "claude/b")):
            git(clone, "add", REGISTRY)
            git(clone, "commit", "--quiet", "-m", "claim")
            git(clone, "push", "--quiet", "-u", "origin", name)
        self.assertEqual(1, self.run_in(b, "verify")[0], "b lost the pair")
        self.assertEqual(0, self.run_in(b, "claim", "sd-02-001", "--allow-same-source", "--publish")[0])
        self.assertIs(True, self.entry(b, "sd-02-001")["shared_source"])
        self.assertEqual(0, self.run_in(b, "verify")[0], "kept on purpose and published")

    def test_a_shared_source_override_that_is_not_published_does_not_count_as_held(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(a, "--offline", "claim", "sd-01-005")
        self.at(seconds=3)
        self.run_in(b, "--offline", "claim", "sd-02-001")
        for clone, name in ((a, "claude/a"), (b, "claude/b")):
            git(clone, "add", REGISTRY)
            git(clone, "commit", "--quiet", "-m", "claim")
            git(clone, "push", "--quiet", "-u", "origin", name)
        self.run_in(b, "--offline", "claim", "sd-02-001", "--allow-same-source")  # recorded here only
        code, _, err = self.run_in(b, "verify")
        self.assertEqual(1, code)
        self.assertIn("your claim is not on origin/claude/b", err)
        self.assertEqual(0, self.run_in(b, "touch", "--publish")[0])
        self.assertEqual(0, self.run_in(b, "verify")[0])

    def test_next_skips_what_is_taken_or_written(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "sd-01-002", "--publish")
        code, out, _ = self.run_in(b, "next", "-n", "2")
        self.assertEqual((0, "sd-01-003\nsd-01-004\n"), (code, out))
        _, out, _ = self.run_in(b, "next", "--group", "sd-02")
        self.assertEqual("sd-02-001\n", out)

    def test_the_session_is_recorded_when_there_is_one(self) -> None:
        a = self.session("a")
        self.run_in(a, "--session", "cse_123", "claim", "sd-01-001")
        self.assertEqual("cse_123", self.entry(a, "sd-01-001")["session"])
        self.assertNotIn("session", self.entry(a, "sd-01-002"))

    def test_claiming_again_renews_instead_of_duplicating(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001")
        self.at(hours=2)
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001")[0])
        entry = self.entry(a, "sd-01-001")
        self.assertEqual(("2026-10-15T08:00:00Z", "2026-10-15T10:00:00Z"), (entry["claimed_at"], entry["heartbeat_at"]))

    def test_an_id_outside_the_source_map_is_an_error(self) -> None:
        a = self.session("a")
        for bad in ("sd-99-999", "banana"):
            with self.subTest(bad):
                self.assertEqual(2, self.run_in(a, "claim", bad)[0])


class LeaseTests(Sessions):
    def test_a_stale_claim_blocks_nobody_until_it_is_taken_on_purpose(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=73)
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("--take-stale", err)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")[0])
        self.assertEqual(["claude/a"], self.entry(b, "sd-01-001")["taken_from"])

    def test_a_session_that_wakes_up_cannot_win_back_a_lesson_that_was_taken(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=73)
        self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")
        self.at(hours=74)
        code, _, err = self.run_in(a, "touch")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/b", err)
        self.assertEqual("2026-10-15T08:00:00Z", self.entry(a, "sd-01-001")["heartbeat_at"], "a lost claim is not renewed")

    def test_a_takeover_beats_a_claim_whose_renewal_was_never_pushed(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=71)
        self.run_in(a, "touch")  # renewed in a's copy only: the remote still shows the claim of hour 0
        self.at(hours=73)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")[0])
        self.at(hours=74)
        git(a, "commit", "--quiet", "-am", "the renewal, pushed by hand")
        git(a, "push", "--quiet", "origin", "claude/a")  # now a's published copy is live again, and older than b's claim
        code, _, err = self.run_in(a, "verify")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/b", err)

    def test_a_lesson_taken_over_twice_is_still_won_against_the_first_owner(self) -> None:
        a, b, c = self.session("a"), self.session("b"), self.session("c")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=73)
        self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")
        git(self.origin, "branch", "-D", "claude/a")  # a's container is gone and its branch was cleaned up
        self.at(hours=146)
        self.assertEqual(0, self.run_in(c, "claim", "sd-01-001", "--take-stale", "--publish")[0])
        self.assertEqual(["claude/b", "claude/a"], self.entry(c, "sd-01-001")["taken_from"])
        self.at(hours=147)
        code, _, err = self.run_in(a, "touch", "--publish")  # a wakes up and pushes its old claim again
        self.assertEqual(1, code)
        self.assertIn("lost to claude/c", err)

    def test_an_expired_claim_that_comes_back_loses_to_a_live_one_even_though_it_is_older(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        git(self.origin, "branch", "-D", "claude/a")  # the branch is gone, so b cannot see a's claim or take it over
        self.at(hours=80)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--publish")[0])
        self.assertNotIn("taken_from", self.entry(b, "sd-01-001"))
        self.at(hours=81)
        code, _, err = self.run_in(a, "touch", "--publish")  # a wakes up with a claim 81 hours old
        self.assertEqual(1, code)
        self.assertIn("lost to claude/b", err)
        self.assertEqual(0, self.run_in(b, "verify")[0])

    def test_a_session_that_takes_back_a_lesson_it_once_held_starts_a_new_claim_that_wins(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=73)
        self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")  # b took it from a
        self.at(hours=140)
        self.assertEqual(0, self.run_in(b, "touch")[0], "renewed in b's copy only")
        self.at(hours=150)  # b's published heartbeat (hour 73) has expired; its local one has not
        code, _, err = self.run_in(a, "claim", "sd-01-001", "--take-stale", "--publish")
        self.assertEqual(0, code, err)
        taken = self.entry(a, "sd-01-001")
        self.assertEqual((["claude/b"], "2026-10-21T14:00:00Z"), (taken["taken_from"], taken["claimed_at"]))
        b_code, _, b_err = self.run_in(b, "touch", "--publish")  # judged before anything is pushed
        self.assertEqual(1, b_code)
        self.assertIn("lost to claude/a", b_err)
        # b's fresh copy reaches the remote by hand, so both public records are live and each names the other as taken from
        git(b, "add", REGISTRY)
        git(b, "commit", "--quiet", "-m", "b pushes its copy by hand")
        git(b, "push", "--quiet", "origin", "claude/b")
        self.assertEqual(0, self.run_in(a, "verify")[0], "a's takeover is the later one and stands")
        self.assertEqual(1, self.run_in(b, "verify")[0])

    def test_touching_keeps_a_claim_alive(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=50)
        self.assertEqual(0, self.run_in(a, "touch", "--publish")[0])
        self.at(hours=100)
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("claimed by claude/a since", err)
        self.assertNotIn("--take-stale", err, "50 hours after the heartbeat is inside the lease")


class RemoteTests(Sessions):
    def test_an_unreadable_remote_stops_the_claim_unless_offline_is_asked_for(self) -> None:
        a = self.session("a")
        before = (a / REGISTRY).read_text(encoding="utf-8")
        code, _, err = self.run_in(a, "--remote", "nowhere", "claim", "sd-01-001")
        self.assertEqual(2, code)
        self.assertIn("nothing was decided", err)
        self.assertEqual(before, (a / REGISTRY).read_text(encoding="utf-8"))
        self.assertEqual(0, self.run_in(a, "--offline", "claim", "sd-01-001")[0])

    def test_publish_commits_only_the_registry_and_leaves_other_staged_work_alone(self) -> None:
        a = self.session("a")
        (a / "other.txt").write_text("keep me\n", encoding="utf-8")
        git(a, "add", "other.txt")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--publish")[0])
        self.assertEqual(REGISTRY, git(a, "show", "--name-only", "--format=", "HEAD"))
        self.assertEqual("A  other.txt", git(a, "status", "--short"))
        self.assertEqual(git(a, "rev-parse", "HEAD"), git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"))

    def test_a_claim_committed_by_hand_but_never_pushed_is_pushed_by_publish(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001")
        git(a, "add", REGISTRY)
        git(a, "commit", "--quiet", "-m", "claim by hand")  # the push was forgotten
        self.assertEqual(0, self.run_in(a, "touch", "--publish")[0], "same second: nothing new to commit")
        self.assertEqual(git(a, "rev-parse", "HEAD"), git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "claude/a"))

    def test_a_branch_with_a_directory_where_the_registry_should_be_does_not_shift_the_others(self) -> None:
        odd = self.clone("odd", branch="aaa")  # sorts before every claude/* branch
        git(odd, "rm", "-q", REGISTRY)
        (odd / REGISTRY).mkdir(parents=True)
        (odd / REGISTRY / "f.txt").write_text("a tree, not a file\n", encoding="utf-8")
        git(odd, "add", "-A")
        git(odd, "commit", "--quiet", "-m", "odd")
        git(odd, "push", "--quiet", "-u", "origin", "aaa")
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("claimed by claude/a since 2026-10-15T08:00:00Z (origin/claude/a)", err)

    def test_nothing_is_published_from_main(self) -> None:
        main = self.clone("m", branch=None)
        self.assertEqual(2, self.run_in(main, "claim", "sd-01-001")[0])
        self.assertEqual("todo", self.entry(main, "sd-01-001")["status"])
        code, _, err = self.run_in(main, "--owner", "someone", "claim", "sd-01-001", "--publish")
        self.assertEqual(2, code)
        self.assertIn("never pushes main, the default branch", err)

    def test_a_branch_whose_registry_cannot_be_parsed_stops_the_decision(self) -> None:
        broken = self.clone("broken", branch="claude/broken")
        (broken / REGISTRY).write_text((broken / REGISTRY).read_text(encoding="utf-8") + "<<<<<<< ours\n", encoding="utf-8")
        git(broken, "commit", "--quiet", "-am", "conflict markers committed by mistake")
        git(broken, "push", "--quiet", "-u", "origin", "claude/broken")
        a = self.session("a")
        self.assertEqual(2, self.run_in(a, "claim", "sd-01-001")[0])
        self.assertEqual("todo", self.entry(a, "sd-01-001")["status"])
        self.assertEqual(0, self.run_in(a, "--ignore-unreadable", "claim", "sd-01-002")[0], "the flag goes on without it")
        self.write_lesson(a, "sd-01-002")
        for command in (("claim", "sd-01-001"), ("verify",), ("next",), ("touch",), ("finish", "sd-01-002")):
            with self.subTest(command[0]):
                code, _, err = self.run_in(a, *command)
                self.assertEqual(2, code)
                self.assertIn("origin/claude/broken", err)
                self.assertIn("nothing was decided", err)
        self.assertEqual("doing", self.entry(a, "sd-01-002")["status"])
        code, _, err = self.run_in(a, "status")
        self.assertEqual(0, code, "reporting is not deciding")
        self.assertIn("could not be parsed", err)

    def test_a_branch_whose_registry_parses_but_holds_an_invalid_record_stops_the_decision(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        original = git(a, "rev-parse", "HEAD")
        for name, damage in (("status typo", ('"status": "doing"', '"status": "doign"')),
                             ("no owner", ('"owner": "claude/a", ', "")),
                             ("bad heartbeat", ('"heartbeat_at": "2026-10-15T08:00:00Z"', '"heartbeat_at": "soon"'))):
            with self.subTest(name):
                text = (a / REGISTRY).read_text(encoding="utf-8")
                self.assertIn(damage[0], text)
                (a / REGISTRY).write_text(text.replace(*damage), encoding="utf-8")
                git(a, "commit", "--quiet", "-am", "damage")
                git(a, "push", "--quiet", "origin", "claude/a")
                b = self.session(f"b-{name.replace(' ', '-')}")
                code, _, err = self.run_in(b, "claim", "sd-01-001")
                self.assertEqual(2, code)
                self.assertIn("origin/claude/a", err)
                self.assertEqual("todo", self.entry(b, "sd-01-001")["status"])
                git(a, "reset", "--quiet", "--hard", original)  # each damage is judged on its own
                git(a, "push", "--quiet", "-f", "origin", "claude/a")

    def test_a_truncated_registry_on_a_branch_stops_the_decision(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "sd-01-002", "--publish")
        original = git(a, "rev-parse", "HEAD")
        lines = (a / REGISTRY).read_text(encoding="utf-8").split("\n\n")
        (a / REGISTRY).write_text("\n\n".join(lines[:3]).rstrip("\n") + "\n", encoding="utf-8")  # header + one lesson survive
        git(a, "commit", "--quiet", "-am", "truncated by mistake")
        git(a, "push", "--quiet", "origin", "claude/a")
        b = self.session("b")
        code, _, err = self.run_in(b, "claim", "sd-01-002")
        self.assertEqual(2, code)
        self.assertIn("origin/claude/a (lacks", err)
        git(a, "reset", "--quiet", "--hard", original)
        git(a, "push", "--quiet", "-f", "origin", "claude/a")
        self.assertEqual(1, self.run_in(b, "claim", "sd-01-002")[0], "intact again: the claim is seen and respected")

    def test_a_branch_whose_registry_is_not_valid_utf8_stops_the_decision(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        original = git(a, "rev-parse", "HEAD")
        data = (a / REGISTRY).read_bytes()
        self.assertIn(b'"owner": "claude/a"', data)
        (a / REGISTRY).write_bytes(data.replace(b'"owner": "claude/a"', b'"owner": "claude/\xffa"'))  # one bad byte in a name
        git(a, "commit", "--quiet", "-am", "a byte that is not UTF-8")
        git(a, "push", "--quiet", "origin", "claude/a")
        b = self.session("b")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(2, code)
        self.assertIn("origin/claude/a (not valid UTF-8)", err)
        self.assertEqual("todo", self.entry(b, "sd-01-001")["status"])
        code, _, err = self.run_in(b, "status")
        self.assertEqual(0, code, "reporting is not deciding")
        self.assertIn("not valid UTF-8", err)
        git(a, "reset", "--quiet", "--hard", original)
        git(a, "push", "--quiet", "-f", "origin", "claude/a")
        self.assertEqual(1, self.run_in(b, "claim", "sd-01-001")[0], "intact again: the claim is seen and respected")

    def test_a_local_registry_that_is_not_valid_utf8_is_reported_not_raised(self) -> None:
        a = self.session("a")
        (a / REGISTRY).write_bytes((a / REGISTRY).read_bytes() + b"\xff\n")
        code, _, err = self.run_in(a, "claim", "sd-01-001")
        self.assertEqual(2, code)
        self.assertIn("cannot read", err)

    def test_a_renamed_default_branch_is_found_by_asking_the_remote(self) -> None:
        b = self.session("b")  # cloned while the default branch was still called main: its origin/HEAD says so
        seed = self.tmp / "seed"
        git(seed, "checkout", "--quiet", "-b", "trunk")
        header, lessons, _ = claims.parse((seed / REGISTRY).read_text(encoding="utf-8"))
        lessons["sd-01-001"] = {"id": "sd-01-001", "status": "written", "title": "One", "owner": "claude/x",
                                "done_at": "2026-10-15T07:00:00Z"}
        (seed / REGISTRY).write_text(claims.render(header, lessons), encoding="utf-8")
        git(seed, "commit", "--quiet", "-am", "a lesson was written and merged")
        git(seed, "push", "--quiet", "origin", "trunk")
        git(self.tmp, "--git-dir", str(self.origin), "symbolic-ref", "HEAD", "refs/heads/trunk")
        git(self.tmp, "--git-dir", str(self.origin), "branch", "-D", "main")  # the default branch was renamed
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code, err)
        self.assertIn("already written by claude/x (origin/trunk)", err)

    def test_nothing_is_published_from_a_renamed_default_branch(self) -> None:
        seed = self.tmp / "seed"
        git(seed, "checkout", "--quiet", "-b", "trunk")
        git(seed, "push", "--quiet", "origin", "trunk")
        git(self.tmp, "--git-dir", str(self.origin), "symbolic-ref", "HEAD", "refs/heads/trunk")
        git(self.tmp, "--git-dir", str(self.origin), "branch", "-D", "main")  # the default branch is now called trunk
        trunk = self.tmp / "t"
        git(self.tmp, "clone", "--quiet", str(self.origin), str(trunk))  # checked out on trunk
        before = git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "trunk")
        code, _, err = self.run_in(trunk, "claim", "sd-01-001")
        self.assertEqual(2, code)
        self.assertIn("claims belong to a work branch", err)
        code, _, err = self.run_in(trunk, "--owner", "someone", "claim", "sd-01-001", "--publish")
        self.assertEqual(2, code)
        self.assertIn("never pushes trunk, the default branch", err)
        self.assertEqual("todo", self.entry(trunk, "sd-01-001")["status"], "nothing was written")
        self.assertEqual(before, git(self.tmp, "--git-dir", str(self.origin), "rev-parse", "trunk"))
        self.assertEqual(0, self.run_in(self.session("a"), "claim", "sd-01-001", "--publish")[0], "a work branch still may")

    def test_a_remote_registry_with_a_header_of_another_pin_stops_the_decision(self) -> None:
        odd = self.clone("odd", branch="claude/odd")
        header, lessons, _ = claims.parse((odd / REGISTRY).read_text(encoding="utf-8"))
        header["source_commit_sha"] = "0" * 40
        (odd / REGISTRY).write_text(claims.render(header, lessons), encoding="utf-8")
        git(odd, "commit", "--quiet", "-am", "a registry pinned to another source commit")
        git(odd, "push", "--quiet", "-u", "origin", "claude/odd")
        a = self.session("a")
        code, _, err = self.run_in(a, "claim", "sd-01-001")
        self.assertEqual(2, code)
        self.assertIn("origin/claude/odd", err)
        self.assertIn("nothing was decided", err)

    def test_a_default_branch_without_a_registry_stops_the_decision(self) -> None:
        b = self.session("b")  # holds a registry of its own, which must not be trusted instead of the default branch's
        seed = self.tmp / "seed"
        git(seed, "rm", "--quiet", REGISTRY)
        git(seed, "commit", "--quiet", "-m", "the registry was deleted from main")
        git(seed, "push", "--quiet", "origin", "main")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(2, code)
        self.assertIn("origin/main (the default branch has no claims.jsonl)", err)
        self.assertEqual("todo", self.entry(b, "sd-01-001")["status"])
        self.assertEqual(0, self.run_in(b, "status")[0], "reporting is not deciding")
        self.assertEqual(0, self.run_in(b, "--ignore-unreadable", "claim", "sd-01-001")[0])

    def test_publish_with_an_owner_that_is_not_the_branch_is_refused_before_anything_is_written(self) -> None:
        a = self.session("a")
        before = (a / REGISTRY).read_text(encoding="utf-8")
        for command in (("claim", "sd-01-001"), ("touch",), ("release", "sd-01-001")):
            with self.subTest(command[0]):
                code, _, err = self.run_in(a, "--owner", "someone-else", *command, "--publish")
                self.assertEqual(2, code)
                self.assertIn("claims are owned by someone-else", err)
        self.assertEqual(before, (a / REGISTRY).read_text(encoding="utf-8"))
        self.assertNotIn("claude/a", git(self.tmp, "--git-dir", str(self.origin), "branch", "--list", "claude/a"))

    def test_status_does_not_count_a_claim_the_branch_only_inherited(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        c = self.clone("c", branch=None)
        git(c, "checkout", "--quiet", "-b", "claude/c", "origin/claude/a")  # c's copy shows a's claim
        self.run_in(a, "release", "sd-01-001", "--publish")                 # which a has since given back
        code, out, _ = self.run_in(c, "status")
        self.assertEqual(0, code)
        self.assertIn("doing 0", out)
        self.assertIn("Next free: sd-01-001", out)
        self.assertEqual("sd-01-001\n", self.run_in(c, "next")[1])

    def test_status_shows_what_other_sessions_hold(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        code, out, _ = self.run_in(b, "status")
        self.assertEqual(0, code)
        self.assertIn("doing 1", out)
        self.assertIn("sd-01-001  claude/a", out)
        self.assertIn("Next free: sd-01-002", out)


class SyncTests(Sessions):
    def test_sync_follows_a_repinned_and_retitled_source_map_and_keeps_every_claim(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001")
        data = json.loads(self.source_map.read_text(encoding="utf-8"))
        data["source_commit_sha"] = "c" * 40
        data["categories"][0]["lessons"][1]["title_source"] = "Two, renamed"
        self.source_map.write_text(json.dumps(data), encoding="utf-8")
        code, out, _ = self.run_in(a, "--offline", "sync")
        self.assertEqual(0, code)
        self.assertIn("1 retitled", out)
        header, lessons, problems = claims.parse((a / REGISTRY).read_text(encoding="utf-8"))
        self.assertEqual(([], "c" * 40, "Two, renamed", "doing"),
                         (problems, header["source_commit_sha"], lessons["sd-01-002"]["title"], lessons["sd-01-001"]["status"]))
        self.assertEqual("claude/a", lessons["sd-01-001"]["owner"])


class VerifyTests(Sessions):
    def test_a_claim_that_exists_only_in_the_working_tree_is_not_held(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001")  # the documented push was forgotten
        for command in (("verify",), ("touch",)):
            with self.subTest(command[0]):
                code, _, err = self.run_in(a, *command)
                self.assertEqual(1, code)
                self.assertIn("your claim is not on origin/claude/a with a live heartbeat yet", err)
                self.assertNotIn("Stop work", err, "the remedy is to push, not to release")
        self.assertEqual("2026-10-15T08:00:00Z", self.entry(a, "sd-01-001")["heartbeat_at"])
        self.write_lesson(a, "sd-01-001")
        self.assertEqual(1, self.run_in(a, "finish", "sd-01-001")[0])
        self.assertEqual("doing", self.entry(a, "sd-01-001")["status"])
        self.assertEqual(0, self.run_in(a, "--offline", "verify")[0], "offline there is no remote to ask")
        git(a, "add", REGISTRY)
        git(a, "commit", "--quiet", "-m", "claim")
        git(a, "push", "--quiet", "-u", "origin", "claude/a")
        self.assertEqual(0, self.run_in(a, "verify")[0], "pushed: the other sessions can see it")

    def test_a_heartbeat_renewed_only_here_does_not_keep_a_published_claim_alive(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=50)
        self.assertEqual(0, self.run_in(a, "touch")[0], "the claim is published, and live at that time")
        self.at(hours=80)  # the published heartbeat (hour 0) has expired; the local one (hour 50) has not
        code, _, err = self.run_in(a, "verify")
        self.assertEqual(1, code)
        self.assertIn("with a live heartbeat yet", err)
        self.write_lesson(a, "sd-01-001")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual((1, True), (code, "--take-stale" in err), "to b the published claim is stale, so it is open to a takeover")
        self.assertEqual(1, self.run_in(a, "finish", "sd-01-001")[0])
        self.assertEqual(0, self.run_in(a, "touch", "--publish")[0], "touch publishes the renewal first")
        self.assertEqual(0, self.run_in(a, "verify")[0], "now the published heartbeat is live")

    def test_touch_renews_an_expired_claim_that_nobody_took(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=100)
        self.assertEqual(0, self.run_in(a, "touch", "--publish")[0])
        self.assertEqual("2026-10-19T12:00:00Z", self.entry(a, "sd-01-001")["heartbeat_at"])
        self.assertEqual(0, self.run_in(a, "verify")[0])

    def test_touch_publish_pushes_a_forgotten_claim_before_judging_it(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001")
        self.assertEqual(0, self.run_in(a, "touch", "--publish")[0])
        self.assertEqual(1, self.run_in(b, "claim", "sd-01-001")[0])

    def test_ids_named_to_verify_or_touch_must_all_be_claims_of_the_caller(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        for command in ("verify", "touch"):
            with self.subTest(command):
                code, _, err = self.run_in(a, command, "sd-01-002")
                self.assertEqual((1, True), (code, "sd-01-002: not claimed by claude/a" in err))
                code, _, err = self.run_in(a, command, "sd-01-001", "sd-01-002")
                self.assertEqual(1, code, "one foreign id fails the whole command")
                self.assertEqual(2, self.run_in(a, command, "banana")[0])
                self.assertEqual(0, self.run_in(a, command, "sd-01-001")[0])


class SyncDropTests(Sessions):
    def test_sync_drops_what_the_source_map_no_longer_lists_and_says_what_it_dropped(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-003")
        data = json.loads(self.source_map.read_text(encoding="utf-8"))
        data["categories"][0]["lessons"] = [e for e in data["categories"][0]["lessons"] if e["id"] != "sd-01-003"]
        data["categories"][1]["lessons"] = []  # sd-02-001 (todo) is gone too
        self.source_map.write_text(json.dumps(data), encoding="utf-8")
        code, out, err = self.run_in(a, "--offline", "sync")
        self.assertEqual(0, code)
        self.assertIn("2 dropped", out)
        self.assertIn("sd-01-003 (doing)", err)
        self.assertNotIn("sd-02-001", err, "a todo record carries no work worth a warning")
        text = (a / REGISTRY).read_text(encoding="utf-8")
        expected = [(lid, title) for lid, title in LESSONS if lid not in ("sd-01-003", "sd-02-001")]
        self.assertEqual([], claims.registry_problems(text, expected, "b" * 40, set()))


class LocalFileTests(Sessions):
    def test_a_truncated_local_registry_is_refused_before_anything_is_written_or_pushed(self) -> None:
        a = self.session("a")
        lines = (a / REGISTRY).read_text(encoding="utf-8").split("\n\n")
        truncated = "\n\n".join(lines[:2]).rstrip("\n") + "\n"  # the header and one lesson: valid, but not the roster
        (a / REGISTRY).write_text(truncated, encoding="utf-8")
        for command in (("claim", "sd-01-005", "--publish"), ("claim", "--next", "1"), ("verify",), ("touch",), ("next",),
                        ("status",), ("release", "sd-01-001"), ("finish", "sd-01-001")):
            with self.subTest(" ".join(command)):
                code, _, err = self.run_in(a, *command)
                self.assertEqual(2, code)
                self.assertIn("lacks 5 source-map lesson(s), e.g. sd-01-002; sd101_claims.py sync repairs", err)
        self.assertEqual(truncated, (a / REGISTRY).read_text(encoding="utf-8"))
        self.assertEqual("", git(self.tmp, "--git-dir", str(self.origin), "branch", "--list", "claude/a"), "nothing was pushed")
        self.assertEqual(0, self.run_in(a, "--offline", "sync")[0], "sync is how a lagging registry is repaired")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-005")[0])

    def test_a_local_registry_for_another_source_pin_is_refused_until_sync(self) -> None:
        a = self.session("a")
        text = (a / REGISTRY).read_text(encoding="utf-8")
        (a / REGISTRY).write_text(text.replace(COMMIT, "c" * 40), encoding="utf-8")
        code, _, err = self.run_in(a, "claim", "sd-01-001")
        self.assertEqual(2, code)
        self.assertIn("source_commit_sha", err)
        self.assertEqual(0, self.run_in(a, "--offline", "sync")[0])
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001")[0])


class MergeTests(Sessions):
    def test_sessions_that_claim_neighbouring_lessons_merge_without_a_conflict(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "sd-01-002", "--publish")[0])
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-003", "sd-01-004", "--publish")[0])
        git(a, "push", "--quiet", "origin", "claude/a:main")  # a's pull request is merged
        git(b, "fetch", "--quiet", "origin")
        merged = subprocess.run(["git", "merge", "--no-edit", "origin/main"], cwd=b, capture_output=True, text=True, check=False)
        self.assertEqual(0, merged.returncode, merged.stdout + merged.stderr)
        owners = {lesson_id: self.entry(b, lesson_id).get("owner") for lesson_id, _ in LESSONS[:5]}
        self.assertEqual({"sd-01-001": "claude/a", "sd-01-002": "claude/a", "sd-01-003": "claude/b", "sd-01-004": "claude/b",
                          "sd-01-005": None}, owners)

    def test_two_sessions_that_claimed_the_same_lesson_do_conflict(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(a, "--offline", "claim", "sd-01-002")
        self.at(seconds=3)
        self.run_in(b, "--offline", "claim", "sd-01-002")
        for clone, name in ((a, "claude/a"), (b, "claude/b")):
            git(clone, "add", REGISTRY)
            git(clone, "commit", "--quiet", "-m", "claim")
            git(clone, "push", "--quiet", "-u", "origin", name)
        git(a, "push", "--quiet", "origin", "claude/a:main")
        git(b, "fetch", "--quiet", "origin")
        merged = subprocess.run(["git", "merge", "--no-edit", "origin/main"], cwd=b, capture_output=True, text=True, check=False)
        self.assertNotEqual(0, merged.returncode)
        subprocess.run(["git", "merge", "--abort"], cwd=b, check=False)


class FinishAndReleaseTests(Sessions):
    def test_finish_needs_a_claim_of_yours_and_the_lesson_file(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(1, self.run_in(a, "finish", "sd-01-001")[0], "no lesson.md yet")
        self.write_lesson(b, "sd-01-001")
        self.assertEqual(1, self.run_in(b, "finish", "sd-01-001")[0], "claimed by a, not b")
        self.assertEqual("doing", self.entry(a, "sd-01-001")["status"])

    def test_finish_refuses_a_pull_request_number_that_is_not_one(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.write_lesson(a, "sd-01-001")
        before = (a / REGISTRY).read_text(encoding="utf-8")
        for bad in ("-1", "0", "x", "1.5"):
            with self.subTest(bad), self.assertRaises(SystemExit) as raised:
                self.run_in(a, "finish", "sd-01-001", "--pr", bad)
            self.assertEqual(2, raised.exception.code)
        self.assertEqual(before, (a / REGISTRY).read_text(encoding="utf-8"))
        self.assertEqual(0, self.run_in(a, "finish", "sd-01-001", "--pr", "12")[0])
        self.assertEqual(12, self.entry(a, "sd-01-001")["pr"])

    def test_finish_refuses_a_claim_that_was_lost(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=73)
        self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")
        self.write_lesson(a, "sd-01-001")
        code, _, err = self.run_in(a, "finish", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/b", err)

    def test_release_gives_the_lesson_back_but_not_with_a_draft_on_disk(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "sd-01-002", "--publish")
        self.write_lesson(a, "sd-01-002")
        self.assertEqual(1, self.run_in(a, "release", "sd-01-002")[0])
        self.assertEqual(0, self.run_in(a, "release", "sd-01-001", "--publish")[0])
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001")[0])

    def test_a_session_cannot_release_the_claim_of_another(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        git(b, "fetch", "--quiet", "origin")
        git(b, "merge", "--quiet", "origin/claude/a")  # b's copy now shows a's claim
        self.assertEqual(1, self.run_in(b, "release", "sd-01-001")[0])
        self.assertEqual("claude/a", self.entry(b, "sd-01-001")["owner"])


class FormatTests(unittest.TestCase):
    EXPECTED = [("sd-01-001", "One"), ("sd-01-002", "Two")]

    def text(self, **changes: object) -> str:
        header = {"schema_version": 1, "lease_hours": 72, "source_repository": "r/r", "source_commit_sha": COMMIT}
        lessons = {"sd-01-001": {"id": "sd-01-001", "status": "written", "title": "One"},
                   "sd-01-002": {"id": "sd-01-002", "status": "doing", "title": "Two", "owner": "claude/a",
                                 "claimed_at": "2026-10-15T08:00:00Z", "heartbeat_at": "2026-10-15T09:00:00Z"}}
        lessons["sd-01-002"].update(changes)
        return claims.render(header, lessons)

    @staticmethod
    def records(text: str) -> list[str]:
        return [line for line in text.split("\n") if line]

    @staticmethod
    def join(lines: list[str]) -> str:
        return "\n\n".join(lines) + "\n"

    def problems(self, text: str, on_disk: set[str] | None = None) -> list[str]:
        return claims.registry_problems(text, self.EXPECTED, COMMIT, {"sd-01-001"} if on_disk is None else on_disk,
                                        pin_repository="r/r")

    def test_a_correct_registry_has_no_problem_and_survives_a_round_trip(self) -> None:
        text = self.text()
        self.assertEqual([], self.problems(text))
        header, lessons, problems = claims.parse(text)
        self.assertEqual((text, []), (claims.render(header, lessons), problems))

    def test_each_rule_reports_its_own_problem(self) -> None:
        cases = {
            "title": (self.text(title="Zwei"), "title is 'Zwei'"),
            "owner missing": (self.text().replace('"owner": "claude/a", ', ""), "owner is required"),
            "bad time": (self.text(claimed_at="yesterday"), "claimed_at must be a UTC time"),
            "heartbeat early": (self.text(heartbeat_at="2026-10-15T07:00:00Z"), "heartbeat_at is before claimed_at"),
            "field of another status": (self.text(done_at="2026-10-15T09:00:00Z"), "done_at is not allowed"),
            "status": (self.text(status="done"), "status must be one of"),
            "taken_from": (self.text(taken_from="claude/a"), "taken_from must be a list"),
            "repository": (self.text().replace('"source_repository": "r/r"', '"source_repository": "x/y"'),
                           "source_repository is 'x/y'"),
            "repository missing": (self.text().replace('"source_repository": "r/r", ', ""), "source_repository is None"),
            "shared_source": (self.text(shared_source=False), "shared_source must be true"),
            "pr": (self.text().replace('"title": "One"', '"title": "One", "pr": 0'), "pr must be a pull request number"),
            "pin": (self.text().replace(COMMIT, "c" * 40), "source_commit_sha"),
            "lease": (self.text().replace('"lease_hours": 72', '"lease_hours": 0'), "lease_hours must be"),
            "missing lesson": (self.join(self.records(self.text())[:2]), "lacks 1 source-map lesson"),
            "extra lesson": (self.text() + '{"id": "sd-09-009", "status": "todo", "title": "x"}\n', "lists 1 id(s)"),
            "twice": (self.text() + self.records(self.text())[1] + "\n", "appears twice"),
            "not json": (self.text() + "{oops\n", "is not a JSON object"),
            "order": (self.join([self.records(self.text())[0], *reversed(self.records(self.text())[1:3])]), "out of source-map order"),
            "canonical": (self.text().replace('{"id": "sd-01-001", "status": "written", "title": "One"}',
                                              '{"title": "One", "id": "sd-01-001", "status": "written"}'), "canonical form"),
        }
        for name, (text, fragment) in cases.items():
            with self.subTest(name):
                self.assertTrue(any(fragment in line for line in self.problems(text)), f"{fragment!r} not in {self.problems(text)}")

    def test_records_are_set_apart_by_a_blank_line_and_either_layout_is_read(self) -> None:
        text = self.text()
        self.assertEqual(3, len(self.records(text)))
        self.assertEqual(2 * len(self.records(text)) - 1, len(text.rstrip("\n").split("\n")), "a blank line between records")
        _, packed, problems = claims.parse("\n".join(self.records(text)) + "\n")
        self.assertEqual(([], ["sd-01-001", "sd-01-002"]), (problems, list(packed)))
        self.assertTrue(any("canonical form" in line for line in self.problems("\n".join(self.records(text)) + "\n")))

    def test_the_registry_must_agree_with_the_lessons_on_disk(self) -> None:
        self.assertTrue(any("is written, but lessons/sd-01-001/ does not exist" in p for p in self.problems(self.text(), set())))
        todo = self.text().replace('"status": "doing"', '"status": "todo"')
        todo = "\n".join(line if "sd-01-002" not in line else '{"id": "sd-01-002", "status": "todo", "title": "Two"}'
                         for line in todo.split("\n"))
        self.assertTrue(any("exists, but the registry says todo" in p for p in self.problems(todo, {"sd-01-001", "sd-01-002"})))
        self.assertEqual([], self.problems(self.text(), {"sd-01-001", "sd-01-002"}), "a draft on disk may be doing")

    def test_the_real_registry_lists_every_source_map_lesson(self) -> None:
        source = claims.load_source(claims.DEFAULT_SOURCE_MAP)
        text = (claims.DEFAULT_STORE / claims.REGISTRY_NAME).read_text(encoding="utf-8")
        on_disk = {path.name for path in (claims.DEFAULT_STORE / "lessons").iterdir() if path.is_dir()}
        self.assertEqual(404, len(source.lessons))
        self.assertEqual([], claims.registry_problems(text, list(source.lessons), source.commit_sha, on_disk))


if __name__ == "__main__":
    unittest.main()
