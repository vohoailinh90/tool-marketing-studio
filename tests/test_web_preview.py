"""web/ preview page: a render the server reports as `rendered: false` shows as a failed action.

The committed web/dist is served by the real app on a free port and driven in Chromium; only the answer of the
render endpoint is replaced (what the server says for a diagram it cannot draw is tested in test_diagram), so the
test is about what the page does with `rendered: false` and does not need Mermaid or a render.

The decision itself (failure or not, and whether an answer still belongs to the post on screen) is
web/src/lib/render-result.ts; tests/web/render_result_check.mts runs it under Node, and that is what
tests/mutations/web_preview.yaml mutates, because the bundle a mutation would have to edit has a new name at every build.
"""

from __future__ import annotations

import json
import re
import shutil
import socket
import subprocess
import threading
import time
import unittest

from mkt.model import ROOT
from tests.support import cleanup, make_root, post_data, write_yaml
from tests.test_render import chromium_available

try:
    import fastapi  # noqa: F401
    import uvicorn
    from playwright.sync_api import expect
except ImportError:
    uvicorn = None

UI_LANGUAGE_KEY = "tool-marketing-studio-ui-lang"
FAILED = "The images for this post could not be rendered"
ERROR = {"level": "error", "where": "slide 2", "message": "The diagram could not be drawn"}
WARNING = {"level": "warn", "where": "slide 1", "message": "The text is small"}


RESULT_CHECK = ROOT / "tests" / "web" / "render_result_check.mts"


def node_can_strip_types() -> bool:
    """`--experimental-strip-types` exists from Node 22.6 on; an older Node dies with `bad option` instead of running."""
    node = shutil.which("node")
    if not node:
        return False
    try:
        out = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    found = re.match(r"v?(\d+)\.(\d+)", out.strip())
    return bool(found) and (int(found[1]), int(found[2])) >= (22, 6)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@unittest.skipIf(uvicorn is None, "uvicorn/fastapi not installed")
@unittest.skipUnless(chromium_available(), "Chromium not installed")
class PreviewRenderFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mkt.server import create_app
        from playwright.sync_api import sync_playwright
        cls.root = make_root()
        write_yaml(cls.root / "campaigns/demo/posts/vi/02-other.yaml", post_data(id="02-other"))
        cls.port = free_port()
        app = create_app(cls.root, port=cls.port, dist=ROOT / "web" / "dist", token="tok")
        cls.server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=cls.port, log_level="warning"))
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()
        for _ in range(100):
            if cls.server.started:
                break
            time.sleep(0.05)
        else:
            raise RuntimeError("the app did not start")
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.should_exit = True
        cls.thread.join(10)
        cleanup(cls.root)

    def setUp(self):
        context = self.browser.new_context()
        self.addCleanup(context.close)
        context.add_init_script(f"localStorage.setItem({json.dumps(UI_LANGUAGE_KEY)}, 'en')")
        self.page = context.new_page()

    def answer_render_with(self, *answers):
        """The next calls of the render endpoint get these answers in turn; everything else reaches the app."""
        queue = list(answers)

        def handle(route):
            if route.request.method == "POST":
                route.fulfill(status=200, content_type="application/json", body=json.dumps(queue.pop(0)))
            else:
                route.continue_()
        self.page.route("**/api/campaigns/*/posts/*/*/render", handle)

    def hold_render(self):
        """The render endpoint does not answer until `held[0].fulfill(...)`: a render that takes seconds."""
        self.held = []

        def handle(route):
            if route.request.method == "POST":
                self.held.append(route)
            else:
                route.continue_()
        self.page.route("**/api/campaigns/*/posts/*/*/render", handle)

    def open_preview(self):
        self.page.goto(f"http://127.0.0.1:{self.port}/preview")
        self.render_button = self.page.get_by_role("button", name="Render images")
        self.render_button.wait_for()
        self.failed = self.page.get_by_role("alert").filter(has_text=FAILED)

    def click_render(self):
        """Click, wait for the answer, then for the page to finish the action (the button is disabled while it runs)."""
        with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/render")):
            self.render_button.click()
        expect(self.render_button).to_be_enabled()

    def test_a_render_the_server_refuses_is_shown_as_failed_next_to_its_errors(self):
        self.answer_render_with({"rendered": False, "issues": [ERROR]})
        self.open_preview()
        expect(self.failed).to_have_count(0)
        self.click_render()
        expect(self.failed).to_have_count(1)
        expect(self.page.get_by_text(ERROR["message"])).to_be_visible()

    def test_a_render_that_worked_shows_no_failure_even_with_warnings(self):
        self.answer_render_with({"rendered": True, "issues": [WARNING]})
        self.open_preview()
        self.click_render()
        expect(self.page.get_by_text(WARNING["message"])).to_be_visible()
        expect(self.failed).to_have_count(0)

    def test_the_failure_is_gone_after_the_next_render_works(self):
        self.answer_render_with({"rendered": False, "issues": [ERROR]}, {"rendered": True, "issues": []})
        self.open_preview()
        self.click_render()
        expect(self.failed).to_have_count(1)
        self.click_render()
        expect(self.failed).to_have_count(0)

    def test_an_answer_that_arrives_after_another_post_was_picked_is_not_shown_for_that_post(self):
        self.hold_render()
        self.open_preview()
        yaml_box = self.page.get_by_role("textbox", name="Post content")
        expect(yaml_box).to_contain_text("id: 01-pain")
        self.render_button.click()
        for _ in range(100):
            if self.held:
                break
            self.page.wait_for_timeout(50)
        self.assertEqual(len(self.held), 1)
        self.page.get_by_role("combobox", name="Post").click()
        self.page.get_by_role("option", name=re.compile("02-other")).click()
        expect(yaml_box).to_contain_text("id: 02-other")
        self.held[0].fulfill(status=200, content_type="application/json",
                             body=json.dumps({"rendered": False, "issues": [ERROR]}))
        expect(self.render_button).to_be_enabled()
        expect(self.failed).to_have_count(0)
        expect(self.page.get_by_text(ERROR["message"])).to_have_count(0)
        expect(yaml_box).to_contain_text("id: 02-other")


@unittest.skipUnless(node_can_strip_types(), "Node 22.6+ is needed to run TypeScript under type stripping")
class RenderResultTests(unittest.TestCase):
    def test_the_decision_of_the_preview_page_about_a_render_answer(self):
        done = subprocess.run(["node", "--experimental-strip-types", "--no-warnings", str(RESULT_CHECK)],
                              capture_output=True, text=True, timeout=120)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("render-result: ok", done.stdout)


if __name__ == "__main__":
    unittest.main()
