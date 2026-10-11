import json
import struct
import unittest

from mkt.layouts import Ctx, render_body
from mkt.model import load_campaign
from tests.support import PNG, cleanup, make_root, post_data, write_yaml


def png_size(path) -> tuple[int, int]:
    """Width and height from the PNG header (IHDR), without an imaging library."""
    data = path.read_bytes()[:24]
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    return struct.unpack(">II", data[16:24])


def chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:
        return False


class LayoutTests(unittest.TestCase):
    def test_slide_text_is_escaped(self):
        html = render_body({"layout": "cover", "title": "<script>alert(1)</script> **ok**"}, Ctx(lang="vi", campaign_dir=None))
        self.assertNotIn("<script>", html)
        self.assertIn('<strong class="hl">ok</strong>', html)

    def test_flow_total_is_computed(self):
        html = render_body({"layout": "flow", "title": "t", "steps": [{"text": "a", "minutes": 45}, {"text": "b", "minutes": 30}]},
                           Ctx(lang="ja", campaign_dir=None))
        self.assertIn("1時間15分", html)


@unittest.skipUnless(chromium_available(), "Chromium not installed")
class RenderSmokeTests(unittest.TestCase):
    def test_renders_png_at_feed_size_with_an_image_slide(self):
        from mkt.render import render_posts
        root = make_root()
        try:
            (root / "campaigns/demo/shot.png").write_bytes(PNG)
            slides = post_data()["slides"] + [{"layout": "image", "src": "shot.png", "caption": "real screen"}]
            write_yaml(root / "campaigns/demo/posts/vi/01-pain.yaml", post_data(slides=slides))
            campaign = load_campaign(root, "demo")
            warnings = render_posts(campaign, [campaign.post("01-pain", "vi")], {}, log=lambda *_: None)
            out = campaign.export_dir(campaign.post("01-pain", "vi"))
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["slides"]), 4)
            self.assertEqual(warnings, [])
            self.assertEqual(png_size(out / "04.png"), (1080, 1350))
            self.assertTrue((out / "facebook.txt").read_text(encoding="utf-8").startswith("Một dòng mở đầu"))
        finally:
            cleanup(root)


if __name__ == "__main__":
    unittest.main()
