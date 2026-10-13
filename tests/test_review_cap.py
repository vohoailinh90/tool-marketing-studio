"""Reviews have no cap in the policy (docs/claude-to-codex.md section 16); the other round caps stay positive integers."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "agent-routing" / "policy.yaml"


def load_route():
    spec = importlib.util.spec_from_file_location("route_under_test", ROOT / "scripts" / "route.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ReviewCapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.route = load_route()
        self.policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        self.caps = self.policy["lanes"]["codex"]["round_caps"]

    def plan(self, caps):
        steps = [{"step": "implement", "mode": "IMPLEMENT"}, {"step": "review", "command": "review"},
                 {"step": "security-review", "command": "security review"}]
        return self.route.round_plan(steps, caps, "codex", "T2")

    def test_the_policy_sets_no_review_cap_but_keeps_the_task_caps(self) -> None:
        self.assertIsNone(self.caps["review"])
        self.assertEqual({k: self.caps[k] for k in ("BRAINSTORM", "IMPLEMENT", "FIX")},
                         {"BRAINSTORM": 2, "IMPLEMENT": 1, "FIX": 2})

    def test_a_null_review_cap_is_no_limit(self) -> None:
        plan = self.plan(self.caps)
        self.assertEqual(plan["review"], {"planned": 2, "cap": None})

    def test_a_numeric_review_cap_is_still_enforced(self) -> None:
        caps = copy.deepcopy(self.caps)
        caps["review"] = 1
        with self.assertRaisesRegex(self.route.RoutingError, "section 16 allows 1"):
            self.plan(caps)

    def test_nothing_else_may_be_null_or_nonsense(self) -> None:
        for mode, bad in (("review", 0), ("review", "x"), ("IMPLEMENT", None), ("FIX", 0)):
            caps = copy.deepcopy(self.caps)
            caps[mode] = bad
            with self.subTest(mode=mode, bad=bad), self.assertRaisesRegex(self.route.RoutingError, "positive integer"):
                self.plan(caps)


if __name__ == "__main__":
    unittest.main()
