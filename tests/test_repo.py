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


if __name__ == "__main__":
    unittest.main()
