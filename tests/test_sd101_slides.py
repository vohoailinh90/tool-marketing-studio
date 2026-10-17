"""scripts/sd101_slides.py: the slide-deck claims, with real git repositories standing in for the sessions' containers."""

from __future__ import annotations

import contextlib
import datetime
import io
import os
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

import yaml

from scripts import sd101_slides as slides

LESSONS = ["sd-01-001", "sd-01-002", "sd-01-003", "sd-01-004", "sd-02-001"]
T0 = datetime.datetime(2026, 10, 17, 8, 0, 0, tzinfo=datetime.timezone.utc)
CANVAS = "cvs_5ZDSW8ECGA8AZBX5S8S7FF58M2"
URL = "https://moda.app/canvas/bf6e7887-320a-42be-be97-28c9def2a282?source=agent"


def git(cwd: Path, *args: str) -> str:
    import subprocess

    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def png(path: Path, width: int = 1920, height: int = 1080) -> None:
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    chunk = struct.pack(">I", len(header)) + b"IHDR" + header + struct.pack(">I", zlib.crc32(b"IHDR" + header))
    path.write_bytes(slides.PNG_SIGNATURE + chunk)


class Sessions(unittest.TestCase):
    """A bare origin whose main holds five written lessons, and one clone per simulated session."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@example.com", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.clock = T0
        for patch in (mock.patch.object(slides, "now", lambda: self.clock), mock.patch.object(slides.time, "sleep")):
            patch.start()
            self.addCleanup(patch.stop)
        self.origin = self.tmp / "origin.git"
        git(self.tmp, "init", "--quiet", "--bare", "-b", "main", str(self.origin))
        seed = self.tmp / "seed"
        git(self.tmp, "clone", "--quiet", str(self.origin), str(seed))
        git(seed, "checkout", "--quiet", "-B", "main")
        for lesson_id in LESSONS:
            folder = seed / "store" / "lessons" / lesson_id
            folder.mkdir(parents=True)
            (folder / "lesson.md").write_text("# x\n", encoding="utf-8")
        git(seed, "add", "-A")
        git(seed, "commit", "--quiet", "-m", "seed")
        git(seed, "push", "--quiet", "origin", "main")
        self.seed = seed

    def session(self, name: str) -> Path:
        path = self.tmp / name
        git(self.tmp, "clone", "--quiet", str(self.origin), str(path))
        git(path, "checkout", "--quiet", "-b", f"claude/{name}")
        return path

    def run_in(self, clone: Path, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = slides.main(["--store", str(clone / "store"), *args])
        return code, out.getvalue(), err.getvalue()

    def record(self, clone: Path, lesson_id: str) -> dict | None:
        path = clone / "store" / "lessons" / lesson_id / "slides" / "deck.yaml"
        return yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None

    def at(self, hours: float = 0, seconds: float = 0) -> None:
        self.clock = T0 + datetime.timedelta(hours=hours, seconds=seconds)

    def finish(self, clone: Path, lesson_id: str, *extra: str) -> tuple[int, str, str]:
        return self.run_in(clone, "finish", lesson_id, "--canvas", CANVAS, "--url", URL, "--slides", "10", *extra)


class ClaimTests(Sessions):
    def test_a_published_claim_keeps_every_other_session_off_the_lesson(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--publish")[0])
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("claimed by claude/a", err)
        self.assertIsNone(self.record(b, "sd-01-001"), "a refused claim writes nothing")

    def test_sessions_that_claim_different_lessons_do_not_collide(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.assertEqual(0, self.run_in(a, "claim", "--next", "2", "--publish")[0])
        self.assertEqual(0, self.run_in(b, "claim", "--next", "2", "--publish")[0])
        self.assertEqual(["claude/a", "claude/a", "claude/b", "claude/b", None],
                         [(self.record(a if i < 2 else b, lid) or {}).get("owner") for i, lid in enumerate(LESSONS)])

    def test_a_claim_is_all_or_nothing(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        code, _, err = self.run_in(b, "claim", "sd-01-002", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("sd-01-001", err)
        self.assertIsNone(self.record(b, "sd-01-002"))

    def test_the_earlier_claim_wins_even_when_it_is_pushed_second(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(a, "claim", "sd-01-001")
        self.at(seconds=5)
        self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--publish")[0], "b pushes first and finds itself alone")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.run_in(a, "verify")[0], "a claimed first, so a keeps it")
        code, _, err = self.run_in(b, "verify")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/a", err)

    def test_a_claim_that_was_never_pushed_does_not_verify(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001")
        code, _, err = self.run_in(a, "verify")
        self.assertEqual(1, code)
        self.assertIn("not on origin/claude/a", err)

    def test_a_copy_of_a_claim_inherited_by_another_branch_is_not_a_claim(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        git(a, "push", "--quiet", "origin", "claude/a:refs/heads/claude/c")  # a branch cut from a's, still carrying the record
        self.run_in(a, "release", "sd-01-001", "--publish")
        code, _, err = self.run_in(b, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, code, err)

    def test_a_lesson_that_is_not_written_cannot_be_claimed(self) -> None:
        a = self.session("a")
        code, _, err = self.run_in(a, "claim", "sd-09-009")
        self.assertEqual(1, code)
        self.assertIn("not a written lesson", err)

    def test_the_default_branch_is_never_pushed(self) -> None:
        code, _, err = self.run_in(self.seed, "claim", "sd-01-001", "--publish")
        self.assertEqual(2, code)
        self.assertIn("default branch", err)

    def test_an_unreadable_remote_stops_the_claim_unless_offline_is_asked_for(self) -> None:
        a = self.session("a")
        git(a, "remote", "set-url", "origin", str(self.tmp / "missing.git"))
        self.assertEqual(2, self.run_in(a, "claim", "sd-01-001")[0])
        self.assertEqual(0, self.run_in(a, "--offline", "claim", "sd-01-001")[0])

    def test_next_skips_lessons_that_are_taken_or_done_and_stays_in_its_group(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.run_in(a, "release", "sd-01-001", "--publish")
        self.run_in(a, "claim", "sd-01-002", "--publish")
        code, out, _ = self.run_in(b, "next", "--count", "2")
        self.assertEqual((0, "sd-01-001 sd-01-003\n"), (code, out))
        code, out, _ = self.run_in(b, "next", "--count", "5", "--group", "sd-02")
        self.assertEqual((0, "sd-02-001\n"), (code, out))


class LeaseTests(Sessions):
    def test_a_stale_claim_blocks_nobody_until_it_is_taken_on_purpose(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=slides.LEASE_HOURS - 1)
        self.assertEqual(1, self.run_in(b, "claim", "sd-01-001", "--take-stale")[0], "still alive")
        self.at(hours=slides.LEASE_HOURS + 1)
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("--take-stale", err)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")[0])
        record = self.record(b, "sd-01-001")
        self.assertEqual((["claude/a"], 1), (record["taken_from"], record["generation"]))

    def test_a_takeover_beats_the_claim_it_took_over_even_if_the_old_owner_wakes_up(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=slides.LEASE_HOURS + 1)
        self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")
        self.assertEqual(1, self.run_in(a, "touch", "--publish")[0], "a's renewal does not outrank the takeover")
        self.assertEqual(0, self.run_in(b, "verify")[0])

    def test_touching_keeps_a_claim_alive(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=60)
        self.assertEqual(0, self.run_in(a, "touch", "--publish")[0])
        self.at(hours=100)
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("claimed by claude/a", err)
        self.assertNotIn("--take-stale", err)

    def test_a_heartbeat_from_the_future_is_not_proof_of_life(self) -> None:
        holding = slides.Holding("sd-01-001", "doing", "claude/a", "2026-10-17T08:00:00Z", "2026-10-20T08:00:00Z", 0, (), "x")
        self.assertTrue(slides.is_stale(holding, T0))


class FinishTests(Sessions):
    def test_a_finished_deck_cannot_be_claimed_again(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        code, _, err = self.finish(a, "sd-01-001", "--publish")
        self.assertEqual(0, code, err)
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("already built by claude/a", err)

    def test_finish_records_the_deck_and_drops_the_heartbeat(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.finish(a, "sd-01-001")[0])
        record = self.record(a, "sd-01-001")
        self.assertEqual(("done", CANVAS, 10, "1920x1080", "pending"),
                         (record["status"], record["moda_canvas"], record["slide_count"], record["size"], record["exports"]))
        self.assertNotIn("heartbeat_at", record)
        self.assertEqual([], slides.folder_problems(a / "store" / "lessons" / "sd-01-001" / "slides", "sd-01-001"))

    def test_finish_refuses_a_deck_the_session_does_not_hold(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(2, self.finish(b, "sd-01-001")[0])
        self.assertIsNone(self.record(b, "sd-01-001"))

    def test_finish_refuses_a_claim_that_was_lost(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(a, "claim", "sd-01-001")
        self.at(seconds=5)
        self.run_in(b, "claim", "sd-01-001", "--publish")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        code, _, err = self.finish(b, "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/a", err)

    def test_finish_refuses_a_record_that_names_no_moda_canvas(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        before = self.record(a, "sd-01-001")
        code, _, err = self.run_in(a, "finish", "sd-01-001", "--canvas", "abc", "--url", "https://example.com/x",
                                   "--slides", "10")
        self.assertEqual(1, code)
        self.assertIn("moda_canvas", err)
        self.assertIn("moda_url", err)
        self.assertEqual(before, self.record(a, "sd-01-001"))

    def test_finish_with_exports_done_needs_every_file_and_leaves_the_record_alone_otherwise(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        before = self.record(a, "sd-01-001")
        code, _, err = self.finish(a, "sd-01-001", "--exports", "done")
        self.assertEqual(1, code)
        self.assertIn("sd-01-001.pptx is missing", err)
        self.assertIn("10.png is missing", err)
        self.assertEqual(before, self.record(a, "sd-01-001"))

    def test_exported_records_complete_exports_and_refuses_incomplete_ones(self) -> None:
        import zipfile

        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.finish(a, "sd-01-001")
        folder = a / "store" / "lessons" / "sd-01-001" / "slides"
        code, _, err = self.run_in(a, "exported", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("sd-01-001.pptx is missing", err)
        self.assertEqual("pending", self.record(a, "sd-01-001")["exports"])
        with zipfile.ZipFile(folder / "sd-01-001.pptx", "w") as archive:
            archive.writestr("x", "x")
        for number in range(1, 11):
            png(folder / f"{number:02d}.png")
        code, _, err = self.run_in(a, "exported", "sd-01-001", "--publish")
        self.assertEqual(0, code, err)
        self.assertEqual("done", self.record(a, "sd-01-001")["exports"])
        self.assertIn("10.png", git(a, "ls-tree", "-r", "--name-only", "origin/claude/a"))

    def test_exported_refuses_a_deck_that_is_not_finished(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        code, _, err = self.run_in(a, "exported", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("not a finished deck", err)

    def test_release_gives_a_claim_back_but_never_a_finished_deck(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "sd-01-002", "--publish")
        self.assertEqual(0, self.run_in(a, "release", "sd-01-001", "--publish")[0])
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--publish")[0])
        self.finish(a, "sd-01-002")
        code, _, err = self.run_in(a, "release", "sd-01-002")
        self.assertEqual(1, code)
        self.assertIn("already finished", err)

    def test_a_claim_that_was_never_pushed_can_be_released_and_pushed(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001")
        self.assertEqual(0, self.run_in(a, "release", "sd-01-001", "--publish")[0])
        self.assertIsNone(self.record(a, "sd-01-001"))


class FolderTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name) / "slides"
        self.dir.mkdir()

    def write(self, **fields: object) -> None:
        record = {"id": "sd-01-001", "status": "done", "owner": "claude/a", "done_at": "2026-10-17T09:00:00Z",
                  "moda_canvas": CANVAS, "moda_url": URL, "slide_count": 4, "size": "1920x1080", "exports": "pending"}
        record.update(fields)
        (self.dir / "deck.yaml").write_text(slides.render(record), encoding="utf-8")

    def exports(self, count: int = 4) -> None:
        import zipfile

        with zipfile.ZipFile(self.dir / "sd-01-001.pptx", "w") as archive:
            archive.writestr("x", "x")
        for number in range(1, count + 1):
            png(self.dir / f"{number:02d}.png")

    def problems(self) -> list[str]:
        return slides.folder_problems(self.dir, "sd-01-001")

    def test_pending_exports_leave_only_the_record(self) -> None:
        self.write()
        self.assertEqual([], self.problems())
        (self.dir / "01.png").write_bytes(b"x")
        self.assertTrue(any("01.png is not expected" in problem for problem in self.problems()))

    def test_complete_exports_pass(self) -> None:
        self.write(exports="done")
        self.exports()
        self.assertEqual([], self.problems())

    def test_a_missing_slide_or_a_wrong_size_is_reported(self) -> None:
        self.write(exports="done")
        self.exports(3)
        self.assertEqual(["04.png is missing"], self.problems())
        png(self.dir / "04.png", 800, 600)
        self.assertEqual(["04.png is not a 1920x1080 PNG"], self.problems())

    def test_a_pptx_that_is_not_a_zip_is_reported(self) -> None:
        self.write(exports="done")
        self.exports()
        (self.dir / "sd-01-001.pptx").write_bytes(b"not a zip")
        self.assertEqual(["sd-01-001.pptx is not a PowerPoint file"], self.problems())

    def test_a_record_for_another_lesson_or_with_a_stray_key_is_reported(self) -> None:
        self.write(id="sd-01-002", heartbeat_at="2026-10-17T09:00:00Z")
        text = "\n".join(self.problems())
        self.assertIn("id must be sd-01-001", text)
        self.assertIn("'heartbeat_at' is not allowed on a done record", text)

    def test_a_hand_written_timestamp_without_quotes_is_still_a_timestamp(self) -> None:
        text = slides.render({"id": "sd-01-001", "status": "doing", "owner": "claude/a",
                              "claimed_at": "2026-10-17T09:00:00Z", "heartbeat_at": "2026-10-17T09:00:00Z"})
        unquoted = text.replace("'", "")
        self.assertIsInstance(yaml.safe_load(unquoted)["claimed_at"], datetime.datetime)
        self.assertEqual("2026-10-17T09:00:00Z", slides.parse_record(unquoted)["claimed_at"])
        self.assertEqual([], slides.record_problems(slides.parse_record(unquoted), "sd-01-001"))

    def test_the_record_is_required(self) -> None:
        self.assertEqual(["deck.yaml is missing"], self.problems())


if __name__ == "__main__":
    unittest.main()
