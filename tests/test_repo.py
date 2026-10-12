import re
import shutil
import tempfile
import unittest
from pathlib import Path

from mkt.check import check_campaign
from mkt.model import ROOT, campaign_slugs, load_campaign
from mkt.scaffold import ScaffoldError, new_tool


class RepoTests(unittest.TestCase):
    def test_every_campaign_in_the_repo_has_no_errors(self):
        for slug in campaign_slugs(ROOT):
            errors = [str(i) for i in check_campaign(load_campaign(ROOT, slug)) if i.level == "error"]
            self.assertEqual(errors, [], slug)

    def test_scaffold_makes_a_campaign_that_loads_and_checks(self):
        root = Path(tempfile.mkdtemp())
        try:
            for part in ("tools/_template", "campaigns/_template"):
                shutil.copytree(ROOT / part, root / part)
            new_tool(root, "new-tool", "New Tool", "me/new-tool")
            campaign = load_campaign(root, "new-tool")
            self.assertEqual([i for i in check_campaign(campaign) if i.level == "error"], [])
            with self.assertRaises(ScaffoldError):
                new_tool(root, "new-tool", "Again")
            with self.assertRaises(ScaffoldError):
                new_tool(root, "../evil", "Evil")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_the_verification_commands_in_claude_md_run_top_to_bottom_from_the_root(self):
        """A bare `cd` leaves every later line in the wrong directory (`python3 scripts/...` then fails)."""
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        block = re.search(r"## Verification commands\s+```bash\n(.*?)```", text, re.DOTALL)
        self.assertIsNotNone(block, "the Verification commands block moved: update this test")
        commands = [command for command in (re.sub(r"\s+#.*$", "", line).strip() for line in block.group(1).splitlines()) if command]
        self.assertGreaterEqual(len(commands), 6)
        for command in commands:
            if re.search(r"(^|[;&|(]\s*)cd\s", command):
                self.assertTrue(command.startswith("(") and command.endswith(")"), f"{command!r}: wrap the cd in a subshell")

    def test_ui_catalogs_agree(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("i18n_check", ROOT / "scripts" / "i18n_check.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.problems(), [])
        broken = Path(tempfile.mkdtemp())
        (broken / "vi.json").write_text('{"a": "{n} bài"}', encoding="utf-8")
        (broken / "ja.json").write_text('{"a": "投稿"}', encoding="utf-8")
        (broken / "en.json").write_text('{"a": "{n} posts", "b": "x"}', encoding="utf-8")
        found = module.problems(broken)
        self.assertTrue(any("placeholders" in p for p in found))
        self.assertTrue(any("missing key 'b'" in p for p in found))

    def test_ui_catalog_check_reads_nested_catalogs_and_the_agent_office_ones(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("i18n_check", ROOT / "scripts" / "i18n_check.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.problems(module.OFFICE_LOCALES), [])
        self.assertEqual(module.flatten({"a": {"b": "x", "c": {"d": "y"}}, "e": "z"}), {"a.b": "x", "a.c.d": "y", "e": "z"})
        broken = Path(tempfile.mkdtemp())
        (broken / "vi.json").write_text('{"g": {"a": "{n} bài", "b": "x"}}', encoding="utf-8")
        (broken / "ja.json").write_text('{"g": {"a": "{n} 件"}}', encoding="utf-8")
        (broken / "en.json").write_text('{"g": {"a": "posts", "b": ""}}', encoding="utf-8")
        found = module.problems(broken)
        self.assertTrue(any("missing key 'g.b'" in p for p in found), found)
        self.assertTrue(any("'g.b' is empty" in p for p in found), found)
        self.assertTrue(any("'g.a' has placeholders" in p for p in found), found)

    def test_ui_catalog_check_reports_what_it_cannot_read_as_messages(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("i18n_check", ROOT / "scripts" / "i18n_check.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaises(KeyError):
            module.flatten({"c.d": "x", "c": {"d": "y"}})  # two paths, one name: never silently overwritten
        self.assertEqual(module.flatten({"g": {}}), {"g": {}})  # an empty object stays visible
        directory = Path(tempfile.mkdtemp())
        (directory / "vi.json").write_text('{"c.d": "x", "c": {"d": "y"}, "n": 3, "e": {}, "l": ["a"]}', encoding="utf-8")
        (directory / "ja.json").write_text('[]', encoding="utf-8")
        (directory / "en.json").write_text('{"n": 3}', encoding="utf-8")
        found = module.problems(directory)
        self.assertTrue(any("vi.json" in p and "defined twice" in p and "'c.d'" in p for p in found), found)
        self.assertTrue(any("ja.json: must be a JSON object" in p for p in found), found)
        (directory / "vi.json").write_text('{"n": 3, "e": {}, "l": ["a"], "b": "  "}', encoding="utf-8")
        (directory / "ja.json").write_text('{"n": 3, "e": {}, "l": ["a"], "b": "x"}', encoding="utf-8")
        (directory / "en.json").write_text('{"n": 3, "e": {}, "l": ["a"], "b": "x"}', encoding="utf-8")
        found = module.problems(directory)
        for key in ("n", "e", "l"):  # a non-string value keeps the established message, flat or nested
            self.assertTrue(any(f"vi.json: '{key}' is empty" in p for p in found), (key, found))
        self.assertFalse(any("is not a message" in p for p in found), found)
        self.assertTrue(any("'b' is empty" in p for p in found), found)


if __name__ == "__main__":
    unittest.main()
