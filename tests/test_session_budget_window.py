"""The context window size: statusline.py records it, session_budget.py reads it.

Hook payloads do not carry the window's size, so session_budget.py once assumed 200K and told a 1M-context
session it was 86% full at 171K tokens. The status line payload does carry the size, so it leaves it in a file
the hook reads first; then the CLAUDE_SESSION_BUDGET_CONTEXT_WINDOW variable; then the 200K default.
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

    def recorded(self) -> object:
        return json.loads(self.state.read_text(encoding="utf-8"))


class StatuslineRecordsTheWindowTests(TempRoot):
    def test_the_size_is_recorded_for_the_session(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        self.assertEqual({"s1": 1_000_000}, self.recorded())

    def test_a_float_that_is_a_whole_number_is_accepted(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 200000.0), self.root)
        self.assertEqual({"s1": 200_000}, self.recorded())

    def test_a_new_size_replaces_the_old_one_for_the_same_session(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 200_000), self.root)
        STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        self.assertEqual({"s1": 1_000_000}, self.recorded())

    def test_other_sessions_are_kept(self) -> None:
        STATUSLINE.record_window_size(payload("small", 200_000), self.root)
        STATUSLINE.record_window_size(payload("large", 1_000_000), self.root)
        self.assertEqual({"small": 200_000, "large": 1_000_000}, self.recorded())

    def test_an_unchanged_size_does_not_rewrite_the_file(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        with mock.patch.object(os, "replace") as replace:
            STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        replace.assert_not_called()

    def test_the_file_is_put_in_place_whole_through_a_temporary_file(self) -> None:
        with mock.patch.object(os, "replace", wraps=os.replace) as replace:
            STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
        replace.assert_called_once()
        source, target = replace.call_args.args
        self.assertEqual(self.state, Path(target))
        self.assertNotEqual(self.state, Path(source))
        self.assertEqual([self.state.name], sorted(path.name for path in self.state.parent.iterdir()))

    def test_a_failed_write_leaves_no_temporary_file_behind(self) -> None:
        STATUSLINE.record_window_size(payload("s1", 200_000), self.root)
        with mock.patch.object(os, "replace", side_effect=OSError("disk full")), self.assertRaises(OSError):
            STATUSLINE.record_window_size(payload("s2", 1_000_000), self.root)
        self.assertEqual([self.state.name], sorted(path.name for path in self.state.parent.iterdir()))
        self.assertEqual({"s1": 200_000}, self.recorded())

    def test_the_oldest_sessions_are_dropped_past_the_cap(self) -> None:
        for number in range(STATUSLINE.MAX_RECORDED_SESSIONS + 8):
            STATUSLINE.record_window_size(payload(f"s{number}", 200_000), self.root)
        kept = list(self.recorded())
        self.assertEqual(STATUSLINE.MAX_RECORDED_SESSIONS, len(kept))
        self.assertEqual(f"s{STATUSLINE.MAX_RECORDED_SESSIONS + 7}", kept[-1])
        self.assertNotIn("s0", kept)

    def test_a_session_seen_again_becomes_the_newest(self) -> None:
        for name in ("a", "b", "c"):
            STATUSLINE.record_window_size(payload(name, 200_000), self.root)
        STATUSLINE.record_window_size(payload("a", 1_000_000), self.root)
        self.assertEqual(["b", "c", "a"], list(self.recorded()))

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
            "window not an object": {"session_id": "s1", "context_window": 1_000_000},
            "no window": {"session_id": "s1"},
        }
        for name, body in unusable.items():
            with self.subTest(case=name), contextlib.redirect_stderr(io.StringIO()):
                STATUSLINE.record_window_size(body, self.root)
                self.assertFalse(self.state.exists())

    def test_a_state_file_that_is_not_a_mapping_is_replaced(self) -> None:
        self.state.parent.mkdir(parents=True)
        for text in ("not json", "[1, 2]", "7", ""):
            with self.subTest(content=text):
                self.state.write_text(text, encoding="utf-8")
                STATUSLINE.record_window_size(payload("s1", 1_000_000), self.root)
                self.assertEqual({"s1": 1_000_000}, self.recorded())

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
        self.assertEqual({"s1": 1_000_000}, self.recorded())

    def test_the_project_directory_variable_picks_the_checkout(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.root)}):
            self.assertEqual(self.root, STATUSLINE.project_root())
        with mock.patch.dict(os.environ):
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
            self.assertEqual(ROOT, STATUSLINE.project_root())


class HookReadsTheWindowTests(TempRoot):
    def record(self, content: object) -> None:
        self.state.parent.mkdir(parents=True, exist_ok=True)
        self.state.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")

    def window(self, body: dict | None, env: str | None = None) -> int:
        with mock.patch.dict(os.environ):
            os.environ.pop(ENV, None)
            if env is not None:
                os.environ[ENV] = env
            return BUDGET.context_window(body, self.root)

    def test_the_two_scripts_agree_on_where_and_how_much(self) -> None:
        self.assertEqual(STATUSLINE.WINDOW_STATE, BUDGET.WINDOW_STATE)
        self.assertEqual(STATUSLINE.MIN_WINDOW_TOKENS, BUDGET.MIN_WINDOW_TOKENS)
        self.assertEqual(STATUSLINE.MAX_WINDOW_TOKENS, BUDGET.MAX_WINDOW_TOKENS)

    def test_what_the_status_line_recorded_wins(self) -> None:
        self.record({"s1": 1_000_000})
        self.assertEqual(1_000_000, self.window({"session_id": "s1"}, env="500000"))

    def test_the_environment_variable_comes_next(self) -> None:
        self.assertEqual(500_000, self.window({"session_id": "s1"}, env="500000"))
        self.record({"other": 1_000_000})
        self.assertEqual(500_000, self.window({"session_id": "s1"}, env="500000"))

    def test_the_default_comes_last(self) -> None:
        self.assertEqual(200_000, self.window({"session_id": "s1"}))
        for env in ("", "many", "0", "-5"):
            with self.subTest(env=env):
                self.assertEqual(200_000, self.window({"session_id": "s1"}, env=env))

    def test_another_sessions_size_is_not_used(self) -> None:
        self.record({"other": 1_000_000})
        self.assertEqual(200_000, self.window({"session_id": "s1"}))

    def test_a_call_without_a_payload_keeps_the_old_behaviour(self) -> None:
        self.record({"s1": 1_000_000})
        self.assertEqual(200_000, self.window(None))
        self.assertEqual(500_000, self.window(None, env="500000"))
        self.assertEqual(200_000, self.window({}))

    def test_a_recording_that_cannot_be_used_is_ignored(self) -> None:
        bad = {
            "not json": "not json", "a list": "[1]", "empty file": "",
            "a boolean": {"s1": True}, "text": {"s1": "1000000"}, "a float": {"s1": 1e6}, "zero": {"s1": 0},
            "too small": {"s1": BUDGET.MIN_WINDOW_TOKENS - 1}, "too large": {"s1": BUDGET.MAX_WINDOW_TOKENS + 1},
        }
        for name, content in bad.items():
            with self.subTest(content=name):
                self.record(content)
                self.assertEqual(200_000, self.window({"session_id": "s1"}))

    def test_a_payload_without_a_usable_session_id_reads_nothing(self) -> None:
        self.record({"": 1_000_000, "7": 1_000_000})
        for body in ({}, {"session_id": ""}, {"session_id": 7}, {"session_id": None}):
            with self.subTest(body=body):
                self.assertEqual(200_000, self.window(body))

    def test_a_missing_state_file_is_fine(self) -> None:
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

    def nudge(self, recorded: dict | None, env: str | None = None) -> str:
        if recorded is not None:
            self.state.parent.mkdir(parents=True, exist_ok=True)
            self.state.write_text(json.dumps(recorded), encoding="utf-8")
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
        self.assertEqual("", self.nudge({"s1": 1_000_000}))

    def test_with_no_record_the_old_default_still_nudges(self) -> None:
        self.assertIn("~86% full", self.nudge(None))

    def test_a_recorded_small_window_still_nudges(self) -> None:
        self.assertIn("~86% full", self.nudge({"s1": 200_000}, env="1000000"))

    def test_the_variable_still_covers_a_session_the_status_line_has_not_seen(self) -> None:
        self.assertEqual("", self.nudge(None, env="1000000"))

    def test_the_handoff_records_the_window_it_was_measured_against(self) -> None:
        self.state.parent.mkdir(parents=True, exist_ok=True)
        self.state.write_text(json.dumps({"s1": 1_000_000}), encoding="utf-8")
        state = BUDGET.collect_state({"session_id": "s1", "transcript_path": str(self.transcript)}, "manual", self.root)
        self.assertEqual(1_000_000, state["context_window"])
        self.assertIn("171,021 / 1,000,000 tokens", BUDGET.render_auto_state(state))


if __name__ == "__main__":
    unittest.main()
