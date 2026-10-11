"""Regression tests for the Codex review of vohoailinh90/tool-marketing-studio#1 (REQ-MKT-002)."""

import os
import time
import unittest
import zipfile
from unittest import mock

import yaml

from mkt import ai, publish
from mkt.approvals import approve
from mkt.check import has_url
from mkt.model import ROOT, load_campaign
from mkt.publish import publish_facebook, smoke_facebook
from tests.support import FakeSession, cleanup, fake_render, make_root

ENV = {"FB_PAGE_ID": "555", "FB_PAGE_TOKEN": "EAAG-secret-page-token-123", "FB_GRAPH_VERSION": "v23.0"}
SAME_REPO = "github.event.pull_request.head.repo.full_name == github.repository"


class CiRunnerTests(unittest.TestCase):
    def test_pull_requests_from_forks_never_reach_the_self_hosted_runner(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
        for name, job in workflow["jobs"].items():
            guard = " ".join(str(job.get("if", "")).split())
            self.assertIn("github.event_name != 'pull_request'", guard, name)
            self.assertIn(SAME_REPO, guard, name)


class BareDomainTests(unittest.TestCase):
    def test_a_bare_domain_with_any_real_ending_is_a_link(self):
        for text in ("Vào example.ca nhé", "product.tech", "see tool.consulting.", "ｓｈｏｐ．ｊｐ"):
            self.assertTrue(has_url(text), text)

    def test_a_domain_glued_to_japanese_text_is_a_link(self):
        for text in ("詳細はexample.comへ", "公式サイトexample.com/a", "ツールexample.com"):
            self.assertTrue(has_url(text), text)

    def test_abbreviations_and_file_names_that_are_not_domains_pass(self):
        for text in ("TP.HCM", "TP.Huế", "Node.js", "v23.0", "e.g. Outlook", "Ph.D", "St.Louis"):
            self.assertFalse(has_url(text), text)

    def test_a_long_run_of_labels_is_checked_quickly(self):
        for text in ("a-" * 15000, "a." * 15000):
            started = time.monotonic()
            has_url(text)
            self.assertLess(time.monotonic() - started, 2.0, text[:4])


class InsightShapeTests(unittest.TestCase):
    def report(self, **changes):
        report = {"demand": {"level": "weak"}, "by_language": [{"lang": "vi", "signal": "weak"}],
                  "next_steps": [{"priority": 1, "action": "ask", "effort": "S"}]}
        report.update(changes)
        return report

    def test_a_scalar_where_a_list_belongs_is_refused(self):
        for section in ("by_language", "requests", "objections", "next_posts", "questions"):
            report = self.report(**{section: "unknown"})
            issues = ai.check_insights(report, [])
            self.assertTrue(any(i.level == "error" and section in i.message for i in issues), section)
            self.assertEqual(report[section], [])

    def test_items_the_page_cannot_show_are_dropped(self):
        report = self.report(by_language=["vi", {"lang": "ja", "signal": "weak"}], questions=[{"q": 1}, "Why?"])
        ai.check_insights(report, [])
        self.assertEqual(report["by_language"], [{"lang": "ja", "signal": "weak"}])
        self.assertEqual(report["questions"], ["Why?"])

    def test_a_demand_that_is_not_a_mapping_is_an_error_not_a_crash(self):
        issues = ai.check_insights(self.report(demand="strong"), [])
        self.assertTrue(any(i.level == "error" and "demand" in i.message for i in issues))


class NestedPostShapeTests(unittest.TestCase):
    def setUp(self):
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("fastapi/httpx not installed")
        from mkt.server import create_app
        self.root = make_root()
        dist = self.root / "dist"
        dist.mkdir()
        (dist / "index.html").write_text("<html><head></head></html>", encoding="utf-8")
        self.client = TestClient(create_app(self.root, port=8765, dist=dist, token="tok"), base_url="http://127.0.0.1:8765")
        self.path = self.root / "campaigns/demo/posts/vi/01-pain.yaml"

    def tearDown(self):
        cleanup(self.root)

    def test_a_shape_the_checker_cannot_read_is_reported_and_not_saved(self):
        before = self.path.read_text(encoding="utf-8")
        for text in ("id: 01-pain\nslides: [{layout: [cover]}]\n", "id: 01-pain\nformat: [square]\n",
                     "id: 01-pain\nlink: [survey]\n"):
            response = self.client.put("/api/campaigns/demo/posts/vi/01-pain", json={"yaml": text},
                                       headers={"X-Studio-Token": "tok"})
            self.assertEqual(response.status_code, 200, text)
            self.assertTrue(any(i["level"] == "error" for i in response.json()["issues"]), text)
        self.assertNotEqual(self.path.read_text(encoding="utf-8"), before)   # saved: a draft may have errors

    def test_a_crashing_check_leaves_the_file_as_it_was(self):
        before = self.path.read_text(encoding="utf-8")
        with mock.patch("mkt.server.check_post", side_effect=TypeError("unhashable type: 'list'")):
            response = self.client.put("/api/campaigns/demo/posts/vi/01-pain", json={"yaml": "id: 01-pain\n"},
                                       headers={"X-Studio-Token": "tok"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)


class UnlistedExportFileTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root(platforms={"facebook": {"caption": "Một dòng mở đầu", "hashtags": ["demo"]}})
        self.env = mock.patch.dict(os.environ, ENV)
        self.env.start()
        self.campaign = load_campaign(self.root, "demo")
        self.post = self.campaign.post("01-pain", "vi")
        fake_render(self.campaign, self.post)
        approve(self.campaign, self.post, {})
        self.out = self.campaign.export_dir(self.post)

    def tearDown(self):
        self.env.stop()
        cleanup(self.root)

    def test_a_text_file_added_after_rendering_stays_out_of_the_pack(self):
        (self.out / "facebook-extra.txt").write_text("not reviewed", encoding="utf-8")
        (self.out / "facebook-comment.txt").write_text("not reviewed", encoding="utf-8")
        with zipfile.ZipFile(publish.build_pack(self.campaign, self.post, "facebook", {})) as archive:
            self.assertEqual(sorted(archive.namelist()), ["01.png", "02.png", "facebook.txt"])

    def test_a_comment_file_added_after_rendering_is_not_posted(self):
        smoke_facebook(self.root, session=FakeSession([(200, {"id": "555", "name": "Demo Page"})]))
        (self.out / "facebook-comment.txt").write_text("not reviewed", encoding="utf-8")
        plan = publish_facebook(self.campaign, self.post, {}, confirm_page_name=None, dry_run=True)
        self.assertFalse(any("/comments" in step for step in plan["steps"]))


if __name__ == "__main__":
    unittest.main()
