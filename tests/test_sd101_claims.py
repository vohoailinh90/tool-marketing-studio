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
        code, _, err = self.run_in(a, "verify")  # a's own copy is fresh, and older than b's claim
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
        self.assertIn("never pushes main", err)

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
        return claims.registry_problems(text, self.EXPECTED, COMMIT, {"sd-01-001"} if on_disk is None else on_disk)

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
