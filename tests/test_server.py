import tempfile
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient
except ImportError:  # httpx missing
    TestClient = None

from tests.support import cleanup, make_root


@unittest.skipIf(TestClient is None, "fastapi/httpx not installed")
class ServerGuardTests(unittest.TestCase):
    def setUp(self):
        from mkt.server import create_app
        self.root = make_root()
        dist = Path(tempfile.mkdtemp())
        (dist / "index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
        self.app = create_app(self.root, port=8765, dist=dist, token="tok")
        self.client = TestClient(self.app, base_url="http://127.0.0.1:8765")

    def tearDown(self):
        cleanup(self.root)

    def test_missing_token_is_refused(self):
        self.assertEqual(self.client.get("/api/state").status_code, 403)
        self.assertEqual(self.client.get("/api/state", headers={"X-Studio-Token": "nope"}).status_code, 403)

    def test_token_opens_the_api(self):
        response = self.client.get("/api/state", headers={"X-Studio-Token": "tok"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["campaigns"], ["demo"])

    def test_other_hosts_are_refused(self):
        evil = TestClient(self.app, base_url="http://evil.example:8765")
        self.assertEqual(evil.get("/", headers={"X-Studio-Token": "tok"}).status_code, 403)

    def test_form_posts_are_refused(self):
        response = self.client.post("/api/facebook/smoke", headers={"X-Studio-Token": "tok"}, data={"a": "b"})
        self.assertEqual(response.status_code, 415)

    def test_files_need_the_token(self):
        self.assertEqual(self.client.get("/files/demo/vi/01-pain/01.png").status_code, 403)

    def test_index_carries_the_token(self):
        self.assertIn('name="studio-token" content="tok"', self.client.get("/").text)

    def test_path_tricks_are_not_found(self):
        response = self.client.get("/api/campaigns/..%2Fetc/posts/vi/x", headers={"X-Studio-Token": "tok"})
        self.assertIn(response.status_code, (403, 404))


if __name__ == "__main__":
    unittest.main()
