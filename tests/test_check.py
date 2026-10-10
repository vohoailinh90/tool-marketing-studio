import os
import unittest

from mkt.check import check_campaign, check_post, unsourced_numbers, x_length
from mkt.model import load_campaign
from tests.support import cleanup, make_root, post_data, write_yaml


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root()

    def tearDown(self):
        cleanup(self.root)

    def errors(self, **changes):
        write_yaml(self.root / "campaigns/demo/posts/vi/01-pain.yaml", post_data(**changes))
        campaign = load_campaign(self.root, "demo")
        return [i.message for i in check_post(campaign, campaign.post("01-pain", "vi")) if i.level == "error"]

    def test_clean_post_has_no_errors(self):
        self.assertEqual(self.errors(), [])

    def test_url_in_slide_text_is_an_error(self):
        slides = post_data()["slides"] + [{"layout": "cta", "title": "Xem www.example.com nhé"}]
        self.assertTrue(any("URL" in m for m in self.errors(slides=slides)))

    def test_url_in_caption_is_an_error(self):
        platforms = {"facebook": {"caption": "Vào https://evil.example ngay"}}
        self.assertTrue(any("URL" in m for m in self.errors(platforms=platforms)))

    def test_image_paths_cannot_leave_the_campaign(self):
        outside = self.root / "secret.png"
        outside.write_bytes(b"x")
        for src in ("../../secret.png", str(outside), "C:/secret.png"):
            slides = [{"layout": "image", "src": src}]
            self.assertTrue(any("image src" in m or "not found" in m for m in self.errors(slides=slides)), src)

    def test_a_symlink_out_of_the_campaign_is_refused(self):
        outside = self.root / "secret.png"
        outside.write_bytes(b"x")
        link = self.root / "campaigns/demo/shot.png"
        os.symlink(outside, link)
        self.assertTrue(any("not found" in m for m in self.errors(slides=[{"layout": "image", "src": "shot.png"}])))

    def test_unknown_layout_is_an_error(self):
        self.assertTrue(any("unknown layout" in m for m in self.errors(slides=[{"layout": "marquee"}])))

    def test_todo_blocks_a_ready_post_but_not_a_draft(self):
        slides = [{"layout": "cover", "title": "TODO"}]
        self.assertTrue(any("TODO" in m for m in self.errors(slides=slides)))
        self.assertFalse(any("TODO" in m for m in self.errors(slides=slides, status="draft")))

    def test_placeholder_link_blocks_a_ready_post(self):
        campaign_path = self.root / "campaigns/demo/campaign.yaml"
        import yaml
        data = yaml.safe_load(campaign_path.read_text(encoding="utf-8"))
        data["links"]["survey"] = "https://REPLACE_ME/x"
        write_yaml(campaign_path, data)
        self.assertTrue(any("not a real URL" in m for m in self.errors()))

    def test_x_counts_cjk_and_vietnamese_letters_double(self):
        self.assertEqual(x_length("a"), 1)
        self.assertEqual(x_length("あ"), 2)
        self.assertEqual(x_length("ệ"), 2)
        self.assertEqual(x_length("{link}"), 23)

    def test_numbers_that_differ_between_languages_are_flagged(self):
        en = post_data(slides=[{"layout": "cover", "title": "Save 45 minutes"}, {"layout": "cta", "title": "Try"}])
        write_yaml(self.root / "campaigns/demo/posts/en/01-pain.yaml", en)
        campaign = load_campaign(self.root, "demo")
        self.assertTrue(any("another language" in i.message for i in check_campaign(campaign)))

    def test_unsourced_numbers_are_errors_in_claims(self):
        write_yaml(self.root / "campaigns/demo/posts/vi/01-pain.yaml",
                   post_data(slides=[{"layout": "stat", "value": "99%", "label": "nhanh hơn"}]))
        campaign = load_campaign(self.root, "demo")
        issues = unsourced_numbers(campaign, campaign.post("01-pain", "vi"))
        self.assertTrue(any(i.level == "error" and "99" in i.message for i in issues))


if __name__ == "__main__":
    unittest.main()
