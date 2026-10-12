"""The hook wiring in .claude/settings.json is a contract a validator can assert.

A drifted subcommand name or matcher fails silently at runtime (the hook errors without
blocking, so nothing enforces and nothing says so), and no reviewer should be the check.
This repository ships its hooks enabled, so settings.json must stay the example the checks read.
"""

from __future__ import annotations

import json
import os
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / ".claude" / "settings.example.json"
ENABLED = ROOT / ".claude" / "settings.json"
HOOKS = ROOT / "scripts" / "hooks"

# script path -> (module name, the table of subcommands the script answers to)
HOOK_SCRIPTS = {
    "scripts/hooks/session_budget.py": ("session_budget", "HANDLERS"),
    "scripts/hooks/agent_budget.py": ("agent_budget", "HOOK_HANDLERS"),
    "scripts/hooks/office_events.py": ("office_events", "EVENT_BUILDERS"),
}


def load_module(name: str, path: Path):
    """Load from source, never from a bytecode cache."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


def example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


class SettingsContractTests(unittest.TestCase):
    def test_every_configured_hook_command_resolves_to_a_real_subcommand(self) -> None:
        handlers = {
            script: set(getattr(load_module(name, ROOT / script), table)) for script, (name, table) in HOOK_SCRIPTS.items()
        }
        configured = [
            (event, entry["command"])
            for event, groups in example()["hooks"].items()
            for group in groups
            for entry in group["hooks"]
        ]
        self.assertTrue(configured)
        for event, command in configured:
            with self.subTest(event=event, command=command):
                script = next((name for name in handlers if name in command), None)
                self.assertIsNotNone(script, f"{command!r} names no known hook script")
                self.assertIn(command.rsplit(" ", 1)[-1], handlers[script])

    def test_configured_events_and_matchers_match_the_documented_hook_contract(self) -> None:
        # None: the event takes no matcher (SubagentStart/SubagentStop match on agent type, and the
        # office observer wants every one).
        expected = {
            "PreToolUse": ["*", "Agent|Task"],
            "PostToolUse": ["*"],
            "PostToolUseFailure": ["Agent|Task"],
            "SubagentStart": [None],
            "SubagentStop": [None],
            "PreCompact": ["auto"],
            "StopFailure": ["rate_limit"],
            "SessionStart": ["startup|resume|compact"],
        }
        hooks = example()["hooks"]
        self.assertEqual(set(hooks), set(expected))
        for event, matchers in expected.items():
            with self.subTest(event=event):
                self.assertEqual([group.get("matcher") for group in hooks[event]], matchers)

    def test_referenced_scripts_exist_and_are_executable(self) -> None:
        self.assertIn("scripts/hooks/statusline.py", example()["statusLine"]["command"])
        for path in [ROOT / script for script in HOOK_SCRIPTS] + [HOOKS / "statusline.py"]:
            with self.subTest(script=path.name):
                self.assertTrue(path.is_file())
                self.assertTrue(os.access(path, os.X_OK))

    def test_the_observer_never_blocks_and_the_budget_hook_is_the_only_one_that_can_refuse(self) -> None:
        """Only agent_budget.py may print a decision; the observer and the session hooks never do."""
        for script in ("scripts/hooks/office_events.py", "scripts/hooks/session_budget.py"):
            text = (ROOT / script).read_text(encoding="utf-8")
            self.assertNotIn("permissionDecision", text, script)
        self.assertIn("permissionDecision", (HOOKS / "agent_budget.py").read_text(encoding="utf-8"))


class EnabledSettingsTests(unittest.TestCase):
    def test_the_enabled_settings_are_the_example_so_the_contract_above_covers_what_runs(self) -> None:
        if not ENABLED.is_file():
            self.skipTest("no .claude/settings.json here: the hooks are not enabled in this checkout")
        self.assertEqual(
            json.loads(ENABLED.read_text(encoding="utf-8")),
            example(),
            "settings.json drifted from settings.example.json: copy the example over it, or change both",
        )


if __name__ == "__main__":
    unittest.main()
