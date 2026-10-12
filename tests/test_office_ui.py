"""office/: the page that draws the snapshot.

The page has no browser test in CI (the runner may have no browser), so what can be computed
is computed here: every message key the code or the data can ask for exists in all three
catalogs, and the one piece of non-trivial UI logic, where a handoff line runs, is run under Node.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICE = ROOT / "office"
SRC = OFFICE / "src"
LOCALES = SRC / "locales"
EDGES_CHECK = ROOT / "tests" / "web" / "office_edges_check.mts"
LANGUAGES = ("ja", "en", "vi")


def load_module(name: str, path: Path):
    """Load from source, never from the bytecode cache (see test_session_budget)."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


snapshot = load_module("office_snapshot", ROOT / "scripts" / "office" / "snapshot.py")
ROSTER = snapshot.load_roster()


def flat(tree: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in tree.items():
        path = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(flat(value, f"{path}."))
        else:
            out[path] = value
    return out


def catalog(language: str) -> dict[str, str]:
    return flat(json.loads((LOCALES / f"{language}.json").read_text(encoding="utf-8")))


def has(messages: dict[str, str], key: str) -> bool:
    """Plural keys (`key_one` / `key_other`) are asked for as `key`."""
    return key in messages or f"{key}_other" in messages


class CatalogCoverageTests(unittest.TestCase):
    def assert_everywhere(self, keys: set[str], what: str) -> None:
        for language in LANGUAGES:
            messages = catalog(language)
            missing = sorted(key for key in keys if not has(messages, key))
            self.assertEqual(missing, [], f"{language}: {what} has no message for {missing}")

    def test_every_literal_key_the_code_asks_for_is_in_every_catalog(self) -> None:
        keys: set[str] = set()
        for path in SRC.rglob("*.ts*"):
            text = path.read_text(encoding="utf-8")
            keys |= set(re.findall(r"""\bt\(\s*["']([A-Za-z0-9_.\-]+)["']""", text))
            keys |= set(re.findall(r"""tOr\(\s*t,\s*[`"'][^`"']*[`"'],\s*["']([A-Za-z0-9_.\-]+)["']""", text))
        self.assertGreater(len(keys), 40, "the scan found almost nothing: the pattern no longer matches the code")
        self.assert_everywhere(keys, "a key the code names")

    def test_every_state_tag_log_kind_and_phase_the_reducer_can_emit_has_a_message(self) -> None:
        keys = {f"state.{state}" for state in snapshot.STATES}
        keys |= {f"boss.state.{state}" for state in snapshot.STATES}
        keys |= {f"tag.{tag}" for tag in ("received", "handoff", "error")}
        keys |= {f"log.kind.{kind}" for kind in snapshot.LOG_KINDS}
        keys |= {f"phase.{step}" for step in (*snapshot.PHASES, *snapshot.TEAM_STAGES)}
        keys |= {f"mode.{mode}" for mode in snapshot.MODES}
        keys |= {f"boss.{mode}.{field}" for mode in snapshot.MODES for field in ("name", "role")}
        keys |= {f"budget.title.{mode}" for mode in snapshot.MODES} | {f"budget.none.{mode}" for mode in snapshot.MODES}
        keys |= {f"stats.{name}" for name in ("agents", "total", "running", "done", "blocked")}
        self.assert_everywhere(keys, "a reducer vocabulary")

    def test_every_lane_and_roster_agent_has_a_message_and_so_does_a_stranger(self) -> None:
        keys = {"lane.other", "roster.other.role"}
        for view in ("claude", "team"):
            keys |= {f"lane.{lane['id']}" for lane in ROSTER[view]["lanes"]}
            keys |= {f"roster.{name}.role" for name in ROSTER[view]["agents"]}
        self.assert_everywhere(keys, "a roster entry")

    def test_every_budget_slot_a_route_can_produce_has_a_label(self) -> None:
        policy = (ROOT / "agent-routing" / "policy.yaml").read_text(encoding="utf-8")
        reserves = set(re.findall(r"^  (\w+_reserve):", policy, re.MULTILINE))
        self.assertTrue({"analyst_reserve", "escalation_reserve"} <= reserves)
        self.assert_everywhere({"budget.slot.base"} | {f"budget.slot.{name}" for name in reserves}, "a budget slot")

    def test_the_catalogs_agree_on_placeholders_and_none_is_left_empty(self) -> None:
        vi, en, ja = (catalog(language) for language in LANGUAGES)
        self.assertEqual(set(vi), set(en))
        self.assertEqual(set(vi), set(ja))
        placeholder = re.compile(r"\{(\w+)\}")
        for key in vi:
            self.assertEqual(set(placeholder.findall(vi[key])), set(placeholder.findall(en[key])), key)
            self.assertEqual(set(placeholder.findall(vi[key])), set(placeholder.findall(ja[key])), key)
            for language, messages in zip(LANGUAGES, (ja, en, vi)):
                self.assertTrue(messages[key].strip(), f"{language}: {key} is empty")


class SourceHygieneTests(unittest.TestCase):
    def test_no_user_facing_english_hides_outside_the_catalogs(self) -> None:
        """The kit's components ship English defaults (a screen-reader label, say); none may survive."""
        for path in SRC.rglob("*.tsx"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn('>Close<', text, path.name)
            self.assertNotRegex(text, r"""aria-label=["'][A-Za-z]""", f"{path.name} has a literal aria-label")
            self.assertNotRegex(text, r"""sr-only">[A-Za-z]""", f"{path.name} has a literal screen-reader label")

    def test_a_button_holds_no_heading_or_block_content(self) -> None:
        """A heading inside a button is read out flat and is invalid HTML: the card is an article with one button."""
        pattern = re.compile(r"<button\b[^>]*>(?:(?!</button>).)*?<(?:h[1-6]|p|div|ul|ol|dl|section|article)\b", re.DOTALL)
        for path in (SRC / "components" / "office").rglob("*.tsx"):
            self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")), f"{path.name}: block content inside a <button>")

    def test_the_server_page_wiring_matches_the_api_it_calls(self) -> None:
        api = (SRC / "lib" / "api.ts").read_text(encoding="utf-8")
        self.assertIn("/api/snapshot", api)
        for demo in snapshot.demo_names():
            self.assertIn(demo, api, f"api.ts does not know the bundled demo {demo}")

    def test_dependencies_are_ignored_and_the_built_page_is_committed_like_web_dist(self) -> None:
        """CLAUDE.md: the built page is committed so users need no Node; CI rebuilds it and diffs."""
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("office/node_modules/", ignored)
        self.assertNotIn("office/dist", ignored)
        self.assertTrue((OFFICE / "dist" / "index.html").is_file(), "run `cd office && npm run build` and commit office/dist")

    def test_the_committed_build_cannot_feed_the_next_build_or_the_linter(self) -> None:
        """Tailwind scans every file it is not told to skip: without this the second build is larger than the first."""
        css = (SRC / "index.css").read_text(encoding="utf-8")
        self.assertIn('@source not "../dist";', css)
        self.assertIn('"ignorePatterns": ["dist"]', (OFFICE / ".oxlintrc.json").read_text(encoding="utf-8"))


@unittest.skipUnless(shutil.which("node"), "needs Node 22.6+ (TypeScript type stripping); CI installs it")
class EdgeGeometryTests(unittest.TestCase):
    def test_a_line_leaves_and_enters_the_cards_on_the_sides_that_face_each_other(self) -> None:
        result = subprocess.run(["node", "--experimental-strip-types", str(EDGES_CHECK)], capture_output=True, text=True,
                                cwd=ROOT, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("office edges: ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
