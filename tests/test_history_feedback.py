import os
import unittest
from unittest import mock

from mkt import feedback, history
from mkt.model import load_campaign
from mkt.publish import PublishError, update_ledger
from tests.support import FakeSession, cleanup, make_root


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root()
        self.campaign = load_campaign(self.root, "demo")
        self.post = self.campaign.post("01-pain", "vi")

    def tearDown(self):
        cleanup(self.root)

    def test_several_manual_postings_are_all_kept(self):
        history.mark_posted(self.campaign, self.post, "facebook", url="https://fb.example/1", where="Group A",
                            when="2026-10-12 20:30")
        history.mark_posted(self.campaign, self.post, "facebook", url="https://fb.example/2", where="Group B")
        rows = history.rows(self.root)
        self.assertEqual(sorted(r["where"] for r in rows), ["Group A", "Group B"])
        self.assertEqual({r["tool_name"] for r in rows}, {"Demo Tool"})
        with self.assertRaises(PublishError):
            history.mark_posted(self.campaign, self.post, "facebook", url="https://fb.example/1")

    def test_bad_input_is_refused(self):
        with self.assertRaises(PublishError):
            history.mark_posted(self.campaign, self.post, "myspace")
        with self.assertRaises(PublishError):
            history.mark_posted(self.campaign, self.post, "facebook", url="javascript:alert(1)")
        with self.assertRaises(PublishError):
            history.mark_posted(self.campaign, self.post, "facebook", when="next tuesday")

    def test_pasted_comments_are_split_and_deduplicated(self):
        feedback.add_manual(self.campaign, "01-pain", "vi", "facebook", "Hay quá\n\nCó bản Mac không?")
        data = feedback.add_manual(self.campaign, "01-pain", "vi", "facebook", "Có bản Mac không?\n\nCần cho công ty",
                                   totals={"reactions": "12"})
        self.assertEqual([c["text"] for c in data["comments"]], ["Hay quá", "Có bản Mac không?", "Cần cho công ty"])
        self.assertEqual(data["totals"]["reactions"], 12)

    def test_scan_reads_comments_of_an_api_post(self):
        update_ledger(self.campaign, "01-pain/vi/facebook", state="done", remote_id="555_77")
        session = FakeSession([
            (200, {"reactions": {"summary": {"total_count": 9}}, "comments": {"summary": {"total_count": 2}},
                   "shares": {"count": 1}}),
            (200, {"data": [{"id": "c1", "message": "Want it", "created_time": "t", "like_count": 3},
                            {"id": "c2", "message": "Mac?", "created_time": "t", "like_count": 0}], "paging": {}}),
        ])
        with mock.patch.dict(os.environ, {"FB_PAGE_ID": "555", "FB_PAGE_TOKEN": "tok-123456"}):
            data = feedback.scan_facebook(self.campaign, "01-pain", "vi", session=session)
        self.assertEqual(data["totals"], {"reactions": 9, "comments": 2, "shares": 1})
        self.assertEqual(len(data["comments"]), 2)
        self.assertNotIn("from", session.calls[1]["params"]["fields"])

    def test_scan_needs_an_api_post(self):
        with self.assertRaises(PublishError):
            feedback.scan_facebook(self.campaign, "01-pain", "vi", session=FakeSession([]))


if __name__ == "__main__":
    unittest.main()
