"""scripts/hooks/office_events.py: the observer that feeds the agent-office dashboard.

The hook must only ever record. Every test that matters here is a claim about what it
refuses to do: break the session, block a tool, store a prompt, or lose a line.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = ROOT / "scripts" / "hooks" / "office_events.py"


def load_module(name: str, path: Path):
    """Load from source, never from the bytecode cache (see test_session_budget)."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


hook = load_module("office_events", HOOK_PATH)


def lines(root: Path, name: str = hook.EVENTS_NAME) -> list[dict]:
    path = root / "artifacts" / "handoff" / name
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class TempRoot(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.env = mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)
        for var in (hook.DISABLE_VAR, hook.SHAPE_VAR, hook.MAX_BYTES_VAR, hook.NOTES_VAR):
            os.environ.pop(var, None)

    def run_hook(self, command: str, payload: object) -> tuple[int, str, str]:
        stdin = io.StringIO(payload if isinstance(payload, str) else json.dumps(payload))
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdin", stdin), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = hook.main(["office_events.py", command])
        return code, out.getvalue(), err.getvalue()


class SpawnEventTests(TempRoot):
    def test_a_spawn_request_records_the_type_and_the_short_description_only(self) -> None:
        self.run_hook("pre-tool-use", {
            "session_id": "s1", "hook_event_name": "PreToolUse", "tool_name": "Agent", "tool_use_id": "toolu_1",
            "tool_input": {"subagent_type": "architecture-critic", "description": "Challenge the design",
                           "prompt": "SECRET-PROMPT-BODY"},
        })
        (event,) = lines(self.root)
        self.assertEqual((event["ev"], event["agent"], event["task"], event["tool_use_id"], event["session"]),
                         ("spawn_request", "architecture-critic", "Challenge the design", "toolu_1", "s1"))
        self.assertNotIn("SECRET-PROMPT-BODY", json.dumps(event))

    def test_the_legacy_task_tool_name_is_a_spawn_too(self) -> None:
        self.run_hook("pre-tool-use", {"tool_name": "Task", "tool_input": {"subagent_type": "architect"}})
        self.assertEqual([event["agent"] for event in lines(self.root)], ["architect"])

    def test_a_spawn_without_a_type_is_the_general_purpose_agent(self) -> None:
        self.run_hook("pre-tool-use", {"tool_name": "Agent", "tool_input": {"description": "look around"}})
        self.assertEqual(lines(self.root)[0]["agent"], "general-purpose")

    def test_other_tools_are_not_spawn_requests(self) -> None:
        self.run_hook("pre-tool-use", {"tool_name": "Bash", "tool_input": {"command": "ls"}})
        self.assertEqual(lines(self.root), [])

    def test_a_spawn_result_carries_the_agent_id_and_the_counts_the_dashboard_shows(self) -> None:
        self.run_hook("post-tool-use", {
            "tool_name": "Agent", "tool_use_id": "toolu_1", "tool_input": {"subagent_type": "code-reviewer"},
            "tool_response": {"status": "completed", "agentId": "agent-9", "totalTokens": 1200,
                              "totalDurationMs": 5400, "totalToolUseCount": 7, "content": "SECRET-REPLY"},
        })
        (event,) = lines(self.root)
        self.assertEqual((event["ev"], event["agent_id"], event["status"], event["tool_uses"], event["tokens"]),
                         ("spawn_result", "agent-9", "completed", 7, 1200))
        self.assertNotIn("SECRET-REPLY", json.dumps(event))

    def test_a_failed_spawn_records_the_error(self) -> None:
        self.run_hook("post-tool-use-failure", {
            "tool_name": "Agent", "tool_use_id": "toolu_2", "tool_input": {"subagent_type": "architect"}, "error": "boom",
        })
        (event,) = lines(self.root)
        self.assertEqual((event["ev"], event["error"], event["agent"]), ("spawn_failed", "boom", "architect"))

    def test_the_notes_switch_also_drops_the_error_text_of_a_failed_spawn(self) -> None:
        with mock.patch.dict(os.environ, {hook.NOTES_VAR: "0"}):
            self.run_hook("post-tool-use-failure", {
                "tool_name": "Agent", "tool_use_id": "toolu_2", "tool_input": {"subagent_type": "architect"},
                "error": "failed to read /home/someone/SECRET-PATH",
            })
        (event,) = lines(self.root)
        self.assertEqual((event["ev"], event["agent"]), ("spawn_failed", "architect"))
        self.assertNotIn("error", event)
        self.assertNotIn("SECRET-PATH", json.dumps(event))

    def test_a_failure_of_another_tool_is_not_recorded(self) -> None:
        self.run_hook("post-tool-use-failure", {"tool_name": "Bash", "error": "exit 1"})
        self.assertEqual(lines(self.root), [])


class LifecycleEventTests(TempRoot):
    def test_start_and_stop_carry_the_subagent_identity(self) -> None:
        self.run_hook("subagent-start", {"agent_id": "a1", "agent_type": "architect"})
        self.run_hook("subagent-stop", {"agent_id": "a1", "agent_type": "architect",
                                        "last_assistant_message": "All done.\n  Two findings.",
                                        "agent_transcript_path": "/home/someone/transcript.jsonl"})
        start, stop = lines(self.root)
        self.assertEqual((start["ev"], start["agent_id"], start["agent"]), ("start", "a1", "architect"))
        self.assertEqual((stop["ev"], stop["note"]), ("stop", "All done. Two findings."))
        self.assertNotIn("transcript", json.dumps(stop))

    def test_the_reply_excerpt_can_be_switched_off_and_nothing_else_changes(self) -> None:
        with mock.patch.dict(os.environ, {hook.NOTES_VAR: "0"}):
            self.run_hook("subagent-stop", {"agent_id": "a1", "agent_type": "architect", "last_assistant_message": "SECRET-REPLY"})
        (stop,) = lines(self.root)
        self.assertEqual((stop["ev"], stop["agent_id"]), ("stop", "a1"))
        self.assertNotIn("note", stop)
        self.assertNotIn("SECRET-REPLY", json.dumps(stop))

    def test_the_reply_excerpt_is_cut_to_the_documented_length(self) -> None:
        self.run_hook("subagent-stop", {"agent_id": "a1", "agent_type": "architect", "last_assistant_message": "x" * 2000})
        self.assertEqual(len(lines(self.root)[0]["note"]), hook.TEXT_LIMIT)

    def test_a_tool_call_inside_a_subagent_is_attributed_to_it(self) -> None:
        self.run_hook("post-tool-use", {"tool_name": "Read", "agent_id": "a1", "agent_type": "architect"})
        (event,) = lines(self.root)
        self.assertEqual((event["ev"], event["agent_id"], event["tool"]), ("tool", "a1", "Read"))

    def test_a_main_thread_tool_call_has_no_agent(self) -> None:
        self.run_hook("post-tool-use", {"tool_name": "Edit"})
        (event,) = lines(self.root)
        self.assertEqual(event["ev"], "tool")
        self.assertNotIn("agent_id", event)


class FailOpenTests(TempRoot):
    def assert_silent_success(self, result: tuple[int, str, str]) -> None:
        code, out, _ = result
        self.assertEqual(code, 0)
        self.assertEqual(out, "", "an observer must never print a decision to the harness")

    def test_garbage_on_stdin_is_ignored(self) -> None:
        self.assert_silent_success(self.run_hook("pre-tool-use", "not json {{{"))
        self.assert_silent_success(self.run_hook("pre-tool-use", "[1, 2]"))
        self.assert_silent_success(self.run_hook("pre-tool-use", ""))
        self.assertEqual(lines(self.root), [])

    def test_an_unknown_subcommand_does_nothing(self) -> None:
        self.assert_silent_success(self.run_hook("no-such-event", {"tool_name": "Agent"}))
        self.assertEqual(lines(self.root), [])

    def test_a_write_failure_is_swallowed(self) -> None:
        with mock.patch.object(hook, "append_line", side_effect=OSError("disk full")):
            result = self.run_hook("pre-tool-use", {"tool_name": "Agent", "tool_input": {"subagent_type": "architect"}})
        self.assert_silent_success(result)
        self.assertIn("continuing", result[2])

    def test_the_disable_switch_writes_nothing(self) -> None:
        with mock.patch.dict(os.environ, {hook.DISABLE_VAR: "1"}):
            self.assert_silent_success(self.run_hook("pre-tool-use", {"tool_name": "Agent", "tool_input": {}}))
        self.assertEqual(lines(self.root), [])


class StorageTests(TempRoot):
    def test_an_oversized_description_is_clipped_so_one_write_stays_whole(self) -> None:
        self.run_hook("pre-tool-use", {"tool_name": "Agent", "tool_use_id": "t" * 5000,
                                       "tool_input": {"subagent_type": "a" * 5000, "description": "word " * 5000}})
        raw = (self.root / "artifacts" / "handoff" / hook.EVENTS_NAME).read_bytes()
        self.assertLessEqual(len(raw), hook.MAX_LINE_BYTES + 1)
        self.assertEqual(raw.count(b"\n"), 1)
        json.loads(raw)

    def test_a_large_log_is_rotated_once_instead_of_growing_forever(self) -> None:
        directory = self.root / "artifacts" / "handoff"
        directory.mkdir(parents=True)
        (directory / hook.EVENTS_NAME).write_text("x" * 100, encoding="utf-8")
        with mock.patch.dict(os.environ, {hook.MAX_BYTES_VAR: "50"}):
            self.run_hook("post-tool-use", {"tool_name": "Edit"})
        self.assertEqual((directory / (hook.EVENTS_NAME + ".1")).read_text(encoding="utf-8"), "x" * 100)
        self.assertEqual(len(lines(self.root)), 1)

    def test_the_logs_are_readable_by_their_owner_only(self) -> None:
        with mock.patch.dict(os.environ, {hook.SHAPE_VAR: "1"}):
            self.run_hook("post-tool-use", {"tool_name": "Edit"})
        directory = self.root / "artifacts" / "handoff"
        for name in (hook.EVENTS_NAME, hook.SHAPES_NAME):
            self.assertEqual(stat.S_IMODE((directory / name).stat().st_mode) & 0o077, 0, name)

    @unittest.skipIf(hook.fcntl is None, "needs POSIX advisory locks")
    def test_a_rotation_already_under_way_is_not_repeated_by_a_second_hook(self) -> None:
        directory = self.root / "artifacts" / "handoff"
        directory.mkdir(parents=True)
        log = directory / hook.EVENTS_NAME
        log.write_text("x" * 100, encoding="utf-8")
        held = os.open(directory / (hook.EVENTS_NAME + ".lock"), os.O_CREAT | os.O_RDWR, 0o600)
        try:
            hook.fcntl.flock(held, hook.fcntl.LOCK_EX)
            with mock.patch.dict(os.environ, {hook.MAX_BYTES_VAR: "50"}):
                hook.rotate_if_large(log)
            self.assertFalse((directory / (hook.EVENTS_NAME + ".1")).exists(), "the lock holder is rotating; this hook must skip")
        finally:
            os.close(held)

    def test_a_second_rotation_never_replaces_the_kept_generation_with_a_small_file(self) -> None:
        directory = self.root / "artifacts" / "handoff"
        directory.mkdir(parents=True)
        log = directory / hook.EVENTS_NAME
        log.write_text("old history " * 10, encoding="utf-8")
        with mock.patch.dict(os.environ, {hook.MAX_BYTES_VAR: "50"}):
            hook.rotate_if_large(log)
            log.write_text("fresh", encoding="utf-8")
            hook.rotate_if_large(log)  # the stale size check of a slower hook: the file is small now
        self.assertEqual((directory / (hook.EVENTS_NAME + ".1")).read_text(encoding="utf-8"), "old history " * 10)
        self.assertEqual(log.read_text(encoding="utf-8"), "fresh")

    def test_the_shape_recorder_keeps_key_names_and_types_but_never_values(self) -> None:
        with mock.patch.dict(os.environ, {hook.SHAPE_VAR: "1"}):
            self.run_hook("post-tool-use", {
                "hook_event_name": "PostToolUse", "tool_name": "Agent",
                "tool_input": {"prompt": "TOP-SECRET-TEXT"},
                "tool_response": {"agentId": "agent-1", "totalToolUseCount": 3, "usage": {"input_tokens": 5}},
            })
        (shape,) = lines(self.root, hook.SHAPES_NAME)
        self.assertEqual(shape["shape"]["tool_response"],
                         {"agentId": "str", "totalToolUseCount": "int", "usage": {"input_tokens": "int"}})
        self.assertNotIn("TOP-SECRET-TEXT", json.dumps(shape))

    def test_concurrent_hooks_never_interleave_their_lines(self) -> None:
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(self.root)}
        payload = json.dumps({"tool_name": "Read", "agent_id": "a1", "agent_type": "architect"})
        procs = [subprocess.Popen([sys.executable, str(HOOK_PATH), "post-tool-use"], stdin=subprocess.PIPE, env=env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True) for _ in range(16)]
        for proc in procs:
            proc.communicate(payload)
        self.assertEqual([proc.returncode for proc in procs], [0] * 16)
        self.assertEqual(len(lines(self.root)), 16)  # every line parses and none was lost


class SettingsWiringTests(unittest.TestCase):
    """What settings.example.json asks of this hook is a contract a validator can assert."""

    settings = json.loads((ROOT / ".claude" / "settings.example.json").read_text(encoding="utf-8"))

    def entries(self, event: str) -> list[tuple[str | None, dict]]:
        return [(group.get("matcher"), entry) for group in self.settings["hooks"][event] for entry in group["hooks"]
                if "office_events.py" in entry["command"]]

    def test_the_spawn_matchers_name_exactly_the_spawn_tools(self) -> None:
        for event in ("PreToolUse", "PostToolUseFailure"):
            matchers = {matcher for matcher, _ in self.entries(event)}
            self.assertEqual(matchers, {"|".join(sorted(hook.SPAWN_TOOLS))}, event)

    def test_the_hook_that_sees_every_tool_call_never_waits_for_it(self) -> None:
        ((matcher, entry),) = self.entries("PostToolUse")
        self.assertEqual(matcher, "*")
        self.assertIs(entry.get("async"), True, "a hook on every tool call must run async or it adds latency to all of them")

    def test_each_registered_event_runs_the_subcommand_built_for_it(self) -> None:
        wanted = {"PreToolUse": "pre-tool-use", "PostToolUse": "post-tool-use", "PostToolUseFailure": "post-tool-use-failure",
                  "SubagentStart": "subagent-start", "SubagentStop": "subagent-stop"}
        for event, subcommand in wanted.items():
            commands = [entry["command"].rsplit(" ", 1)[-1] for _, entry in self.entries(event)]
            self.assertEqual(commands, [subcommand], event)
        self.assertEqual(set(wanted.values()), set(hook.EVENT_BUILDERS))


if __name__ == "__main__":
    unittest.main()
