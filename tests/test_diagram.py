import shutil
import tempfile
import unittest
from pathlib import Path

from mkt import diagram
from mkt.check import check_post, unsourced_numbers
from mkt.layouts import Ctx, render_body
from mkt.model import load_campaign
from mkt.page import build_page
from tests.support import PNG, cleanup, make_root, post_data, write_yaml
from tests.test_render import chromium_available, png_size

FLOW = "flowchart TD\n  A[Khách gửi form] --> B{Hợp lệ?}\n  B -->|Có| C[Lưu vào bảng tính]:::ok\n  B -->|Không| D[Báo lỗi]:::bad\n  C --> E[Gửi email]:::hl"
SEQUENCE = "sequenceDiagram\n  participant K as Khách\n  participant T as Tool\n  K->>T: Gửi form\n  T-->>K: Email xác nhận"
STATE = 'stateDiagram-v2\n  [*] --> Nhap\n  Nhap --> Duyet: Duyệt\n  Duyet --> [*]'
BROKEN = "flowchart TD\n  A -->"


def slide(source, **more) -> dict:
    return {"layout": "diagram", "title": "Cách tool xử lý", "source": source, **more}


class SourceTests(unittest.TestCase):
    def problems(self, source):
        return diagram.source_problems(source)

    def test_the_three_supported_kinds_are_accepted(self):
        for source in (FLOW, SEQUENCE, STATE, "graph LR\n  A --> B", "%% a comment\nflowchart TD\n  A <--> B"):
            self.assertEqual(self.problems(source), [], source)

    def test_it_must_start_with_a_supported_type(self):
        for source in ("", "   \n", "%% only a comment", "classDiagram\n  A <|-- B", "pie\n  \"a\": 1", "A --> B",
                       "---\nconfig:\n  theme: dark\n---\nflowchart TD\n  A --> B"):
            self.assertTrue(any("start with" in m or "no content" in m for m in self.problems(source)), source)

    def test_links_clicks_directives_and_css_are_refused(self):
        refused = {
            "click": 'flowchart TD\n  A --> B\n  click A href "x" _blank',
            "click after a semicolon": 'flowchart TD\n  A --> B; click A call f()',
            "href": 'flowchart TD\n  A --> B\n  href A "x"',
            "link in a sequence": 'sequenceDiagram\n  participant A\n  link A: Docs @ x',
            "style": "flowchart TD\n  A --> B\n  style A fill:#f00",
            "classDef": "flowchart TD\n  A --> B\n  classDef big fill:#f00",
            "linkStyle": "flowchart TD\n  A --> B\n  linkStyle 0 stroke:#f00",
            "init directive": 'flowchart TD\n  %%{init: {"securityLevel": "loose"}}%%\n  A --> B',
            "javascript url": 'flowchart TD\n  A["javascript:alert(1)"] --> B',
            "data url": 'flowchart TD\n  A["data:text/html;base64,AA"] --> B',
            "accTitle": "flowchart TD\n  accTitle: x\n  A --> B",
            "image node": 'flowchart TD\n  A@{ img: "file:///etc/hostname", label: "x" } --> B',
            "node attributes": "flowchart TD\n  A@{ shape: cyl } --> B",
        }
        for name, source in refused.items():
            self.assertTrue(self.problems(source), name)

    def test_a_fullwidth_spelling_is_refused_too(self):
        self.assertTrue(self.problems("flowchart TD\n  A --> B\n  ｃｌｉｃｋ A href \"x\""))

    def test_html_is_refused_but_arrows_and_line_breaks_are_not(self):
        for source in ('flowchart TD\n  A["<img src=x onerror=alert(1)>"] --> B',
                       'flowchart TD\n  A["<script>x</script>"] --> B',
                       'flowchart TD\n  A["<a href=x>y</a>"] --> B',
                       'flowchart TD\n  A["<!-- x -->"] --> B'):
            self.assertTrue(any("HTML" in m for m in self.problems(source)), source)
        self.assertEqual(self.problems('flowchart TD\n  A["Dòng một<br/>dòng hai"] <-.-> B\n  B <==> C\n  C --- D'), [])
        self.assertEqual(self.problems("sequenceDiagram\n  A<<->>B: hi\n  A-->>B: back"), [])

    def test_only_the_known_tones_may_highlight(self):
        for tone in diagram.TONES:
            self.assertEqual(self.problems(f"flowchart TD\n  A:::{tone} --> B\n  class B {tone}"), [], tone)
        for source in ("flowchart TD\n  A:::red --> B", "flowchart TD\n  A --> B\n  class A,B pink"):
            self.assertTrue(any("unknown tone" in m for m in self.problems(source)), source)

    def test_a_diagram_too_big_for_a_phone_is_refused(self):
        many_lines = "flowchart TD\n" + "\n".join(f"  N{i} --> N{i + 1}" for i in range(diagram.MAX_LINES))
        self.assertTrue(any("too long" in m for m in self.problems(many_lines)))
        self.assertTrue(any("too long" in m for m in self.problems("flowchart TD\n  A[" + "x" * diagram.MAX_CHARS + "] --> B")))

    def test_the_source_must_be_text(self):
        for source in (None, 12, ["flowchart TD"], {"a": 1}):
            self.assertTrue(self.problems(source), source)

    def test_node_ids_with_a_digit_are_not_numbers(self):
        self.assertNotIn("12", diagram.label_text("flowchart TD\n  step12[Gửi] --> A1[Xong]"))
        self.assertIn("45", diagram.label_text("flowchart TD\n  A[Mất 45 phút] --> B"))


class BundleTests(unittest.TestCase):
    def test_the_vendored_bundle_is_the_pinned_one(self):
        self.assertIn("__esbuild_esm_mermaid_nm", diagram.bundle())

    def test_a_different_bundle_is_never_run(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        other = folder / "mermaid.min.js"
        other.write_text("window.mermaid = {};", encoding="utf-8")
        original = diagram.BUNDLE
        diagram.BUNDLE = other
        try:
            with self.assertRaises(diagram.DiagramError):
                diagram.bundle()
        finally:
            diagram.BUNDLE = original


class PostCheckTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root()

    def tearDown(self):
        cleanup(self.root)

    def campaign_post(self, slides):
        write_yaml(self.root / "campaigns/demo/posts/vi/01-pain.yaml", post_data(slides=slides))
        campaign = load_campaign(self.root, "demo")
        return campaign, campaign.post("01-pain", "vi")

    def errors(self, slides):
        campaign, post = self.campaign_post(slides)
        return [i.message for i in check_post(campaign, post) if i.level == "error"]

    def test_a_good_diagram_slide_has_no_errors(self):
        self.assertEqual(self.errors([slide(FLOW, caption="Mỗi bước tự động"), slide(SEQUENCE), slide(STATE)]), [])

    def test_a_bad_source_is_an_error_on_its_slide(self):
        messages = self.errors([slide('flowchart TD\n  A --> B\n  click A href "x"')])
        self.assertTrue(any("click" in m for m in messages))

    def test_the_slide_needs_a_source_and_knows_no_other_fields(self):
        self.assertTrue(any("needs 'source'" in m for m in self.errors([{"layout": "diagram", "title": "t"}])))
        self.assertTrue(any("no field 'code'" in m for m in self.errors([slide(FLOW, code="x")])))

    def test_a_url_in_a_label_is_an_error(self):
        self.assertTrue(any("URL" in m for m in self.errors([slide('flowchart TD\n  A["xem www.example.com"] --> B')])))

    def test_numbers_in_labels_must_come_from_the_brief_but_node_ids_need_not(self):
        campaign, post = self.campaign_post([slide("flowchart TD\n  step12[Gửi form] --> n99[Xong]")])
        self.assertEqual([i for i in unsourced_numbers(campaign, post) if i.level == "error"], [])
        campaign, post = self.campaign_post([slide("flowchart TD\n  A[Mất 45 phút] --> B[Xong]")])
        self.assertTrue(any(i.level == "error" and "45" in i.message for i in unsourced_numbers(campaign, post)))


class LayoutTests(unittest.TestCase):
    def test_the_source_is_escaped_and_nothing_is_drawn_without_a_browser(self):
        html = render_body(slide('flowchart TD\n  A["<script>alert(1)</script>"] --> B'), Ctx(lang="vi", campaign_dir=None))
        self.assertNotIn("<script>", html)
        self.assertIn('<pre class="diagram__src">flowchart TD', html)
        self.assertNotIn("<svg", html)

    def test_the_page_on_disk_carries_no_mermaid(self):
        page = build_page(slide(FLOW), Ctx(lang="vi", campaign_dir=None), brand={"accent": "#2563eb"}, tool_name="Demo",
                          series="", handle="", index=1, total=1, fmt_name="portrait")
        self.assertNotIn("__esbuild_esm_mermaid_nm", page)
        self.assertLess(len(page), 100_000)
        self.assertIn("default-src 'none'", page)


@unittest.skipUnless(chromium_available(), "Chromium not installed")
class DrawTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, ignore_errors=True)
        self.page = self.browser.new_page(viewport={"width": 1080, "height": 1350})
        self.addCleanup(self.page.close)

    def open(self, source, lang="vi", accent="#2563eb", **more):
        html = build_page(slide(source, **more), Ctx(lang=lang, campaign_dir=None), brand={"accent": accent},
                          tool_name="Demo", series="", handle="", index=1, total=1, fmt_name="portrait")
        path = self.folder / "slide.html"
        path.write_text(html, encoding="utf-8")
        self.page.goto(path.as_uri())

    def count(self, selector) -> int:
        return self.page.evaluate("(s) => document.querySelectorAll(s).length", selector)

    def test_each_kind_becomes_an_svg_in_place_of_its_source(self):
        for source in (FLOW, SEQUENCE, STATE):
            self.open(source)
            self.assertEqual(self.count(".diagram__src"), 1)
            diagram.render_in_page(self.page)
            self.assertEqual((self.count(".diagram__art svg"), self.count(".diagram__src")), (1, 0), source)
            self.assertEqual(diagram.text_warnings(self.page), [], source)

    def test_japanese_labels_are_drawn(self):
        self.open("flowchart TD\n  A[お客様がフォームを送信] --> B{入力は正しい?}", lang="ja")
        diagram.render_in_page(self.page)
        self.assertEqual(self.count(".diagram__art svg"), 1)

    def test_the_campaign_accent_colours_the_diagram(self):
        self.open(FLOW, accent="#e11d48")
        diagram.render_in_page(self.page)
        drawn = self.page.evaluate("document.querySelector('.diagram__art svg').outerHTML").lower()
        self.assertIn("#e11d48", drawn)
        self.assertNotIn("#2563eb", drawn)

    def test_mermaid_runs_in_strict_mode(self):
        self.open(FLOW)
        diagram.render_in_page(self.page)
        self.assertEqual(self.page.evaluate("mermaid.mermaidAPI.getConfig().securityLevel"), "strict")

    def test_a_link_in_the_drawing_is_refused_even_when_check_was_skipped(self):
        self.open('flowchart TD\n  A[Start] --> B[End]\n  click A href "https://example.com" _blank')
        with self.assertRaises(diagram.DiagramError) as caught:
            diagram.render_in_page(self.page)
        self.assertIn("links, images and scripts", str(caught.exception))

    def test_an_image_in_the_drawing_is_refused_even_when_check_was_skipped(self):
        picture = self.folder / "local.png"
        picture.write_bytes(PNG)
        self.open(f'flowchart TD\n  A@{{ img: "{picture.as_uri()}", label: "x", w: 60, h: 60 }} --> B[End]')
        with self.assertRaises(diagram.DiagramError) as caught:
            diagram.render_in_page(self.page)
        self.assertIn("images", str(caught.exception))

    def test_a_source_mermaid_cannot_parse_is_an_error_that_says_where(self):
        self.open(BROKEN)
        with self.assertRaises(diagram.DiagramError) as caught:
            diagram.render_in_page(self.page)
        self.assertIn("Mermaid cannot draw this diagram", str(caught.exception))

    def test_text_too_small_to_read_is_a_warning(self):
        crowded = "flowchart LR\n" + "\n".join(f"  N{i}[Bước số {i} của quy trình dài] --> N{i + 1}[Bước kế tiếp]" for i in range(1, 7))
        self.open(crowded)
        diagram.render_in_page(self.page)
        self.page.evaluate("fit()")
        warnings = diagram.text_warnings(self.page)
        self.assertEqual(len(warnings), 1)
        self.assertIn("flowchart TD", warnings[0])

    def test_a_page_without_a_diagram_has_nothing_to_warn_about(self):
        self.page.set_content("<html><body>no diagram</body></html>")
        self.assertEqual(diagram.text_warnings(self.page), [])


@unittest.skipUnless(chromium_available(), "Chromium not installed")
class RenderPostTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root()
        self.addCleanup(cleanup, self.root)

    def render(self, *posts):
        from mkt.render import render_posts
        campaign = load_campaign(self.root, "demo")
        issues = render_posts(campaign, [campaign.post(pid, "vi") for pid in posts], {}, log=lambda *_: None)
        return campaign, issues

    def write(self, post_id, slides):
        write_yaml(self.root / f"campaigns/demo/posts/vi/{post_id}.yaml", post_data(id=post_id, slides=slides))

    def test_a_post_with_diagrams_renders_to_feed_sized_images(self):
        self.write("01-pain", [{"layout": "cover", "title": "Một form"}, slide(FLOW, caption="Mỗi bước tự động"), slide(SEQUENCE)])
        campaign, issues = self.render("01-pain")
        self.assertEqual(issues, [])
        out = campaign.export_dir(campaign.post("01-pain", "vi"))
        self.assertEqual(png_size(out / "02.png"), (1080, 1350))
        self.assertEqual(png_size(out / "03.png"), (1080, 1350))
        self.assertGreater((out / "02.png").stat().st_size, 20_000)

    def test_a_diagram_mermaid_cannot_draw_costs_only_its_own_post(self):
        self.write("01-pain", [{"layout": "cover", "title": "Một form"}, slide(FLOW)])
        self.write("02-bad", [{"layout": "cover", "title": "Một form"}, slide(BROKEN)])
        campaign, issues = self.render("01-pain")
        self.assertEqual(issues, [])
        bad = campaign.export_dir(campaign.post("02-bad", "vi"))
        (bad / "manifest.json").parent.mkdir(parents=True, exist_ok=True)
        (bad / "manifest.json").write_text("{}", encoding="utf-8")        # a render from before the edit
        (bad / "01.png").write_bytes(b"old")
        campaign, issues = self.render("01-pain", "02-bad")
        self.assertEqual([(i.level, i.where) for i in issues], [("error", "demo/vi/02-bad slide 2")])
        self.assertIn("Mermaid cannot draw", issues[0].message)
        self.assertEqual(sorted(p.name for p in bad.iterdir()), [], "a post that could not be drawn keeps no half-render")
        good = campaign.export_dir(campaign.post("01-pain", "vi"))
        self.assertTrue((good / "manifest.json").is_file())

    def test_a_crowded_diagram_still_renders_with_a_warning(self):
        crowded = "flowchart LR\n" + "\n".join(f"  N{i}[Bước số {i} của quy trình dài] --> N{i + 1}[Bước kế tiếp]" for i in range(1, 7))
        self.write("01-pain", [slide(crowded)])
        campaign, issues = self.render("01-pain")
        self.assertEqual([i.level for i in issues], ["warn"])
        self.assertTrue((campaign.export_dir(campaign.post("01-pain", "vi")) / "01.png").is_file())

    def test_the_cli_exits_non_zero_when_a_diagram_cannot_be_drawn(self):
        import contextlib
        import io
        from mkt.cli import main
        self.write("01-pain", [{"layout": "cover", "title": "Một form"}, slide(BROKEN)])
        shown = io.StringIO()
        with contextlib.redirect_stdout(shown):
            code = main(["render", "demo", "--post", "01-pain", "--lang", "vi"], root=self.root)
        self.assertEqual(code, 1)
        self.assertIn("Mermaid cannot draw", shown.getvalue())
        self.write("01-pain", [{"layout": "cover", "title": "Một form"}, slide(FLOW)])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["render", "demo", "--post", "01-pain", "--lang", "vi"], root=self.root), 0)

    def test_the_app_reports_a_post_it_could_not_render(self):
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            self.skipTest("fastapi/httpx not installed")
        from mkt.server import create_app
        dist = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, dist, ignore_errors=True)
        (dist / "index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
        client = TestClient(create_app(self.root, port=8765, dist=dist, token="tok"), base_url="http://127.0.0.1:8765")
        url = "/api/campaigns/demo/posts/vi/01-pain/render"
        self.write("01-pain", [{"layout": "cover", "title": "Một form"}, slide(BROKEN)])
        broken = client.post(url, headers={"X-Studio-Token": "tok"}, json={}).json()
        self.assertFalse(broken["rendered"])
        self.assertEqual([i["level"] for i in broken["issues"]], ["error"])
        self.write("01-pain", [{"layout": "cover", "title": "Một form"}, slide(FLOW)])
        self.assertTrue(client.post(url, headers={"X-Studio-Token": "tok"}, json={}).json()["rendered"])


if __name__ == "__main__":
    unittest.main()
