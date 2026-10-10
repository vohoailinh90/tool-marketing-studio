import os
import unittest
from pathlib import Path
from unittest import mock

from mkt import publish
from mkt.approvals import ApprovalError, approval_state, approve
from mkt.model import load_campaign
from mkt.publish import PublishError, UnknownOutcome, load_ledger, publish_facebook, smoke_facebook
from tests.support import FakeSession, cleanup, fake_render, make_root, post_data, write_yaml

TOKEN = "EAAG-secret-page-token-123"
ENV = {"FB_PAGE_ID": "555", "FB_PAGE_TOKEN": TOKEN, "FB_GRAPH_VERSION": "v23.0"}


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root()
        self.env = mock.patch.dict(os.environ, ENV)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        cleanup(self.root)

    def campaign_and_post(self):
        campaign = load_campaign(self.root, "demo")
        return campaign, campaign.post("01-pain", "vi")

    def approved(self):
        campaign, post = self.campaign_and_post()
        fake_render(campaign, post)
        approve(campaign, post, {})
        return self.campaign_and_post()

    def smoke(self):
        smoke_facebook(self.root, session=FakeSession([(200, {"id": "555", "name": "Demo Page"})]))

    # ----------------------------------------------------------- approval

    def test_a_draft_cannot_be_approved(self):
        write_yaml(self.root / "campaigns/demo/posts/vi/01-pain.yaml", post_data(status="draft"))
        campaign, post = self.campaign_and_post()
        fake_render(campaign, post)
        with self.assertRaises(ApprovalError):
            approve(campaign, post, {})

    def test_stale_images_cannot_be_approved(self):
        campaign, post = self.campaign_and_post()
        fake_render(campaign, post)
        write_yaml(post.path, post_data(series="changed after render"))
        campaign, post = self.campaign_and_post()
        with self.assertRaises(ApprovalError):
            approve(campaign, post, {})

    def test_edit_voids_approval(self):
        campaign, post = self.approved()
        self.assertTrue(approval_state(campaign, post, {})[0])
        write_yaml(post.path, post_data(series="edited"))
        campaign, post = self.campaign_and_post()
        self.assertFalse(approval_state(campaign, post, {})[0])

    # ----------------------------------------------------------- publishing

    def test_dry_run_sends_nothing(self):
        campaign, post = self.approved()
        session = FakeSession([])
        result = publish_facebook(campaign, post, {}, confirm_page_name=None, dry_run=True, session=session)
        self.assertTrue(result["dry_run"])
        self.assertEqual(session.calls, [])
        self.assertEqual(load_ledger(campaign), {})

    def test_unapproved_post_is_refused(self):
        campaign, post = self.campaign_and_post()
        fake_render(campaign, post)
        with self.assertRaises(PublishError):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=True, session=FakeSession([]))

    def test_real_send_requires_smoke(self):
        campaign, post = self.approved()
        with self.assertRaisesRegex(PublishError, "smoke"):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=FakeSession([]))

    def test_real_send_requires_the_page_name(self):
        campaign, post = self.approved()
        self.smoke()
        with self.assertRaisesRegex(PublishError, "Page name"):
            publish_facebook(campaign, post, {}, confirm_page_name="Other", dry_run=False, session=FakeSession([]))

    def test_smoke_refuses_a_token_for_another_page(self):
        with self.assertRaises(PublishError):
            smoke_facebook(self.root, session=FakeSession([(200, {"id": "999", "name": "Someone else"})]))

    def test_publish_records_done_and_keeps_the_token_out_of_urls(self):
        campaign, post = self.approved()
        self.smoke()
        session = FakeSession([(200, {"id": "p1"}), (200, {"id": "p2"}), (200, {"id": "555_77"}), (200, {"id": "c1"})])
        row = publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=session)
        self.assertEqual(row["state"], "done")
        self.assertEqual(row["steps"]["photos"], ["p1", "p2"])
        self.assertEqual(row["steps"]["comment"], "c1")
        self.assertIn('"media_fbid": "p2"', session.calls[2]["data"]["attached_media[1]"])
        for call in session.calls:
            self.assertNotIn(TOKEN, call["url"])
            self.assertEqual(call["headers"]["Authorization"], f"Bearer {TOKEN}")
        with self.assertRaisesRegex(PublishError, "already published"):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=FakeSession([]))

    def test_feed_network_error_stays_pending_and_blocks(self):
        campaign, post = self.approved()
        self.smoke()
        session = FakeSession([(200, {"id": "p1"}), (200, {"id": "p2"}), ConnectionError("reset")])
        with self.assertRaises(UnknownOutcome):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=session)
        self.assertEqual(load_ledger(campaign)["01-pain/vi/facebook"]["state"], "pending")
        with self.assertRaisesRegex(PublishError, "may have posted"):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=FakeSession([]))
        publish.resolve(campaign, post, "facebook", "failed")
        self.assertEqual(load_ledger(campaign)["01-pain/vi/facebook"]["state"], "failed")

    def test_a_refused_feed_post_is_failed_and_may_retry(self):
        campaign, post = self.approved()
        self.smoke()
        session = FakeSession([(200, {"id": "p1"}), (200, {"id": "p2"}), (400, {"error": {"message": "nope"}})])
        with self.assertRaises(PublishError):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=session)
        self.assertEqual(load_ledger(campaign)["01-pain/vi/facebook"]["state"], "failed")

    def test_a_failed_comment_keeps_the_post_done(self):
        campaign, post = self.approved()
        self.smoke()
        session = FakeSession([(200, {"id": "p1"}), (200, {"id": "p2"}), (200, {"id": "555_77"}),
                               (400, {"error": {"message": "comments off"}})])
        row = publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=session,
                               log=lambda *_: None)
        self.assertEqual(row["state"], "done")
        self.assertIn("comment_error", row["steps"])

    def test_token_is_redacted_from_errors(self):
        campaign, post = self.approved()
        self.smoke()
        session = FakeSession([(400, {"error": {"message": f"Invalid token {TOKEN}"}})])
        with self.assertRaises(PublishError) as caught:
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=session)
        self.assertNotIn(TOKEN, str(caught.exception))
        self.assertNotIn(TOKEN, Path(campaign.dir / "published.yaml").read_text(encoding="utf-8"))

    def test_a_held_lock_blocks_publishing(self):
        campaign, post = self.approved()
        self.smoke()
        (self.root / ".studio").mkdir(exist_ok=True)
        (self.root / ".studio" / "publish.lock").write_text("x")
        with self.assertRaisesRegex(PublishError, "another publish"):
            publish_facebook(campaign, post, {}, confirm_page_name="Demo Page", dry_run=False, session=FakeSession([]))

    def test_pack_refuses_stale_images(self):
        campaign, post = self.campaign_and_post()
        fake_render(campaign, post)
        self.assertTrue(publish.build_pack(campaign, post, "facebook", {}).exists())
        write_yaml(post.path, post_data(series="edited"))
        campaign, post = self.campaign_and_post()
        with self.assertRaises(PublishError):
            publish.build_pack(campaign, post, "facebook", {})


if __name__ == "__main__":
    unittest.main()
