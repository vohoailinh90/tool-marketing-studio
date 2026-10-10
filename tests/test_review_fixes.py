"""Regression tests for the independent review of REQ-MKT-001 (H1–H4, M1–M6)."""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from mkt import ai, publish
from mkt.approvals import approval_state, approve
from mkt.check import check_post, has_url
from mkt.layouts import FIELDS, LAYOUTS, Ctx, render_body
from mkt.model import ROOT, load_campaign
from mkt.page import build_page
from mkt.publish import PublishError, UnknownOutcome, load_ledger, publish_facebook, smoke_facebook
from tests.support import FakeSession, cleanup, fake_render, make_root, post_data, write_yaml

PAYLOAD = '"><iframe src="file:///etc/passwd"></iframe><x a="'
TOKEN = "EAAG-secret-page-token-123"
ENV = {"FB_PAGE_ID": "555", "FB_PAGE_TOKEN": TOKEN, "FB_GRAPH_VERSION": "v23.0"}

# One slide per layout with every field it reads, every string set to the payload.
SAMPLES = {
    "cover": {}, "quote": {}, "stat": {},
    "pains": {"items": [{"emoji": PAYLOAD, "text": PAYLOAD}]},
    "checklist": {"items": [PAYLOAD]},
    "chat": {"messages": [{"from": PAYLOAD, "text": PAYLOAD, "initial": PAYLOAD}, {"me": True, "text": PAYLOAD}]},
    "flow": {"steps": [{"text": PAYLOAD, "emoji": PAYLOAD, "minutes": 5}]},
    "compare": {"before": {"label": PAYLOAD, "items": [PAYLOAD]}, "after": {"label": PAYLOAD, "items": [PAYLOAD]}},
    "table": {"columns": [PAYLOAD], "rows": [[PAYLOAD, {"text": PAYLOAD, "tone": PAYLOAD}]], "total_row": True},
    "features": {"items": [{"emoji": PAYLOAD, "title": PAYLOAD, "text": PAYLOAD}]},
    "poll": {"options": [PAYLOAD]},
    "cta": {"show_link": True},
    "email": {"buttons": [PAYLOAD]},
    "timeline": {"items": [{"when": PAYLOAD, "text": PAYLOAD}]},
}


class EscapingTests(unittest.TestCase):
    def test_no_field_of_any_layout_can_open_a_tag(self):
        for name in LAYOUTS:
            if name == "image":
                continue
            slide = {"layout": name, **{key: PAYLOAD for key in FIELDS[name]}, **SAMPLES[name]}
            html = render_body(slide, Ctx(lang="vi", campaign_dir=Path(".")))
            self.assertNotIn("<iframe", html, name)
            self.assertNotIn("<x ", html, name)

    def test_enumerations_must_be_known_values(self):
        root = make_root(slides=[{"layout": "pains", "title": "t", "items": ["a"], "tone": PAYLOAD},
                                 {"layout": "cover", "title": "t", "colour": "red"}])
        try:
            campaign = load_campaign(root, "demo")
            messages = [i.message for i in check_post(campaign, campaign.post("01-pain", "vi")) if i.level == "error"]
            self.assertTrue(any("'tone' must be one of" in m for m in messages))
            self.assertTrue(any("has no field 'colour'" in m for m in messages))
        finally:
            cleanup(root)

    def test_the_page_forbids_frames_and_foreign_scripts(self):
        html = build_page({"layout": "cover", "title": "t"}, Ctx(lang="vi", campaign_dir=Path(".")),
                          brand={}, tool_name="T", series="", handle="", index=1, total=1, fmt_name="portrait")
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("default-src 'none'", html)
        self.assertNotIn("unsafe-inline' 'unsafe-eval", html)


class LinkTests(unittest.TestCase):
    def test_links_in_any_spelling_are_found(self):
        for text in ("evil.example/x", "bit.ly/abc", "hxxps://a.b", "https ://a.b", "https：//a.b", "ｈｔｔｐｓ://a.b",
                     "Vào evil.vn ngay", "www.x.y"):
            self.assertTrue(has_url(text), text)
        for text in ("Outlook", "3.5 giờ", "Node.js", "1/2 người", "v23.0", "SQLite"):
            self.assertFalse(has_url(text), text)

    def test_link_placeholder_only_where_a_link_belongs(self):
        root = make_root(platforms={"facebook": {"caption": "Xem {link}", "first_comment": "ok {link}"}})
        try:
            campaign = load_campaign(root, "demo")
            messages = [i.message for i in check_post(campaign, campaign.post("01-pain", "vi"))]
            self.assertTrue(any("facebook.caption" in m for m in messages))
            self.assertFalse(any("first_comment" in m for m in messages))
        finally:
            cleanup(root)


class PublishOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root()
        self.env = mock.patch.dict(os.environ, ENV)
        self.env.start()
        campaign = load_campaign(self.root, "demo")
        post = campaign.post("01-pain", "vi")
        fake_render(campaign, post)
        approve(campaign, post, {})
        smoke_facebook(self.root, session=FakeSession([(200, {"id": "555", "name": "Demo Page"})]))

    def tearDown(self):
        self.env.stop()
        cleanup(self.root)

    def campaign_and_post(self):
        campaign = load_campaign(self.root, "demo")
        return campaign, campaign.post("01-pain", "vi")

    def test_a_feed_5xx_stays_pending_and_blocks(self):
        campaign, post = self.campaign_and_post()
        session = FakeSession([(200, {"id": "p1"}), (200, {"id": "p2"}), (502, {})])
        with self.assertRaises(UnknownOutcome):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=session)
        self.assertEqual(load_ledger(campaign)["01-pain/vi/facebook"]["state"], "pending")
        self.assertTrue(any("may have posted" in r for r in publish.preconditions(campaign, post, "facebook", {})))

    def test_a_transient_graph_error_stays_pending(self):
        campaign, post = self.campaign_and_post()
        session = FakeSession([(200, {"id": "p1"}), (200, {"id": "p2"}), (400, {"error": {"code": 2, "message": "x"}})])
        with self.assertRaises(UnknownOutcome):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=session)
        self.assertEqual(load_ledger(campaign)["01-pain/vi/facebook"]["state"], "pending")

    def test_a_post_sent_back_to_draft_cannot_be_published(self):
        campaign, post = self.campaign_and_post()
        text = post.path.read_text(encoding="utf-8").replace("status: ready", "status: draft")
        post.path.write_text(text, encoding="utf-8")
        campaign, post = self.campaign_and_post()
        self.assertFalse(approval_state(campaign, post, {})[0])
        self.assertTrue(any("only a ready post" in r for r in publish.preconditions(campaign, post, "facebook", {})))

    def test_a_tampered_export_is_refused(self):
        campaign, post = self.campaign_and_post()
        (campaign.export_dir(post) / "facebook.txt").write_text("changed by hand", encoding="utf-8")
        self.assertTrue(any("changed after rendering" in r for r in publish.preconditions(campaign, post, "facebook", {})))
        with self.assertRaises(PublishError):
            publish.build_pack(campaign, post, "facebook", {})

    def test_a_page_without_a_name_fails_the_smoke_check(self):
        with self.assertRaises(PublishError):
            smoke_facebook(self.root, session=FakeSession([(200, {"id": "555", "name": ""})]))


class InsightRobustnessTests(unittest.TestCase):
    def test_short_quotes_and_bad_counts_are_cleaned(self):
        report = {"demand": {"level": "weak"}, "by_language": [{"lang": "vi", "signal": "huge"}],
                  "requests": [{"need": "x", "mentions": "lots", "quotes": ["a", "I want a feature for Mac"]}],
                  "next_steps": [{"priority": "1", "action": "a", "effort": "XL"}, {"priority": 2, "action": "b"}]}
        feedback = [{"comments": [{"text": "I  want a feature for Mac please"}]}]
        ai.check_insights(report, feedback)
        self.assertEqual(report["requests"][0]["quotes"], ["I want a feature for Mac"])
        self.assertEqual(report["requests"][0]["mentions"], 0)
        self.assertEqual(report["by_language"][0]["signal"], "unclear")
        self.assertEqual([s["priority"] for s in report["next_steps"]], [1, 2])

    def test_mixed_priorities_render_and_save_both_files(self):
        root = make_root()
        try:
            campaign = load_campaign(root, "demo")
            report = {"demand": {"level": "weak"}, "next_steps": [{"priority": "x", "action": "a"}, {"priority": 2}]}
            ai.check_insights(report, [])
            data_path, text_path = ai.save_insights(campaign, "vi", report, day="2026-10-12")
            self.assertTrue(data_path.exists() and text_path.exists())
        finally:
            cleanup(root)


class ScaffoldNameTests(unittest.TestCase):
    def test_any_tool_name_scaffolds_a_loadable_campaign(self):
        from mkt.scaffold import new_tool
        root = Path(tempfile.mkdtemp())
        try:
            for part in ("tools/_template", "campaigns/_template"):
                shutil.copytree(ROOT / part, root / part)
            new_tool(root, "odd-name", 'Back\\slash "Quote": Tool\nNext', "me/x")
            campaign = load_campaign(root, "odd-name")
            self.assertEqual(campaign.tool_name, 'Back\\slash "Quote": Tool Next')
        finally:
            shutil.rmtree(root, ignore_errors=True)


class ServerInputTests(unittest.TestCase):
    def setUp(self):
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("fastapi/httpx not installed")
        from mkt.server import create_app
        self.root = make_root()
        dist = Path(tempfile.mkdtemp())
        (dist / "index.html").write_text("<html><head></head></html>", encoding="utf-8")
        self.client = TestClient(create_app(self.root, port=8765, dist=dist, token="tok"), base_url="http://127.0.0.1:8765")
        self.headers = {"X-Studio-Token": "tok"}

    def tearDown(self):
        cleanup(self.root)

    def test_only_an_explicit_false_sends_for_real(self):
        with mock.patch("mkt.server.publish_facebook", return_value={"dry_run": True, "steps": []}) as call:
            for body in ({}, {"dry_run": None}, {"dry_run": 0}, {"dry_run": "no"}):
                self.client.post("/api/campaigns/demo/posts/vi/01-pain/publish/facebook", json=body, headers=self.headers)
                self.assertTrue(call.call_args.kwargs["dry_run"], body)
            self.client.post("/api/campaigns/demo/posts/vi/01-pain/publish/facebook", json={"dry_run": False},
                             headers=self.headers)
            self.assertFalse(call.call_args.kwargs["dry_run"])

    def test_a_broken_post_shape_is_not_saved(self):
        path = "/api/campaigns/demo/posts/vi/01-pain"
        before = (self.root / "campaigns/demo/posts/vi/01-pain.yaml").read_text(encoding="utf-8")
        response = self.client.put(path, json={"yaml": "id: 01-pain\nplatforms: [a, b]\n"}, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual((self.root / "campaigns/demo/posts/vi/01-pain.yaml").read_text(encoding="utf-8"), before)

    def test_odd_input_types_are_client_errors_not_crashes(self):
        response = self.client.post("/api/campaigns/demo/posts/vi/01-pain/feedback", headers=self.headers,
                                    json={"platform": "facebook", "text": "hi", "totals": ["x"]})
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/api/campaigns/demo/ai/prompt", headers=self.headers,
                                    json={"kind": "post", "slot": "01-pain", "langs": "vi"})
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
