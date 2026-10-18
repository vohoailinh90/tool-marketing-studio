"""scripts/sd101_slides.py: the slide-deck claims, with real git repositories standing in for the sessions' containers."""

from __future__ import annotations

import contextlib
import datetime
import io
import itertools
import os
import struct
import tempfile
import unittest
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


def pptx(path: Path, parts: tuple[str, ...] = slides.PPTX_PARTS, badged: bool = False, count: int = 8,
         stripped: int = 0) -> None:
    """A minimal presentation of `count` slides; `badged` puts the picture Moda's free plan adds, named as Moda does, on
    every slide but the last `stripped` ones."""
    import zipfile

    with zipfile.ZipFile(path, "w") as archive:
        for part in parts:
            archive.writestr(part, "<x/>")
        badge = '<p:pic><p:nvPicPr><p:cNvPr id="32" name="Moda image moda-export-watermark-1"/></p:nvPicPr></p:pic>'
        for number in range(1, count + 1):
            on = badged and number <= count - stripped
            archive.writestr(f"ppt/slides/slide{number}.xml", f"<p:sld>{badge if on else ''}</p:sld>")
            archive.writestr(f"ppt/slides/_rels/slide{number}.xml.rels", "<Relationships/>")


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

    def merge_into_main(self, branch: str) -> None:
        """What merging a pull request does to the registry: the branch's records land on the default branch."""
        git(self.seed, "fetch", "--quiet", "origin", branch)
        git(self.seed, "merge", "--quiet", "--no-edit", "FETCH_HEAD")
        git(self.seed, "push", "--quiet", "origin", "main")

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

    def test_a_claim_released_on_its_own_branch_is_not_kept_alive_by_the_copy_merged_into_main(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.merge_into_main("claude/a")
        self.assertEqual(0, self.run_in(a, "release", "sd-01-001", "--publish")[0])
        code, _, err = self.run_in(b, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, code, err)

    def test_a_claim_merged_into_main_counts_again_once_its_branch_is_gone(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.merge_into_main("claude/a")
        git(a, "push", "--quiet", "origin", "--delete", "claude/a")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("claimed by claude/a", err)

    def test_a_done_record_edited_into_an_invalid_one_still_holds_its_lesson(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.finish(a, "sd-01-001", "--publish")[0])
        path = a / "store" / "lessons" / "sd-01-001" / "slides" / "deck.yaml"
        path.write_text(path.read_text(encoding="utf-8").replace("slide_count: 10", "slide_count: 99"), encoding="utf-8")
        git(a, "commit", "--quiet", "-am", "edit")
        git(a, "push", "--quiet", "origin", "claude/a")
        code, _, err = self.run_in(b, "claim", "sd-01-001", "--publish")
        self.assertEqual(1, code)
        self.assertIn("already built by claude/a", err)

    def test_a_record_that_cannot_be_read_blocks_its_lesson_until_it_is_fixed(self) -> None:
        folder = self.seed / "store" / "lessons" / "sd-01-001" / "slides"
        folder.mkdir()
        (folder / "deck.yaml").write_text("{{{ not yaml", encoding="utf-8")
        git(self.seed, "add", "-A")
        git(self.seed, "commit", "--quiet", "-m", "broken record")
        git(self.seed, "push", "--quiet", "origin", "main")
        b = self.session("b")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)
        self.assertEqual((0, "sd-01-002 sd-01-003\n"), self.run_in(b, "next", "--count", "2")[:2])
        code, out, _ = self.run_in(b, "status")
        self.assertEqual(0, code)
        self.assertIn("invalid 1", out)

    def test_a_record_whose_values_cannot_be_built_blocks_its_lesson_instead_of_stopping_the_tool(self) -> None:
        texts = {"a month that does not exist": "claimed_at: 2026-13-01T00:00:00Z\n",
                 "a day that does not exist": "claimed_at: 2026-02-30T00:00:00Z\n",
                 "a time before year 1 in UTC": "claimed_at: 0001-01-01T00:00:00+05:00\n",
                 "nesting too deep to read": "taken_from: " + "[" * 5000 + "]" * 5000 + "\n"}
        for label, line in texts.items():
            with self.subTest(label):
                self.assertIsNone(slides.parse_record(f"id: sd-01-001\nstatus: doing\nowner: claude/x\n{line}"))
        x, b = self.session("x"), self.session("b")
        folder = x / "store" / "lessons" / "sd-01-001" / "slides"
        folder.mkdir()
        (folder / "deck.yaml").write_text("id: sd-01-001\nstatus: doing\nowner: claude/x\nclaimed_at: 2026-13-01T00:00:00Z\n"
                                          "heartbeat_at: 2026-10-17T08:00:00Z\n", encoding="utf-8")
        git(x, "add", "-A")
        git(x, "commit", "--quiet", "-m", "a typo")
        git(x, "push", "--quiet", "-u", "origin", "claude/x")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)
        code, out, _ = self.run_in(b, "status")
        self.assertEqual(0, code)
        self.assertIn("invalid 1", out)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-002")[0], "every other lesson can still be claimed")

    def test_offline_never_publishes_the_default_branch(self) -> None:
        before = git(self.seed, "rev-parse", "origin/main")
        code, _, err = self.run_in(self.seed, "--offline", "claim", "sd-01-001")
        self.assertEqual(2, code)
        self.assertIn("default branch", err)
        code, _, err = self.run_in(self.seed, "--offline", "claim", "sd-01-001", "--publish")
        self.assertEqual(2, code)
        self.assertEqual(before, git(self.seed, "ls-remote", "origin", "refs/heads/main").split()[0])
        self.assertFalse((self.seed / "store" / "lessons" / "sd-01-001" / "slides").exists())

    def test_a_claim_whose_record_is_missing_here_is_not_published_as_a_deletion(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--publish")[0])
        relative = "store/lessons/sd-01-001/slides/deck.yaml"
        foreign = slides.render({"id": "sd-01-001", "status": "doing", "owner": "claude/zz",
                                 "claimed_at": "2026-10-17T07:00:00Z", "heartbeat_at": "2026-10-17T07:00:00Z"})
        for change in ("deleted", "folder removed", "replaced by another owner's record"):
            with self.subTest(change=change):
                (a / relative).unlink()
                if change == "folder removed":
                    (a / relative).parent.rmdir()
                if change.startswith("replaced"):
                    (a / relative).write_text(foreign, encoding="utf-8")
                pushed = git(a, "rev-parse", "origin/claude/a")
                code, _, err = self.run_in(a, "claim", "sd-01-001", "--publish")
                self.assertEqual(1, code)
                self.assertIn(f"this tree's deck.yaml is missing or not yours; restore it with "
                              f"`git checkout origin/claude/a -- {relative}`", err)
                self.assertEqual(pushed, git(a, "ls-remote", "origin", "refs/heads/claude/a").split()[0], "nothing pushed")
                self.assertIn(relative, git(a, "ls-tree", "-r", "--name-only", "origin/claude/a"))
                code, _, err = self.run_in(b, "claim", "sd-01-001")
                self.assertEqual(1, code)
                self.assertIn("claimed by claude/a", err)
                git(a, "checkout", "--quiet", "origin/claude/a", "--", relative)  # the hint the refusal gives
                self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--publish")[0])

    def test_publishing_checks_the_remote_afterwards_so_it_refuses_to_run_offline(self) -> None:
        a = self.session("a")
        finish = ("finish", "sd-01-001", "--canvas", CANVAS, "--url", URL, "--slides", "8")
        for command in (("claim", "sd-01-001"), ("touch",), finish, ("exported", "sd-01-001"), ("release", "sd-01-001")):
            with self.subTest(command=command[0]):
                code, _, err = self.run_in(a, "--offline", *command, "--publish")
                self.assertEqual(2, code)
                self.assertIn("cannot be combined with --offline", err)
                self.assertIsNone(self.record(a, "sd-01-001"), "nothing was written")
                self.assertEqual("", git(a, "ls-remote", "origin", "refs/heads/claude/a"), "nothing was pushed")
        self.assertEqual(0, self.run_in(a, "--offline", "claim", "sd-01-001")[0], "offline without --publish still works")

    def test_a_parseable_record_without_an_owner_or_with_an_unknown_status_blocks_its_lesson(self) -> None:
        for text in ("id: sd-01-001\nstatus: doing\nclaimed_at: 2026-10-17T08:00:00Z\nheartbeat_at: 2026-10-17T08:00:00Z\n",
                     "id: sd-01-001\nstatus: banana\nowner: claude/y\n",
                     "id: sd-01-001\nstatus: doing\nowner: claude/z\nclaimed_at: 2026-10-17T08:00:00Z\n"):  # z is not x
            with self.subTest(record=text.splitlines()[2]):
                x, b = self.session("x"), self.session("b")
                folder = x / "store" / "lessons" / "sd-01-001" / "slides"
                folder.mkdir()
                (folder / "deck.yaml").write_text(text, encoding="utf-8")
                git(x, "add", "-A")
                git(x, "commit", "--quiet", "-m", "record")
                git(x, "push", "--quiet", "-u", "origin", "claude/x")
                code, _, err = self.run_in(b, "claim", "sd-01-001")
                self.assertEqual(1, code)
                self.assertIn("cannot be read", err)
                git(x, "push", "--quiet", "origin", "--delete", "claude/x")
                for path in (self.tmp / "x", self.tmp / "b"):
                    import shutil
                    shutil.rmtree(path)

    def test_a_published_claim_that_fails_validation_is_not_a_claim_that_verifies(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        path = a / "store" / "lessons" / "sd-01-001" / "slides" / "deck.yaml"
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if not line.startswith("claimed_at")]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        git(a, "commit", "--quiet", "-am", "claimed_at removed")
        git(a, "push", "--quiet", "origin", "claude/a")
        code, _, err = self.run_in(a, "verify")
        self.assertEqual(1, code)
        self.assertIn("cannot be used as a claim", err)
        self.assertEqual(1, self.finish(a, "sd-01-001")[0])

    def test_a_damaged_copy_of_my_claim_in_this_tree_does_not_verify_touch_or_finish(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        path = a / "store" / "lessons" / "sd-01-001" / "slides" / "deck.yaml"
        published = path.read_text(encoding="utf-8")
        lines = [line for line in published.splitlines() if not line.startswith("claimed_at")]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")  # damaged here only: the pushed copy is fine
        damaged = path.read_text(encoding="utf-8")
        for command in (("verify",), ("touch",)):
            with self.subTest(command=command[0]):
                code, _, err = self.run_in(a, *command)
                self.assertEqual(1, code)
                self.assertIn("your record on this working tree cannot be used as a claim", err)
        self.assertEqual(1, self.finish(a, "sd-01-001")[0])
        self.assertEqual(damaged, path.read_text(encoding="utf-8"))
        path.write_text(published, encoding="utf-8")
        self.assertEqual(0, self.run_in(a, "verify")[0])

    def test_an_invalid_utf8_record_or_a_directory_in_its_place_blocks_the_lesson(self) -> None:
        import shutil

        for label in ("bytes", "directory"):
            with self.subTest(label=label):
                x, b = self.session("x"), self.session("b")
                folder = x / "store" / "lessons" / "sd-01-001" / "slides"
                if label == "bytes":
                    folder.mkdir()
                    (folder / "deck.yaml").write_bytes(  # otherwise valid: only the replaced byte would make its owner another one
                        b"id: sd-01-001\nstatus: doing\nowner: claude/x\xff\nclaimed_at: 2026-10-17T08:00:00Z\n"
                        b"heartbeat_at: 2026-10-17T08:00:00Z\n")
                else:
                    (folder / "deck.yaml").mkdir(parents=True)
                    (folder / "deck.yaml" / "note.txt").write_text("not a record", encoding="utf-8")
                git(x, "add", "-A")
                git(x, "commit", "--quiet", "-m", label)
                git(x, "push", "--quiet", "-u", "origin", "claude/x")
                code, _, err = self.run_in(b, "claim", "sd-01-001")
                self.assertEqual(1, code)
                self.assertIn("cannot be read", err)
                git(x, "push", "--quiet", "origin", "--delete", "claude/x")
                shutil.rmtree(x)
                shutil.rmtree(b)

    def test_a_record_with_a_key_named_twice_blocks_its_lesson(self) -> None:
        x, b = self.session("x"), self.session("b")
        folder = x / "store" / "lessons" / "sd-01-001" / "slides"
        folder.mkdir()
        (folder / "deck.yaml").write_text(
            "id: sd-01-001\nstatus: doing\nowner: claude/x\nclaimed_at: 2026-10-17T08:00:00Z\n"
            "heartbeat_at: 2026-10-17T08:00:00Z\nowner: claude/b\n", encoding="utf-8")
        git(x, "add", "-A")
        git(x, "commit", "--quiet", "-m", "owner twice")
        git(x, "push", "--quiet", "-u", "origin", "claude/x")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)

    def test_a_malformed_record_in_my_own_checkout_blocks_the_claim_and_is_left_alone(self) -> None:
        b = self.session("b")
        folder = b / "store" / "lessons" / "sd-01-001" / "slides"
        folder.mkdir()
        damaged = "<<<<<<< HEAD\nstatus: doing\n=======\nstatus: done\n>>>>>>> main\n"
        (folder / "deck.yaml").write_text(damaged, encoding="utf-8")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)
        self.assertEqual(damaged, (folder / "deck.yaml").read_text(encoding="utf-8"))

    def test_a_malformed_record_in_my_checkout_blocks_the_claim_even_when_it_names_another_owner(self) -> None:
        b = self.session("b")
        folder = b / "store" / "lessons" / "sd-01-001" / "slides"
        folder.mkdir()
        damaged = "id: sd-01-001\nstatus: doing\nowner: claude/x\nclaimed_at: 2026-10-17T08:00:00Z\n"  # no heartbeat_at
        (folder / "deck.yaml").write_text(damaged, encoding="utf-8")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)
        self.assertEqual(damaged, (folder / "deck.yaml").read_text(encoding="utf-8"))

    def test_a_malformed_claim_on_the_default_branch_blocks_even_when_its_owner_branch_exists(self) -> None:
        x, b = self.session("x"), self.session("b")
        git(x, "push", "--quiet", "-u", "origin", "claude/x")  # x's branch exists and carries no record
        folder = self.seed / "store" / "lessons" / "sd-01-001" / "slides"
        folder.mkdir()
        (folder / "deck.yaml").write_text(  # a doing record naming x, without its heartbeat
            "id: sd-01-001\nstatus: doing\nowner: claude/x\nclaimed_at: 2026-10-17T08:00:00Z\n", encoding="utf-8")
        git(self.seed, "add", "-A")
        git(self.seed, "commit", "--quiet", "-m", "damaged record")
        git(self.seed, "push", "--quiet", "origin", "main")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)

    def test_a_batch_claim_writes_nothing_when_one_destination_is_refused(self) -> None:
        import os

        a = self.session("a")
        store = a / "store"
        (store / "elsewhere").mkdir()
        os.symlink(store / "elsewhere", store / "lessons" / "sd-01-002" / "slides")
        real, written = Path.write_text, []

        def spy(self, *args, **kwargs):
            if self.name == "deck.yaml":
                written.append(self)
            return real(self, *args, **kwargs)

        with mock.patch.object(Path, "write_text", spy):
            code, _, err = self.run_in(a, "claim", "sd-01-001", "sd-01-002")
        self.assertEqual(2, code, err)
        self.assertIn("is a symbolic link", err)
        self.assertEqual([], written, "no record was written before every destination was known to be usable")
        self.assertFalse((store / "lessons" / "sd-01-001" / "slides").exists(), "the first lesson was not touched")

    def test_a_batch_claim_that_fails_half_way_puts_back_what_it_wrote(self) -> None:
        a = self.session("a")
        store = a / "store"
        real, calls = Path.write_text, []

        def flaky(self, *args, **kwargs):  # the disk fills up while the second record is written
            if self.name == "deck.yaml":
                calls.append(self)
                if len(calls) == 2:
                    raise OSError(28, "No space left on device")
            return real(self, *args, **kwargs)

        with mock.patch.object(Path, "write_text", flaky):
            code, _, err = self.run_in(a, "claim", "sd-01-001", "sd-01-002")
        self.assertEqual(2, code, err)
        self.assertEqual(2, len(calls))
        for lesson_id in ("sd-01-001", "sd-01-002"):
            self.assertFalse((store / "lessons" / lesson_id / "slides").exists(), lesson_id)

    def test_an_unreadable_record_on_a_feature_branch_blocks_its_lesson(self) -> None:
        x, b = self.session("x"), self.session("b")
        folder = x / "store" / "lessons" / "sd-01-001" / "slides"
        folder.mkdir()
        (folder / "deck.yaml").write_text("<<<<<<< HEAD\nstatus: doing\n=======\nstatus: done\n>>>>>>> other\n", encoding="utf-8")
        git(x, "add", "-A")
        git(x, "commit", "--quiet", "-m", "conflict markers")
        git(x, "push", "--quiet", "-u", "origin", "claude/x")
        code, _, err = self.run_in(b, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)

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

    def test_two_sessions_that_reclaim_each_others_expired_claims_at_once_still_have_one_winner(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(a, "claim", "sd-01-001")
        self.at(seconds=5)
        self.run_in(b, "claim", "sd-01-001")
        self.run_in(b, "claim", "sd-01-001", "--publish")
        self.run_in(a, "claim", "sd-01-001", "--publish")  # both claims are published, then both go quiet
        self.at(hours=slides.LEASE_HOURS + 1)
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001")[0])  # each reads the other's expired claim, neither has pushed
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001")[0])
        self.assertEqual((["claude/b"], 1), (self.record(a, "sd-01-001")["taken_from"], self.record(a, "sd-01-001")["generation"]))
        self.assertEqual((["claude/a"], 1), (self.record(b, "sd-01-001")["taken_from"], self.record(b, "sd-01-001")["generation"]))
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.run_in(b, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.run_in(a, "verify")[0], "the smaller owner wins when nothing else tells the claims apart")
        code, _, err = self.run_in(b, "verify")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/a", err)

    def test_an_owner_who_reclaims_a_lesson_taken_from_it_is_not_its_own_ancestor(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=slides.LEASE_HOURS + 1)
        self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")  # taken_from [a]
        self.at(hours=2 * slides.LEASE_HOURS + 2)  # b goes quiet too
        code, _, err = self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, code, err)
        record = self.record(a, "sd-01-001")
        self.assertEqual((["claude/b"], 2), (record["taken_from"], record["generation"]))
        self.assertEqual(0, self.run_in(a, "verify")[0])
        self.assertEqual(1, self.run_in(b, "claim", "sd-01-001")[0], "the lesson is a's again, not blocked")

    def test_a_local_record_whose_precedence_differs_from_the_published_claim_is_refused(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(hours=-2)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--publish")[0])
        self.at(hours=slides.LEASE_HOURS)  # b's claim expires and a takes it over
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--take-stale", "--publish")[0])
        relative = "store/lessons/sd-01-001/slides/deck.yaml"
        published = (a / relative).read_text(encoding="utf-8")
        edits = {"an earlier claimed_at": {"claimed_at": "2026-10-16T00:00:00Z"},
                 "another generation": {"generation": 5},
                 "a takeover dropped": {"taken_from": None, "generation": None}}
        for label, change in edits.items():
            with self.subTest(label):
                record = {**self.record(a, "sd-01-001"), **change}
                (a / relative).write_text(slides.render({k: v for k, v in record.items() if v is not None}),
                                          encoding="utf-8")
                for command in (("verify",), ("touch", "--publish"), ("claim", "sd-01-001", "--publish"),
                                ("finish", "sd-01-001", "--canvas", CANVAS, "--url", URL, "--slides", "8", "--publish")):
                    code, _, err = self.run_in(a, *command)
                    self.assertEqual(1, code, command)
                    self.assertIn("does not match your claim on origin/claude/a", err)
                self.assertEqual(yaml.safe_load(published), yaml.safe_load(git(a, "show", f"origin/claude/a:{relative}")),
                                 "nothing pushed")
                (a / relative).write_text(published, encoding="utf-8")
                self.assertEqual(0, self.run_in(a, "verify")[0])
        self.at(hours=2 * slides.LEASE_HOURS + 1)  # a's claim has expired too: an edited copy is still not a new claim
        record = {**self.record(a, "sd-01-001"), "claimed_at": "2026-10-16T00:00:00Z"}
        (a / relative).write_text(slides.render(record), encoding="utf-8")
        code, _, err = self.run_in(a, "touch", "--publish")
        self.assertEqual(1, code)
        self.assertIn("does not match your claim on origin/claude/a", err)
        self.assertEqual(yaml.safe_load(published), yaml.safe_load(git(a, "show", f"origin/claude/a:{relative}")))

    def test_an_expired_claim_that_a_quiet_stronger_claim_beats_is_not_renewed(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--publish")[0])
        self.at(hours=slides.LEASE_HOURS + 1)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")[0])
        self.at(hours=2 * slides.LEASE_HOURS + 3)  # b took a's claim over, and has gone quiet too
        relative = "store/lessons/sd-01-001/slides/deck.yaml"
        published = git(a, "show", f"origin/claude/a:{relative}")
        code, _, err = self.run_in(a, "touch", "--publish")
        self.assertEqual(1, code)
        self.assertIn("claude/b holds the stronger claim; take the lesson over on purpose with "
                      "`claim sd-01-001 --take-stale`", err)
        self.assertEqual(published, git(a, "show", f"origin/claude/a:{relative}"), "the superseded claim is not renewed")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--take-stale", "--publish")[0])
        self.assertEqual((["claude/b"], 2), (self.record(a, "sd-01-001")["taken_from"],
                                             self.record(a, "sd-01-001")["generation"]))
        code, _, err = self.run_in(b, "touch", "--publish")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/a", err)
        self.assertEqual(0, self.run_in(a, "verify")[0], "one live claim, one winner")

    def test_the_loser_of_a_race_does_not_come_back_by_renewing_after_both_went_quiet(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001")[0])
        self.at(seconds=5)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001")[0])
        self.run_in(b, "claim", "sd-01-001", "--publish")  # b pushes first but claimed later: it lost
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=slides.LEASE_HOURS + 1)
        code, _, err = self.run_in(b, "touch", "--publish")
        self.assertEqual(1, code)
        self.assertIn("claude/a holds the stronger claim", err)
        self.assertEqual(0, self.run_in(a, "touch", "--publish")[0], "the winner renews its own expired claim")

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

    def test_a_stale_copy_of_my_claim_on_main_does_not_hide_its_renewal_on_my_branch(self) -> None:
        z = self.tmp / "z"
        git(self.tmp, "clone", "--quiet", str(self.origin), str(z))
        git(z, "checkout", "--quiet", "-b", "zzz/a")  # sorts after main, so main's copy is read first
        self.run_in(z, "claim", "sd-01-001", "--publish")
        self.merge_into_main("zzz/a")
        self.at(hours=slides.LEASE_HOURS + 8)
        code, _, err = self.run_in(z, "touch", "--publish")
        self.assertEqual(0, code, err)
        self.assertEqual(0, self.run_in(z, "verify")[0])

    def test_my_own_stale_claim_can_be_claimed_again_when_an_older_stale_claim_exists(self) -> None:
        context = slides.Context(Path("."), Path("."), "origin", "claude/me", True)
        old = slides.Holding("sd-01-001", "doing", "claude/old", "2026-10-01T08:00:00Z", "2026-10-01T08:00:00Z", 0, (), "x")
        mine = slides.Holding("sd-01-001", "doing", "claude/me", "2026-10-10T08:00:00Z", "2026-10-10T08:00:00Z", 0, (), "y")
        self.assertIsNone(slides.refusal("sd-01-001", [old, mine], context, T0, False))
        self.assertIn("--take-stale", slides.refusal("sd-01-001", [old], context, T0, False))

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

    def test_finish_reports_an_earlier_claim_that_was_pushed_while_it_published(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(b, "claim", "sd-01-001")  # b claimed first but has not pushed yet
        self.at(seconds=5)
        self.run_in(a, "claim", "sd-01-001", "--publish")
        real = slides.publish

        def racing(context, paths, message):
            if context.me == "claude/a":  # b's push lands after a's check and before a's own push
                git(b, "add", "-A")
                git(b, "commit", "--quiet", "-m", "claim")
                git(b, "push", "--quiet", "-u", "origin", "claude/b")
            return real(context, paths, message)

        with mock.patch.object(slides, "publish", racing):
            code, _, err = self.finish(a, "sd-01-001", "--publish")
        self.assertEqual(1, code)
        self.assertIn("claude/b holds the earlier claim", err)

    def test_finish_reports_an_earlier_claimant_that_finished_while_it_published(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(b, "claim", "sd-01-001")  # b claimed first but has not pushed yet
        self.at(seconds=5)
        self.run_in(a, "claim", "sd-01-001", "--publish")
        real = slides.publish

        def racing(context, paths, message):
            if context.me == "claude/a":  # b pushes its claim and its finished deck while a is publishing
                self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--publish")[0])
                self.assertEqual(0, self.finish(b, "sd-01-001", "--publish")[0])
            return real(context, paths, message)

        with mock.patch.object(slides, "publish", racing):
            code, _, err = self.finish(a, "sd-01-001", "--publish")
        self.assertEqual(1, code)
        self.assertIn("claude/b holds the earlier claim", err)

    def test_finish_reports_an_unreadable_record_that_appeared_while_it_published(self) -> None:
        a, x = self.session("a"), self.session("x")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        real = slides.publish

        def racing(context, paths, message):
            if context.me == "claude/a":
                folder = x / "store" / "lessons" / "sd-01-001" / "slides"
                folder.mkdir(parents=True)
                (folder / "deck.yaml").write_text("{{{ not yaml", encoding="utf-8")
                git(x, "add", "-A")
                git(x, "commit", "--quiet", "-m", "broken")
                git(x, "push", "--quiet", "-u", "origin", "claude/x")
            return real(context, paths, message)

        with mock.patch.object(slides, "publish", racing):
            code, _, err = self.finish(a, "sd-01-001", "--publish")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)

    def test_finish_reports_a_malformed_claim_that_appeared_while_it_published(self) -> None:
        a, x = self.session("a"), self.session("x")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        real = slides.publish

        def racing(context, paths, message):
            if context.me == "claude/a":  # a parseable record with no heartbeat, pushed by another branch
                folder = x / "store" / "lessons" / "sd-01-001" / "slides"
                folder.mkdir(parents=True)
                (folder / "deck.yaml").write_text(
                    "id: sd-01-001\nstatus: doing\nowner: claude/x\nclaimed_at: 2026-10-17T07:00:00Z\n", encoding="utf-8")
                git(x, "add", "-A")
                git(x, "commit", "--quiet", "-m", "no heartbeat")
                git(x, "push", "--quiet", "-u", "origin", "claude/x")
            return real(context, paths, message)

        with mock.patch.object(slides, "publish", racing):
            code, _, err = self.finish(a, "sd-01-001", "--publish")
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err)

    def test_offline_honours_the_records_a_checkout_already_holds(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.finish(a, "sd-01-001", "--publish")[0])
        self.merge_into_main("claude/a")
        git(b, "fetch", "--quiet", "origin", "main")
        git(b, "merge", "--quiet", "--no-edit", "origin/main")
        before = self.record(b, "sd-01-001")
        code, _, err = self.run_in(b, "--offline", "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("already built by claude/a", err)
        self.assertEqual(before, self.record(b, "sd-01-001"))
        code, out, _ = self.run_in(b, "--offline", "status")
        self.assertEqual(0, code)
        self.assertIn("done 1 | doing 0", out)

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
        self.assertEqual(before, self.record(a, "sd-01-001"))

    def test_exported_records_a_pptx_exported_without_the_badge_and_refuses_a_missing_one(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.finish(a, "sd-01-001")
        folder = a / "store" / "lessons" / "sd-01-001" / "slides"
        code, _, err = self.run_in(a, "exported", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("sd-01-001.pptx is missing", err)
        self.assertEqual("pending", self.record(a, "sd-01-001")["exports"])
        pptx(folder / "sd-01-001.pptx", count=10)
        code, _, err = self.run_in(a, "exported", "sd-01-001", "--publish")
        self.assertEqual(0, code, err)
        self.assertEqual("done", self.record(a, "sd-01-001")["exports"])
        self.assertEqual("Slides: PPTX of sd-01-001", git(a, "log", "-1", "--format=%s", "origin/claude/a"))
        self.assertIn("sd-01-001.pptx", git(a, "ls-tree", "-r", "--name-only", "origin/claude/a"))

    def test_exported_badged_records_the_pptx_with_the_moda_badge_but_never_as_done(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.finish(a, "sd-01-001")
        folder = a / "store" / "lessons" / "sd-01-001" / "slides"
        code, _, err = self.run_in(a, "exported", "sd-01-001", "--badged")
        self.assertEqual(1, code)
        self.assertIn("sd-01-001.pptx is missing", err)
        pptx(folder / "sd-01-001.pptx", badged=True, count=10)
        code, _, err = self.run_in(a, "exported", "sd-01-001")
        self.assertEqual(1, code, "a file with the badge is never recorded as done")
        self.assertIn("sd-01-001.pptx carries the moda.app badge", err)
        self.assertEqual("pending", self.record(a, "sd-01-001")["exports"])
        code, out, err = self.run_in(a, "exported", "sd-01-001", "--badged", "--publish")
        self.assertEqual(0, code, err)
        self.assertIn("exports of sd-01-001 are badged", out)
        self.assertEqual("badged", self.record(a, "sd-01-001")["exports"])
        self.assertIn("sd-01-001.pptx", git(a, "ls-tree", "-r", "--name-only", "origin/claude/a"))
        self.assertEqual("Slides: badged PPTX of sd-01-001", git(a, "log", "-1", "--format=%s", "origin/claude/a"))

    def test_exported_refuses_a_deck_that_is_not_finished(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        code, _, err = self.run_in(a, "exported", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("not a finished deck", err)

    def exports_in(self, clone: Path) -> Path:
        folder = clone / "store" / "lessons" / "sd-01-001" / "slides"
        pptx(folder / "sd-01-001.pptx", count=10)
        return folder

    def test_finish_waits_for_a_renewal_when_the_lease_has_expired(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.at(hours=slides.LEASE_HOURS + 1)
        before = self.record(a, "sd-01-001")
        code, _, err = self.finish(a, "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("has expired; run touch --publish", err)
        self.assertEqual(before, self.record(a, "sd-01-001"))
        self.assertEqual(0, self.run_in(a, "touch", "--publish")[0])
        self.assertEqual(0, self.finish(a, "sd-01-001", "--publish")[0])

    def test_exports_of_a_claim_that_was_taken_over_meanwhile_are_not_published(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.finish(a, "sd-01-001")[0])  # finished here only: the remote still holds the claim
        self.exports_in(a)
        self.at(hours=slides.LEASE_HOURS + 1)
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--take-stale", "--publish")[0])
        code, _, err = self.run_in(a, "exported", "sd-01-001", "--publish")
        self.assertEqual(1, code)
        self.assertIn("lost to claude/b", err)
        self.assertIn("status: doing", git(a, "show", "origin/claude/a:store/lessons/sd-01-001/slides/deck.yaml"))
        self.assertEqual(0, self.run_in(b, "verify")[0], "the lesson is still b's")

    def test_exports_are_checked_again_after_they_are_published(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(b, "claim", "sd-01-001")  # b claimed first but has not pushed yet
        self.at(seconds=5)
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.finish(a, "sd-01-001")[0])
        self.exports_in(a)
        real = slides.publish

        def racing(context, paths, message):
            if context.me == "claude/a":  # b's push lands after a's check and before a's own push
                git(b, "add", "-A")
                git(b, "commit", "--quiet", "-m", "claim")
                git(b, "push", "--quiet", "-u", "origin", "claude/b")
            return real(context, paths, message)

        with mock.patch.object(slides, "publish", racing):
            code, _, err = self.run_in(a, "exported", "sd-01-001", "--publish")
        self.assertEqual(1, code)
        self.assertIn("claude/b holds the earlier claim", err)

    def test_the_exports_of_another_sessions_deck_are_not_a_claim_of_mine(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.finish(a, "sd-01-001", "--publish")
        self.merge_into_main("claude/a")
        git(b, "fetch", "--quiet", "origin", "main")
        git(b, "merge", "--quiet", "--no-edit", "origin/main")
        self.exports_in(b)
        code, _, err = self.run_in(b, "exported", "sd-01-001", "--publish")
        self.assertEqual(0, code, err)

    def test_a_symbolic_link_in_the_way_of_a_record_stops_every_write(self) -> None:
        import os
        import shutil

        for label in ("slides", "lesson", "record"):
            with self.subTest(label=label):
                name = f"s{label}"
                clone = self.session(name)
                store = clone / "store"
                elsewhere = store / "elsewhere"
                elsewhere.mkdir()
                lesson = store / "lessons" / "sd-01-001"
                if label == "slides":
                    os.symlink(elsewhere, lesson / "slides")
                elif label == "lesson":
                    shutil.move(lesson, store / "moved-lesson")
                    os.symlink(store / "moved-lesson", lesson)
                else:
                    (lesson / "slides").mkdir()
                    os.symlink(elsewhere / "deck.yaml", lesson / "slides" / "deck.yaml")  # dangling
                code, _, err = self.run_in(clone, "claim", "sd-01-001")
                self.assertEqual(2, code, err)
                self.assertIn("is a symbolic link", err)
                self.assertEqual([], sorted(path.name for path in elsewhere.iterdir()))
                self.assertFalse((store / "moved-lesson" / "slides").exists())

    def test_a_symbolic_link_to_a_folder_outside_the_repository_is_refused_not_followed(self) -> None:
        import os

        clone = self.session("out")
        outside = self.tmp / "outside"
        outside.mkdir()
        os.symlink(outside, clone / "store" / "lessons" / "sd-01-001" / "slides")
        code, _, err = self.run_in(clone, "claim", "sd-01-001")
        self.assertEqual(2, code, err)
        self.assertIn("is a symbolic link", err)
        self.assertEqual([], list(outside.iterdir()))

    def test_verify_checks_a_finished_deck_that_was_pushed_by_hand(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.at(seconds=0)
        self.run_in(b, "claim", "sd-01-001")  # b claimed first but has not pushed yet
        self.at(seconds=5)
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.finish(a, "sd-01-001")[0])
        code, _, err = self.run_in(a, "verify")
        self.assertEqual(1, code)
        self.assertIn("the finished record is not on origin/claude/a", err)
        git(a, "add", "-A")  # what a documented `commit the slides/ folder` does: no check on the way out
        git(a, "commit", "--quiet", "-m", "slides")
        git(a, "push", "--quiet", "origin", "claude/a")
        self.assertEqual(0, self.run_in(a, "verify")[0], "nobody else has pushed a claim yet")
        git(b, "add", "-A")
        git(b, "commit", "--quiet", "-m", "claim")
        git(b, "push", "--quiet", "-u", "origin", "claude/b")
        code, _, err = self.run_in(a, "verify")
        self.assertEqual(1, code)
        self.assertIn("claude/b holds the earlier claim", err)

    def test_verify_rejects_a_finished_record_that_was_damaged_before_it_was_pushed(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.finish(a, "sd-01-001", "--publish")[0])
        self.assertEqual(0, self.run_in(a, "verify")[0])
        path = a / "store" / "lessons" / "sd-01-001" / "slides" / "deck.yaml"
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if not line.startswith("claimed_at")]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        code, _, err = self.run_in(a, "verify")
        self.assertEqual(1, code, "damaged in this tree, before it is pushed")
        self.assertIn("your finished record on this working tree cannot be used", err)
        git(a, "commit", "--quiet", "-am", "claimed_at removed")
        git(a, "push", "--quiet", "origin", "claude/a")
        code, _, err = self.run_in(a, "verify")
        self.assertEqual(1, code, "damaged on the remote")
        self.assertIn("cannot be used", err)

    def test_touch_does_not_treat_a_finished_deck_as_a_claim_to_renew(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.assertEqual(0, self.finish(a, "sd-01-001")[0])
        code, _, err = self.run_in(a, "touch")
        self.assertEqual(2, code)
        self.assertIn("you hold no claim", err)

    def test_a_staging_failure_stops_publishing_instead_of_pushing_nothing(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        self.finish(a, "sd-01-001")
        folder = a / "store" / "lessons" / "sd-01-001" / "slides"
        pptx(folder / "sd-01-001.pptx", count=10)
        lock = Path(git(a, "rev-parse", "--absolute-git-dir")) / "index.lock"
        lock.write_text("", encoding="utf-8")  # the index is busy: git add cannot stage anything
        code, _, err = self.run_in(a, "exported", "sd-01-001", "--publish")
        self.assertEqual(2, code)
        self.assertIn("git add failed", err)
        lock.unlink()
        self.assertNotIn("sd-01-001.pptx", git(a, "ls-tree", "-r", "--name-only", "origin/claude/a"))
        self.assertEqual(0, self.run_in(a, "exported", "sd-01-001", "--publish")[0], "once the index is free it publishes")
        self.assertIn("sd-01-001.pptx", git(a, "ls-tree", "-r", "--name-only", "origin/claude/a"))

    def test_a_finished_record_whose_precedence_differs_from_the_published_one_is_refused(self) -> None:
        a = self.session("a")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "sd-01-002", "--publish")[0])
        self.assertEqual(0, self.finish(a, "sd-01-001", "--publish")[0])  # its done record is on the remote
        self.assertEqual(0, self.finish(a, "sd-01-002")[0])  # done only here; the remote still holds the claim
        for lesson_id, commands in (("sd-01-001", (("verify", "sd-01-001"), ("exported", "sd-01-001", "--publish"))),
                                    ("sd-01-002", (("exported", "sd-01-002", "--publish"),))):
            relative = f"store/lessons/{lesson_id}/slides/deck.yaml"
            published = git(a, "show", f"origin/claude/a:{relative}")
            kept = (a / relative).read_text(encoding="utf-8")
            for label, change in (("an earlier claimed_at", {"claimed_at": "2026-10-16T00:00:00Z"}),
                                  ("a takeover added", {"taken_from": ["claude/zz"], "generation": 1})):
                with self.subTest(lesson_id=lesson_id, change=label):
                    (a / relative).write_text(slides.render({**self.record(a, lesson_id), **change}), encoding="utf-8")
                    for command in commands:
                        code, _, err = self.run_in(a, *command)
                        self.assertEqual(1, code, command)
                        self.assertIn("does not match your claim on origin/claude/a", err)
                    self.assertEqual(published, git(a, "show", f"origin/claude/a:{relative}"), "nothing pushed")
                    (a / relative).write_text(kept, encoding="utf-8")
        self.assertEqual(0, self.run_in(a, "verify", "sd-01-001")[0], "the restored record verifies again")

    def test_release_gives_a_claim_back_but_never_a_finished_deck(self) -> None:
        a, b = self.session("a"), self.session("b")
        self.run_in(a, "claim", "sd-01-001", "sd-01-002", "--publish")
        self.assertEqual(0, self.run_in(a, "release", "sd-01-001", "--publish")[0])
        self.assertEqual(0, self.run_in(b, "claim", "sd-01-001", "--publish")[0])
        self.finish(a, "sd-01-002")
        code, _, err = self.run_in(a, "release", "sd-01-002")
        self.assertEqual(1, code)
        self.assertIn("already finished", err)

    def test_release_never_pushes_a_deletion_over_a_finished_record_on_the_remote(self) -> None:
        a = self.session("a")
        self.assertEqual(0, self.run_in(a, "claim", "sd-01-001", "--publish")[0])
        relative = "store/lessons/sd-01-001/slides/deck.yaml"
        claim = (a / relative).read_text(encoding="utf-8")
        self.assertEqual(0, self.finish(a, "sd-01-001", "--publish")[0])
        finished = git(a, "show", f"origin/claude/a:{relative}")
        (a / relative).write_text(claim, encoding="utf-8")  # a conflict resolution put the claim back
        for extra in ((), ("--publish",)):
            with self.subTest(extra=extra):
                code, _, err = self.run_in(a, "release", "sd-01-001", *extra)
                self.assertEqual(1, code)
                self.assertIn("your finished record is on origin/claude/a; a finished deck is not released", err)
                self.assertTrue((a / relative).is_file())
                self.assertEqual(finished, git(a, "show", f"origin/claude/a:{relative}"), "the finished record stays")
        code, _, err = self.run_in(self.session("b"), "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("already built by claude/a", err)

    def test_of_two_finished_records_the_takeover_wins_as_it_does_for_claims(self) -> None:
        old = {"id": "sd-01-001", "status": "done", "owner": "claude/a", "claimed_at": "2026-10-13T08:00:00Z",
               "done_at": "2026-10-17T07:00:00Z", "moda_canvas": CANVAS, "moda_url": URL, "slide_count": 8,
               "size": "1920x1080", "exports": "pending"}
        taker = {**old, "owner": "claude/b", "claimed_at": "2026-10-16T09:00:00Z", "taken_from": ["claude/a"],
                 "generation": 1}
        for name, record in (("a", old), ("b", taker)):
            clone = self.session(name)
            folder = clone / "store" / "lessons" / "sd-01-001" / "slides"
            folder.mkdir()
            (folder / "deck.yaml").write_text(slides.render(record), encoding="utf-8")
            git(clone, "add", "-A")
            git(clone, "commit", "--quiet", "-m", "finished")
            git(clone, "push", "--quiet", "-u", "origin", f"claude/{name}")
        c = self.session("c")
        code, _, err = self.run_in(c, "claim", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("already built by claude/b", err)
        holdings, _ = slides.gather(slides.Context(c, c / "store", "origin", "claude/c", False), ["sd-01-001"])
        self.assertEqual("claude/b", slides.standing(holdings["sd-01-001"], self.clock)[1].owner)

    def test_release_refuses_to_leave_other_files_behind_in_slides(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001", "--publish")
        folder = a / "store" / "lessons" / "sd-01-001" / "slides"
        (folder / "extra.txt").write_text("x", encoding="utf-8")
        code, _, err = self.run_in(a, "release", "sd-01-001")
        self.assertEqual(1, code)
        self.assertIn("also holds extra.txt", err)
        self.assertTrue((folder / "deck.yaml").is_file())

    def test_a_claim_that_was_never_pushed_can_be_released_and_pushed(self) -> None:
        a = self.session("a")
        self.run_in(a, "claim", "sd-01-001")
        self.assertEqual(0, self.run_in(a, "release", "sd-01-001", "--publish")[0])
        self.assertIsNone(self.record(a, "sd-01-001"))

    def test_a_lesson_id_with_path_parts_never_reaches_a_file_outside_lessons(self) -> None:
        a = self.session("a")
        base = {"id": "sd-01-001", "owner": "claude/a", "claimed_at": "2026-10-17T08:00:00Z"}
        doing = slides.render({**base, "status": "doing", "heartbeat_at": "2026-10-17T08:00:00Z"})
        done = slides.render({**base, "status": "done", "done_at": "2026-10-17T09:00:00Z", "moda_canvas": CANVAS,
                              "moda_url": URL, "slide_count": 8, "size": "1920x1080", "exports": "pending"})
        decoys = {}
        for name, text in (("victim", doing), ("trophy", done)):
            folder = a / "store" / name / "slides"
            folder.mkdir(parents=True)
            (folder / "deck.yaml").write_text(text, encoding="utf-8")
            decoys[name] = (folder / "deck.yaml", text)
        for lesson_id, name in (("../victim", "victim"), ("sd-01-001/../../victim", "victim"),
                                (str(a / "store" / "victim"), "victim")):
            with self.subTest(command="release", lesson_id=lesson_id):
                code, _, err = self.run_in(a, "release", lesson_id)
                self.assertEqual(2, code)
                self.assertIn("is not a lesson id", err)
                self.assertEqual(decoys[name][1], decoys[name][0].read_text(encoding="utf-8"), "the decoy is left alone")
        for lesson_id in ("../trophy", str(a / "store" / "trophy")):
            with self.subTest(command="exported", lesson_id=lesson_id):
                code, _, err = self.run_in(a, "exported", lesson_id)
                self.assertEqual(2, code)
                self.assertIn("is not a lesson id", err)
                self.assertEqual(decoys["trophy"][1], decoys["trophy"][0].read_text(encoding="utf-8"))


class FolderTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name) / "slides"
        self.dir.mkdir()

    def write(self, **fields: object) -> None:
        record = {"id": "sd-01-001", "status": "done", "owner": "claude/a", "claimed_at": "2026-10-17T08:00:00Z",
                  "done_at": "2026-10-17T09:00:00Z",
                  "moda_canvas": CANVAS, "moda_url": URL, "slide_count": 8, "size": "1920x1080", "exports": "pending"}
        record.update(fields)
        (self.dir / "deck.yaml").write_text(slides.render(record), encoding="utf-8")

    def exports(self) -> None:
        pptx(self.dir / "sd-01-001.pptx")

    def problems(self) -> list[str]:
        return slides.folder_problems(self.dir, "sd-01-001")

    def test_pending_exports_leave_only_the_record(self) -> None:
        self.write()
        self.assertEqual([], self.problems())
        (self.dir / "notes.txt").write_bytes(b"x")
        self.assertEqual(["notes.txt is not expected here"], self.problems())

    def test_a_deck_is_its_pptx_alone_so_a_png_file_is_never_expected(self) -> None:
        for exports, badged in (("pending", False), ("badged", True), ("done", False)):
            with self.subTest(exports=exports):
                self.write(exports=exports)
                if exports != "pending":
                    pptx(self.dir / "sd-01-001.pptx", badged=badged)
                self.assertEqual([], self.problems())
                (self.dir / "01.png").write_bytes(b"x")
                self.assertEqual(["01.png is not expected here (the repository keeps a deck as its PPTX alone: no PNG "
                                  "files)"], self.problems())
                (self.dir / "01.png").unlink()

    def test_a_pptx_exported_without_the_badge_passes_as_done(self) -> None:
        self.write(exports="done")
        self.exports()
        self.assertEqual([], self.problems())

    def test_a_pptx_with_the_moda_badge_is_never_recorded_as_done(self) -> None:
        self.write(exports="done")
        pptx(self.dir / "sd-01-001.pptx", badged=True)
        self.assertEqual(["sd-01-001.pptx carries the moda.app badge: record it with `exported sd-01-001 --badged`"],
                         self.problems())

    def test_a_badged_export_is_the_pptx_alone(self) -> None:
        self.write(exports="badged")
        self.assertEqual(["sd-01-001.pptx is missing"], self.problems())
        pptx(self.dir / "sd-01-001.pptx", badged=True)
        self.assertEqual([], self.problems())
        (self.dir / "sd-01-001.pptx").write_bytes(b"not a zip")
        self.assertEqual(["sd-01-001.pptx is not a PowerPoint file: not a ZIP archive"], self.problems())

    def test_a_pptx_whose_badge_was_removed_from_some_slides_is_never_recorded_as_badged(self) -> None:
        self.write(exports="badged")
        pptx(self.dir / "sd-01-001.pptx", badged=True, stripped=1)
        self.assertEqual(["sd-01-001.pptx carries the moda.app badge on 7 of 8 slides: the badge is never removed, so "
                          "export the deck from Moda again"], self.problems())
        pptx(self.dir / "sd-01-001.pptx", badged=True)
        self.assertEqual([], self.problems())

    def test_a_pptx_short_of_the_deck_s_slides_is_never_recorded(self) -> None:
        for exports, badged in (("badged", True), ("done", False)):
            with self.subTest(exports=exports):
                self.write(exports=exports)
                if exports == "done":
                    self.exports()
                pptx(self.dir / "sd-01-001.pptx", badged=badged, count=1)
                self.assertEqual(["sd-01-001.pptx holds 1 slides, the deck 8: export the whole deck from Moda again"],
                                 self.problems())
                pptx(self.dir / "sd-01-001.pptx", badged=badged)
                self.assertEqual([], self.problems())

    def test_a_badge_free_pptx_is_never_recorded_as_badged(self) -> None:
        self.write(exports="badged")
        pptx(self.dir / "sd-01-001.pptx")
        self.assertEqual(["sd-01-001.pptx does not carry the moda.app badge: record it with `exported sd-01-001`"],
                         self.problems())

    def test_pending_exports_hold_no_pptx(self) -> None:
        self.write()
        for badged in (True, False):  # the hint fits a PPTX with the badge and one without it
            with self.subTest(badged=badged):
                pptx(self.dir / "sd-01-001.pptx", badged=badged)
                self.assertEqual(["sd-01-001.pptx is not expected here (once the deck is finished, record the export with "
                                  "`exported sd-01-001`, adding --badged when the PPTX carries the moda.app badge)"],
                                 self.problems())

    def test_a_missing_pptx_is_reported_for_every_recorded_export(self) -> None:
        for exports in ("badged", "done"):
            with self.subTest(exports=exports):
                self.write(exports=exports)
                self.assertEqual(["sd-01-001.pptx is missing"], self.problems())

    def test_a_deck_has_the_documented_size(self) -> None:
        self.write(size="800x600")
        self.assertIn("deck.yaml: size must be 1920x1080", self.problems())
        self.write(size="1920x1080")
        self.assertEqual([], self.problems())

    def test_a_deck_has_between_eight_and_ten_slides(self) -> None:
        for count, ok in ((7, False), (8, True), (10, True), (11, False)):
            with self.subTest(slides=count):
                self.write(slide_count=count)
                self.assertEqual(ok, self.problems() == [], self.problems())
        self.write(slide_count=7)
        self.assertIn("deck.yaml: slide_count must be between 8 and 10", self.problems())

    def test_a_pptx_that_is_not_a_zip_is_reported(self) -> None:
        self.write(exports="done")
        self.exports()
        (self.dir / "sd-01-001.pptx").write_bytes(b"not a zip")
        self.assertEqual(["sd-01-001.pptx is not a PowerPoint file: not a ZIP archive"], self.problems())

    def test_a_zip_without_the_parts_of_a_presentation_is_not_a_pptx(self) -> None:
        self.write(exports="done")
        self.exports()
        pptx(self.dir / "sd-01-001.pptx", ("x",))
        self.assertEqual(["sd-01-001.pptx is not a PowerPoint file: [Content_Types].xml, ppt/presentation.xml missing"],
                         self.problems())
        pptx(self.dir / "sd-01-001.pptx", ("[Content_Types].xml",))
        self.assertEqual(["sd-01-001.pptx is not a PowerPoint file: ppt/presentation.xml missing"], self.problems())

    def test_a_pptx_with_a_damaged_member_is_reported(self) -> None:
        self.write(exports="done")
        self.exports()
        path = self.dir / "sd-01-001.pptx"
        data = bytearray(path.read_bytes())
        data[data.index(b"<x/>")] ^= 0xFF  # the first member's stored bytes no longer match their checksum
        path.write_bytes(bytes(data))
        self.assertEqual(["sd-01-001.pptx is not a PowerPoint file: [Content_Types].xml is damaged"], self.problems())

    def test_a_pptx_with_a_part_that_cannot_be_unpacked_is_reported_not_raised(self) -> None:
        import zipfile

        def patched(change, payload: bytes = b"<x/>" * 50, method: int = zipfile.ZIP_DEFLATED) -> bytes:
            archive = io.BytesIO()
            with zipfile.ZipFile(archive, "w", method) as zipped:
                for part in slides.PPTX_PARTS:
                    zipped.writestr(part, payload)
            raw = bytearray(archive.getvalue())
            change(raw)
            return bytes(raw)

        def field(raw: bytearray, local: int, central: int, value: int) -> None:  # one 16-bit header field of the first part
            for signature, offset in ((b"PK\x03\x04", local), (b"PK\x01\x02", central)):
                at = raw.find(signature) + offset
                raw[at:at + 2] = struct.pack("<H", value)

        def damaged_data(raw: bytearray) -> None:
            at = raw.find(b"PK\x03\x04")
            name, extra = struct.unpack("<HH", raw[at + 26:at + 30])
            raw[at + 30 + name + extra:at + 34 + name + extra] = b"\xff\xff\xff\xff"

        reason = "a part cannot be read (unsupported compression, encryption or damaged data)"
        self.write(exports="done")
        self.exports()
        junk = b"\x09\x04\x05\x00" + b"\xff" * 40  # stored as it is, then declared to be compressed in another format
        cases = {
            "a compression method nobody supports": (lambda raw: field(raw, 8, 10, 99), {}),
            "an encrypted part": (lambda raw: field(raw, 6, 8, 1), {}),
            "a part whose data does not inflate": (damaged_data, {}),
            "a part in a format whose reader raises its own error (lzma)":
                (lambda raw: field(raw, 8, 10, 14), {"payload": junk, "method": zipfile.ZIP_STORED}),
            "a part in a format whose reader raises an OSError (bzip2)":
                (lambda raw: field(raw, 8, 10, 12), {"payload": junk, "method": zipfile.ZIP_STORED}),
        }
        for label, (change, options) in cases.items():
            with self.subTest(label):
                (self.dir / "sd-01-001.pptx").write_bytes(patched(change, **options))
                self.assertEqual(reason, slides.pptx_damage(self.dir / "sd-01-001.pptx"))
                self.assertEqual([f"sd-01-001.pptx is not a PowerPoint file: {reason}"], self.problems())

    def test_a_pptx_whose_parts_unpack_to_more_than_a_deck_can_hold_is_refused(self) -> None:
        import zipfile

        self.write(exports="done")
        self.exports()
        with zipfile.ZipFile(self.dir / "sd-01-001.pptx", "a") as archive:
            archive.writestr("ppt/media/big.bin", b"\x00" * 5000)
        with mock.patch.object(slides, "MAX_PPTX_BYTES", 4096):
            self.assertEqual(["sd-01-001.pptx is not a PowerPoint file: its parts add up to more than 0 MB unpacked"],
                             self.problems())
        self.assertEqual([], self.problems())

    def test_a_finished_deck_keeps_the_time_of_its_claim(self) -> None:
        record = {"id": "sd-01-001", "status": "done", "owner": "claude/a", "done_at": "2026-10-17T09:00:00Z",
                  "moda_canvas": CANVAS, "moda_url": URL, "slide_count": 8, "size": "1920x1080", "exports": "pending"}
        self.assertEqual(["claimed_at must look like 2026-10-17T11:00:00Z"], slides.record_problems(record, "sd-01-001"))

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

    def test_generation_and_taken_from_come_together_and_never_name_the_owner(self) -> None:
        base = {"id": "sd-01-001", "status": "doing", "owner": "claude/a", "claimed_at": "2026-10-17T09:00:00Z",
                "heartbeat_at": "2026-10-17T09:00:00Z"}
        self.assertEqual([], slides.record_problems({**base, "generation": 1, "taken_from": ["claude/b"]}, "sd-01-001"))
        self.assertTrue(any("come together" in problem for problem in slides.record_problems({**base, "generation": 99}, "sd-01-001")))
        self.assertTrue(any("come together" in problem for problem in slides.record_problems({**base, "taken_from": ["claude/b"]}, "sd-01-001")))
        self.assertTrue(any("not name the owner" in problem
                            for problem in slides.record_problems({**base, "generation": 1, "taken_from": ["claude/a"]}, "sd-01-001")))

    def test_a_key_named_twice_makes_the_record_unreadable(self) -> None:
        self.write()
        text = (self.dir / "deck.yaml").read_text(encoding="utf-8")
        (self.dir / "deck.yaml").write_text(text + "owner: claude/b\n", encoding="utf-8")
        self.assertEqual(["deck.yaml does not parse as a mapping"], self.problems())
        self.assertIsNone(slides.parse_record(text + "status: doing\n"))

    def test_the_record_is_required(self) -> None:
        self.assertEqual(["deck.yaml is missing"], self.problems())


if __name__ == "__main__":
    unittest.main()
