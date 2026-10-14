"""The context window size: statusline.py records it, session_budget.py reads it.

Hook payloads do not carry the window's size, so session_budget.py once assumed 200K and told a 1M-context
session it was 86% full at 171K tokens. The status line payload does carry the size, so it leaves it in a file
of its own per session, which the hook reads first; then the CLAUDE_SESSION_BUDGET_CONTEXT_WINDOW variable; then
the 200K default. One file per session, because two status lines that read and rewrite one shared file lose each
other's entries.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "scripts" / "hooks"
ENV = "CLAUDE_SESSION_BUDGET_CONTEXT_WINDOW"


def load_module(name: str, path: Path) -> types.ModuleType:
    """Load from source, never from a bytecode cache (a mutated source must be what runs)."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


STATUSLINE = load_module("statusline_under_test", HOOKS / "statusline.py")
BUDGET = load_module("session_budget_under_test", HOOKS / "session_budget.py")


def payload(session: object = "s1", size: object = 1_000_000, **extra: object) -> dict:
    """The part of a status line payload these tests care about."""
    window = {"used_percentage": 15} if size is None else {"context_window_size": size, "used_percentage": 15}
    return {"session_id": session, "context_window": window, **extra}


class TempRoot(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.state = self.root.joinpath(*STATUSLINE.WINDOW_STATE)

    def recorded(self, session: str = "s1") -> str:
        return (self.state / session).read_text(encoding="utf-8")

    def sessions(self) -> list[str]:
        return sorted(path.name for path in self.state.iterdir()) if self.state.is_dir() else []

    def age(self, session: str, seconds: float) -> None:
        """Pretend this session's file was last written at that time (small numbers are long ago)."""
        os.utime(self.state / session, (seconds, seconds))


class StatuslineRecordsTheWindowTests(TempRoot):
    def test_the_size_is_recorded_for_the_session(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        self.assertEqual("1000000", self.recorded())

    def test_a_float_that_is_a_whole_number_is_accepted(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 200000.0), self.root)
        self.assertEqual("200000", self.recorded())

    def test_a_new_size_replaces_the_old_one_for_the_same_session(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 200_000), self.root)
        STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        self.assertEqual("1000000", self.recorded())

    def test_other_sessions_are_kept(self) -> None:
        STATUSLINE.record_window_size(payload("small", 200_000), self.root)
        STATUSLINE.record_window_size(payload("large", 1_000_000), self.root)
        self.assertEqual(["large", "small"], self.sessions())
        self.assertEqual(("200000", "1000000"), (self.recorded("small"), self.recorded("large")))

    def test_an_unchanged_size_is_not_rewritten_but_is_touched(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        self.age("s1", 1000)
        with mock.patch.object(os, "replace") as replace:
            STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        replace.assert_not_called()
        self.assertGreater((self.state / "s1").stat().st_mtime, 1_000_000)

    def test_the_file_is_put_in_place_whole_through_a_temporary_file(self) -> None:
        with mock.patch.object(os, "replace", wraps=os.replace) as replace:
            STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        replace.assert_called_once()
        source, target = replace.call_args.args
        self.assertEqual(self.state / "s1", Path(target))
        self.assertNotEqual(self.state / "s1", Path(source))
        self.assertEqual(["s1"], [name for name in os.listdir(self.state)])

    def test_a_failed_write_leaves_no_temporary_file_behind(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 200_000), self.root)
        with mock.patch.object(os, "replace", side_effect=OSError("disk full")), self.assertRaises(OSError):
            STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        self.assertEqual(["s1"], os.listdir(self.state))
        self.assertEqual("200000", self.recorded())

    def test_the_least_recently_drawn_sessions_are_forgotten_past_the_cap(self) -> None:
        cap = STATUSLINE.MAX_RECORDED_SESSIONS
        for number in range(cap + 8):
            STATUSLINE.record_window_size(payload(f"s{number}", 200_000), self.root)
            self.age(f"s{number}", number + 1)
        kept = self.sessions()
        self.assertEqual(cap, len(kept))
        self.assertIn(f"s{cap + 7}", kept)
        self.assertNotIn("s0", kept)

    def test_a_session_still_drawing_with_an_unchanged_size_outlives_newer_ones(self) -> None:
        cap = STATUSLINE.MAX_RECORDED_SESSIONS
        for number in range(cap):
            STATUSLINE.record_window_size(payload(f"s{number}", 1_000_000), self.root)
            self.age(f"s{number}", number + 1)
        STATUSLINE.record_window_size(payload("s0", 1_000_000), self.root)  # s0 draws again, the size unchanged
        STATUSLINE.record_window_size(payload("new", 1_000_000), self.root)  # a newer session appears
        self.assertIn("s0", self.sessions())
        self.assertNotIn("s1", self.sessions())

    def test_a_status_line_that_finds_a_file_gone_while_pruning_still_succeeds(self) -> None:
        cap = STATUSLINE.MAX_RECORDED_SESSIONS
        for number in range(cap):
            STATUSLINE.record_window_size(payload(f"s{number}", 200_000), self.root)
            self.age(f"s{number}", number + 1)
        original = Path.stat

        def vanishing(path: Path, *args: object, **kwargs: object):
            if path.name == "s0":
                raise FileNotFoundError(path)
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, "stat", vanishing):
            STATUSLINE.record_window_size(payload("new", 200_000), self.root)
        self.assertIn("new", self.sessions())

    def test_a_size_or_a_session_that_cannot_be_used_records_nothing(self) -> None:
        unusable = {
            "no size": payload("s1", None),
            "a boolean": payload("s1", True),
            "text": payload("s1", "1000000"),
            "not a number": payload("s1", float("nan")),
            "infinite": payload("s1", float("inf")),
            "zero": payload("s1", 0),
            "negative": payload("s1", -200_000),
            "too small": payload("s1", STATUSLINE.MIN_WINDOW_TOKENS - 1),
            "too large": payload("s1", STATUSLINE.MAX_WINDOW_TOKENS + 1),
            "a fraction": payload("s1", 1000.5),
            "no session": {"context_window": {"context_window_size": 1_000_000}},
            "empty session": payload("", 1_000_000),
            "a blank session": payload("  ", 1_000_000),
            "a numeric session": payload(7, 1_000_000),
            "a path as session": payload("../s1", 1_000_000),
            "a nested path as session": payload("a/b", 1_000_000),
            "a dotted session": payload("a.b", 1_000_000),
            "a hidden session": payload(".s1", 1_000_000),
            "a very long session": payload("s" * 129, 1_000_000),
            "window not an object": {"session_id": "s1", "context_window": 1_000_000},
            "no window": {"session_id": "s1"},
        }
        for name, body in unusable.items():
            with self.subTest(case=name), contextlib.redirect_stderr(io.StringIO()):
                STATUSLINE.record_window_size(body, self.root)
                self.assertFalse(self.state.exists())

    def test_a_file_that_is_not_a_size_is_replaced(self) -> None:
        self.state.mkdir(parents=True)
        for text in ("not a number", "", "12.5", "\x00"):
            with self.subTest(content=text):
                (self.state / "s1").write_text(text, encoding="utf-8")
                STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
                self.assertEqual("1000000", self.recorded())
        with self.subTest(content="bytes that are not text"):
            (self.state / "s1").write_bytes(b"\xff\xfe\xfa")
            STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
            self.assertEqual("1000000", self.recorded())

    def test_the_status_line_is_printed_even_when_the_file_cannot_be_written(self) -> None:
        blocker = self.root / "a-file"
        blocker.write_text("", encoding="utf-8")
        stdin = io.TextIOWrapper(io.BytesIO(json.dumps(payload("s1", 1_000_000)).encode()))
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(STATUSLINE, "project_root", return_value=blocker / "inside"), \
                mock.patch("sys.stdin", stdin), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = STATUSLINE.main()
        self.assertEqual(0, code)
        self.assertIn("ctx", out.getvalue())
        self.assertIn("could not record the window size", err.getvalue())

    def test_the_real_entry_point_records_what_it_is_given(self) -> None:
        stdin = io.TextIOWrapper(io.BytesIO(json.dumps(payload("s1", 1_000_000)).encode()))
        with mock.patch.object(STATUSLINE, "project_root", return_value=self.root), \
                mock.patch("sys.stdin", stdin), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, STATUSLINE.main())
        self.assertEqual("1000000", self.recorded())

    def test_the_project_directory_variable_picks_the_checkout(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.root)}):
            self.assertEqual(self.root, STATUSLINE.project_root())
        with mock.patch.dict(os.environ):
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
            self.assertEqual(ROOT, STATUSLINE.project_root())


class HookReadsTheWindowTests(TempRoot):
    def record(self, session: str, content: object) -> None:
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / session).write_text(str(content), encoding="utf-8")

    def window(self, body: dict | None, env: str | None = None) -> int:
        with mock.patch.dict(os.environ):
            os.environ.pop(ENV, None)
            if env is not None:
                os.environ[ENV] = env
            return BUDGET.context_window(body, self.root)

    def test_the_two_scripts_agree_on_where_and_how_much(self) -> None:
        self.assertEqual(STATUSLINE.WINDOW_STATE, BUDGET.WINDOW_STATE)
        self.assertEqual(STATUSLINE.SESSION_ID.pattern, BUDGET.SESSION_ID.pattern)
        self.assertEqual(STATUSLINE.MIN_WINDOW_TOKENS, BUDGET.MIN_WINDOW_TOKENS)
        self.assertEqual(STATUSLINE.MAX_WINDOW_TOKENS, BUDGET.MAX_WINDOW_TOKENS)

    def test_what_the_status_line_recorded_wins(self) -> None:
        self.record("s1", 1_000_000)
        self.assertEqual(1_000_000, self.window({"session_id": "s1"}, env="500000"))

    def test_a_trailing_newline_is_fine(self) -> None:
        self.record("s1", "1000000\n")
        self.assertEqual(1_000_000, self.window({"session_id": "s1"}))

    def test_the_environment_variable_comes_next(self) -> None:
        self.assertEqual(500_000, self.window({"session_id": "s1"}, env="500000"))
        self.record("other", 1_000_000)
        self.assertEqual(500_000, self.window({"session_id": "s1"}, env="500000"))

    def test_the_default_comes_last(self) -> None:
        self.assertEqual(200_000, self.window({"session_id": "s1"}))
        for env in ("", "many", "0", "-5"):
            with self.subTest(env=env):
                self.assertEqual(200_000, self.window({"session_id": "s1"}, env=env))

    def test_another_sessions_size_is_not_used(self) -> None:
        self.record("other", 1_000_000)
        self.assertEqual(200_000, self.window({"session_id": "s1"}))

    def test_a_call_without_a_payload_keeps_the_old_behaviour(self) -> None:
        self.record("s1", 1_000_000)
        self.assertEqual(200_000, self.window(None))
        self.assertEqual(500_000, self.window(None, env="500000"))
        self.assertEqual(200_000, self.window({}))

    def test_a_recording_that_cannot_be_used_is_ignored(self) -> None:
        bad = {
            "text": "many", "empty file": "", "a fraction": "12.5", "negative": "-5000", "an exponent": "1e6",
            "two numbers": "1000000 2000000", "zero": "0", "a binary mark": "\x00",
            "too small": str(BUDGET.MIN_WINDOW_TOKENS - 1), "too large": str(BUDGET.MAX_WINDOW_TOKENS + 1),
            "far too long": "9" * 40,
        }
        for name, content in bad.items():
            with self.subTest(content=name):
                self.record("s1", content)
                self.assertEqual(200_000, self.window({"session_id": "s1"}))
        with self.subTest(content="bytes that are not text"):
            (self.state / "s1").write_bytes(b"\xff\xfe\xfa")
            self.assertEqual(200_000, self.window({"session_id": "s1"}))

    def test_a_directory_where_the_file_should_be_is_ignored(self) -> None:
        (self.state / "s1").mkdir(parents=True)
        self.assertEqual(200_000, self.window({"session_id": "s1"}))

    def test_a_session_id_that_is_not_a_plain_name_reads_nothing(self) -> None:
        self.record("s1", 1_000_000)
        (self.state.parent / "outside").write_text("1000000", encoding="utf-8")
        for body in ({}, {"session_id": ""}, {"session_id": 7}, {"session_id": None}, {"session_id": "../outside"},
                     {"session_id": "context-window/s1"}, {"session_id": "s1/../s1"}, {"session_id": "s" * 129}):
            with self.subTest(body=body):
                self.assertEqual(200_000, self.window(body))

    def test_a_missing_state_directory_is_fine(self) -> None:
        self.assertFalse(self.state.exists())
        self.assertEqual(200_000, self.window({"session_id": "s1"}))


class SessionOfAMillionTokensIsNotToldItIsFullTests(TempRoot):
    """The failure that started this: 171,021 tokens read as 86% of 200K, but is 17% of 1M."""

    def setUp(self) -> None:
        super().setUp()
        self.transcript = self.root / "transcript.jsonl"
        usage = {"input_tokens": 3, "cache_read_input_tokens": 160_000, "cache_creation_input_tokens": 11_000,
                 "output_tokens": 18}
        self.transcript.write_text(json.dumps({"message": {"role": "assistant", "usage": usage}}) + "\n",
                                   encoding="utf-8")

    def record(self, size: int) -> None:
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "s1").write_text(str(size), encoding="utf-8")

    def nudge(self, recorded: int | None, env: str | None = None) -> str:
        if recorded is not None:
            self.record(recorded)
        body = {"session_id": "s1", "transcript_path": str(self.transcript)}
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.root)}):
            os.environ.pop(ENV, None)
            if env is not None:
                os.environ[ENV] = env
            with contextlib.redirect_stdout(out):
                self.assertEqual(0, BUDGET.cmd_pre_tool_use(body))
        return out.getvalue()

    def test_a_recorded_million_token_window_gives_no_nudge(self) -> None:
        self.assertEqual("", self.nudge(1_000_000))

    def test_with_no_record_the_old_default_still_nudges(self) -> None:
        self.assertIn("~86% full", self.nudge(None))

    def test_a_recorded_small_window_still_nudges(self) -> None:
        self.assertIn("~86% full", self.nudge(200_000, env="1000000"))

    def test_the_variable_still_covers_a_session_the_status_line_has_not_seen(self) -> None:
        self.assertEqual("", self.nudge(None, env="1000000"))

    def test_the_status_line_and_the_hook_meet_at_the_same_file(self) -> None:
        with mock.patch.object(STATUSLINE, "project_root", return_value=self.root):
            STATUSLINE.record_window_size(payload("s1", 1_000_000), STATUSLINE.project_root())
        self.assertEqual("", self.nudge(None))

    def test_the_handoff_records_the_window_it_was_measured_against(self) -> None:
        self.record(1_000_000)
        state = BUDGET.collect_state({"session_id": "s1", "transcript_path": str(self.transcript)}, "manual", self.root)
        self.assertEqual(1_000_000, state["context_window"])
        self.assertIn("171,021 / 1,000,000 tokens", BUDGET.render_auto_state(state))


if __name__ == "__main__":
    unittest.main()
