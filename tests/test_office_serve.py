"""scripts/office/serve.py: the read-only HTTP face of the dashboard.

The server shows data that can quote task descriptions, so most of what is checked here is
what it refuses: other hosts, other methods, paths outside the built page, a public bind.
"""

from __future__ import annotations

import http.client
import json
import os
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SERVE_PATH = ROOT / "scripts" / "office" / "serve.py"


def load_module(name: str, path: Path):
    """Load from source, never from the bytecode cache (see test_session_budget)."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


serve = load_module("office_serve", SERVE_PATH)


def listing(directory: Path) -> list[str]:
    return sorted(str(path.relative_to(directory)) for path in directory.rglob("*"))


class ServerCase(unittest.TestCase):
    extra_hosts: set[str] | None = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)
        self.root = self.base / "checkout"
        self.home = self.base / "team"
        self.dist = self.base / "dist"
        for directory in (self.root, self.home, self.dist / "assets"):
            directory.mkdir(parents=True)
        (self.dist / "index.html").write_text("<!doctype html><title>office</title>", encoding="utf-8")
        (self.dist / "assets" / "app-1a2b.js").write_text("console.log(1)", encoding="utf-8")
        (self.dist / "assets" / "app-1a2b.css").write_text("body{}", encoding="utf-8")
        (self.base / "secret.txt").write_text("TOP-SECRET", encoding="utf-8")
        self.server = serve.make_server("127.0.0.1", 0, self.root, self.home, self.dist, self.extra_hosts)
        self.port = self.server.server_address[1]
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self._stop, thread)

    def _stop(self, thread: threading.Thread) -> None:
        self.server.shutdown()
        self.server.server_close()
        thread.join(5)

    def request(self, path: str, method: str = "GET", host: str | None = None, body: bytes | None = None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            connection.putrequest(method, path, skip_host=True)
            connection.putheader("Host", host or f"127.0.0.1:{self.port}")
            if body is not None:
                connection.putheader("Content-Length", str(len(body)))
            connection.endheaders(body)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def get_json(self, path: str, **kwargs):
        status, headers, body = self.request(path, **kwargs)
        return status, json.loads(body)


class ApiTests(ServerCase):
    def test_health_lists_the_demos(self) -> None:
        status, data = self.get_json("/api/health")
        self.assertEqual(status, 200)
        self.assertEqual((data["ok"], data["demos"]), (True, ["claude-t3", "team-f12"]))

    def test_an_empty_checkout_is_an_empty_snapshot_not_an_error(self) -> None:
        for mode in ("claude", "team"):
            status, data = self.get_json(f"/api/snapshot?mode={mode}")
            self.assertEqual((status, data["empty"], data["mode"]), (200, True, mode))

    def test_the_mode_defaults_to_claude(self) -> None:
        self.assertEqual(self.get_json("/api/snapshot")[1]["mode"], "claude")

    def test_a_demo_replays_at_the_requested_moment(self) -> None:
        span = self.get_json("/api/snapshot?demo=claude-t3")[1]["span"]
        mid = span["start"] + 10
        status, data = self.get_json(f"/api/snapshot?demo=claude-t3&at={mid}")
        self.assertEqual((status, data["now"], data["demo"], data["live"]), (200, mid, "claude-t3", False))
        self.assertEqual(data["agents"]["requirement-analyst"]["state"], "working")

    def test_the_team_demo_is_served_in_team_mode(self) -> None:
        status, data = self.get_json("/api/snapshot?demo=team-f12")
        self.assertEqual((status, data["mode"], data["feature"]), (200, "team", "F12"))

    def test_bad_parameters_are_a_400_with_a_reason(self) -> None:
        for query in ("mode=both", "at=abc", "at=nan", "at=-5", "at=1e99", "feature=../etc", "feature=" + "a" * 80, "demo=nope"):
            status, data = self.get_json(f"/api/snapshot?{query}")
            self.assertEqual((status, data["error"]), (400, "bad_request"), query)

    def test_the_live_view_follows_the_event_log_as_it_grows(self) -> None:
        log = self.root / "artifacts" / "handoff" / "office-events.jsonl"
        log.parent.mkdir(parents=True)

        def line(kind: str, ts: float, **fields) -> str:
            return json.dumps({"v": 1, "ev": kind, "ts": ts, "session": "s", **fields}) + "\n"

        log.write_text(line("spawn_request", 100.0, agent="architect", task="x", tool_use_id="u1")
                       + line("start", 100.5, agent="architect", agent_id="a1"), encoding="utf-8")
        first = self.get_json("/api/snapshot?mode=claude&at=110")[1]
        self.assertEqual(first["agents"]["architect"]["state"], "working")
        with log.open("a", encoding="utf-8") as handle:
            handle.write(line("stop", 105.0, agent="architect", agent_id="a1", note="done"))
        second = self.get_json("/api/snapshot?mode=claude&at=110")[1]
        self.assertEqual(second["agents"]["architect"]["state"], "done")

    def test_unknown_api_paths_are_a_404(self) -> None:
        self.assertEqual(self.get_json("/api/nothing")[0], 404)

    def test_a_broken_ledger_does_not_take_the_api_down(self) -> None:
        ledger = self.root / "artifacts" / "handoff" / "agent-budget.json"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("{not json", encoding="utf-8")
        self.assertEqual(self.get_json("/api/snapshot?mode=claude")[0], 200)


class RefusalTests(ServerCase):
    def test_a_host_header_that_is_not_this_machine_is_forbidden_everywhere(self) -> None:
        for path in ("/api/snapshot", "/api/health", "/", "/assets/app-1a2b.js"):
            self.assertEqual(self.request(path, host="evil.example")[0], 403, path)
            self.assertEqual(self.request(path, host="evil.example:80")[0], 403, path)

    def test_loopback_names_are_accepted_with_or_without_a_port(self) -> None:
        for host in ("127.0.0.1", "localhost", "LOCALHOST:8765", "[::1]:8765", "127.0.0.1:80"):
            self.assertEqual(self.request("/api/health", host=host)[0], 200, host)

    def test_a_host_header_that_only_starts_like_loopback_is_forbidden(self) -> None:
        for host in ("localhost.evil.example", "127.0.0.1.evil.example", "evil.example:127.0.0.1", "[::1]x", "localhost:abc",
                     "localhost:80:80", "localhost:123456", "localhost evil", "[::1", "local\thost"):
            self.assertEqual(self.request("/api/health", host=host)[0], 403, host)

    def test_only_get_and_head_are_answered(self) -> None:
        for method in ("POST", "PUT", "DELETE", "PATCH", "OPTIONS"):
            status, headers, _ = self.request("/api/snapshot", method=method, body=b"{}" if method in ("POST", "PUT", "PATCH") else None)
            self.assertEqual(status, 405, method)
            self.assertEqual(headers["Allow"], "GET, HEAD")

    def test_paths_outside_the_built_page_are_never_served(self) -> None:
        (self.dist / "link.txt").symlink_to(self.base / "secret.txt")
        for path in ("/../secret.txt", "/%2e%2e/secret.txt", "/..%2fsecret.txt", "/assets/../../secret.txt",
                     "/assets/%2e%2e/%2e%2e/secret.txt", "/link.txt", "//etc/passwd", "/%00.js", "/..\\secret.txt"):
            status, _, body = self.request(path)
            self.assertNotIn(b"TOP-SECRET", body, path)
            self.assertNotIn(b"root:", body, path)

    def test_the_server_writes_nothing(self) -> None:
        before = (listing(self.root), listing(self.home), listing(self.dist))
        for path in ("/", "/api/snapshot?mode=claude", "/api/snapshot?mode=team", "/api/snapshot?demo=claude-t3", "/nope.js"):
            self.request(path)
        self.request("/api/snapshot", method="POST", body=b"x")
        self.assertEqual((listing(self.root), listing(self.home), listing(self.dist)), before)


class AllowedHostTests(ServerCase):
    extra_hosts = {"office.internal"}

    def test_an_operator_listed_host_is_accepted(self) -> None:
        self.assertEqual(self.request("/api/health", host="office.internal:8765")[0], 200)
        self.assertEqual(self.request("/api/health", host="other.internal")[0], 403)


class StaticTests(ServerCase):
    def test_the_index_is_served_at_the_root_and_for_client_side_routes(self) -> None:
        for path in ("/", "/replay", "/some/deep/route"):
            status, headers, body = self.request(path)
            self.assertEqual((status, b"<title>office</title>" in body), (200, True), path)
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertTrue(headers["Content-Type"].startswith("text/html"))

    def test_hashed_assets_are_cached_forever_with_the_right_type(self) -> None:
        status, headers, _ = self.request("/assets/app-1a2b.js")
        self.assertEqual(status, 200)
        self.assertTrue(headers["Content-Type"].startswith("text/javascript"))
        self.assertEqual(headers["Cache-Control"], "public, max-age=31536000, immutable")
        self.assertTrue(self.request("/assets/app-1a2b.css")[1]["Content-Type"].startswith("text/css"))

    def test_a_missing_file_is_a_404_not_the_index(self) -> None:
        self.assertEqual(self.request("/assets/missing.js")[0], 404)

    def test_every_response_carries_the_security_headers(self) -> None:
        for path in ("/", "/api/health", "/api/snapshot?demo=nope", "/assets/app-1a2b.js", "/assets/missing.js"):
            _, headers, _ = self.request(path)
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff", path)
            self.assertEqual(headers["X-Frame-Options"], "DENY", path)
            self.assertIn("default-src 'self'", headers["Content-Security-Policy"], path)
            self.assertIn("connect-src 'self'", headers["Content-Security-Policy"], path)
        forbidden = self.request("/", host="evil.example")[1]
        self.assertEqual(forbidden["X-Content-Type-Options"], "nosniff")

    def test_head_has_the_headers_and_no_body(self) -> None:
        status, headers, body = self.request("/api/health", method="HEAD")
        self.assertEqual((status, body), (200, b""))
        self.assertGreater(int(headers["Content-Length"]), 0)

    def test_without_a_build_the_page_says_how_to_build_it_and_the_api_still_works(self) -> None:
        for item in sorted(self.dist.rglob("*"), reverse=True):
            item.unlink() if item.is_file() or item.is_symlink() else item.rmdir()
        self.dist.rmdir()
        status, _, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn(b"npm run build", body)
        self.assertEqual(self.request("/api/health")[0], 200)


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SERVE_PATH), *args], capture_output=True, text=True, timeout=30,
                              env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT)})

    def test_a_public_bind_is_refused_without_the_flag(self) -> None:
        for host in ("0.0.0.0", "192.168.1.10", "::", "127.office.example"):
            result = self.run_cli("--host", host, "--port", "0")
            self.assertEqual(result.returncode, 2, host)
            self.assertIn("refusing to bind", result.stderr)

    @staticmethod
    def resolves(*addresses: str):
        return mock.patch.object(serve.socket, "getaddrinfo", return_value=[(2, 1, 6, "", (item, 0)) for item in addresses])

    def test_loopback_means_every_address_is_loopback_not_a_loopback_looking_spelling(self) -> None:
        for host in ("127.0.0.1", "127.1.2.3", "::1"):
            self.assertEqual(serve.loopback_bind(host), host, host)
        self.assertEqual(serve.loopback_bind("::1%lo"), "::1", "a scope id is not part of the address that is bound")
        self.assertIsNotNone(serve.loopback_bind("::ffff:127.0.0.1"), "judged by the IPv4 address inside, on every Python")
        self.assertIsNone(serve.loopback_bind("::ffff:10.0.0.1"))
        for host in ("0.0.0.0", "10.0.0.1", "192.168.1.10", "::", ""):
            self.assertIsNone(serve.loopback_bind(host), host)

        with self.resolves("127.0.0.1", "::1"):
            self.assertEqual(serve.loopback_bind("localhost"), "127.0.0.1")
        with self.resolves("203.0.113.9"):
            self.assertIsNone(serve.loopback_bind("127.office.example"), "a name that starts with 127. is still just a name")
        with self.resolves("127.0.0.1", "203.0.113.9"):
            self.assertIsNone(serve.loopback_bind("mixed.example"), "one public address among loopback ones is enough to refuse")
        with mock.patch.object(serve.socket, "getaddrinfo", side_effect=OSError("no such host")):
            self.assertIsNone(serve.loopback_bind("127.nope.example"))

    def test_a_mapped_ipv6_address_is_judged_by_the_ipv4_address_inside(self) -> None:
        """A stand-in answers False for its own flag, as Python before 3.13 does for `::ffff:127.0.0.1`."""
        def stub(inside: str):
            return types.SimpleNamespace(is_loopback=False, ipv4_mapped=serve.ipaddress.IPv4Address(inside))

        self.assertTrue(serve.is_loopback_address(stub("127.0.0.1")))
        self.assertFalse(serve.is_loopback_address(stub("10.0.0.1")))
        self.assertFalse(serve.is_loopback_address(types.SimpleNamespace(is_loopback=False, ipv4_mapped=None)))

    def test_a_name_with_both_families_is_bound_by_its_ipv4_address(self) -> None:
        with self.resolves("::1", "127.0.0.1"):
            self.assertEqual(serve.loopback_bind("localhost"), "127.0.0.1")
        with self.resolves("::1"):
            self.assertEqual(serve.loopback_bind("v6only.localdomain"), "::1")

    def test_a_name_is_resolved_once_and_the_vetted_address_is_what_gets_bound(self) -> None:
        answers = iter([[(2, 1, 6, "", ("127.0.0.1", 0))], [(2, 1, 6, "", ("0.0.0.0", 0))]])
        with mock.patch.object(serve.socket, "getaddrinfo", side_effect=lambda *a, **k: next(answers)) as lookup:
            bound = self.main_binds("--host", "flip.example")
        self.assertEqual(lookup.call_count, 1, "a second lookup is a second chance to get a different answer")
        self.assertEqual(bound["host"], "127.0.0.1", "the numeric address that passed the check, not the name")

    def main_binds(self, *args: str) -> dict:
        """Run `main` up to the point of serving and report what it would have bound and accepted."""
        seen: dict = {}

        class Stop:
            server_address = ("", 0)

            def serve_forever(self) -> None:
                raise KeyboardInterrupt

            def server_close(self) -> None:
                pass

        def fake(host, port, root, team_home, dist, extra_hosts=None, verbose=False):
            seen.update(host=host, extra_hosts=extra_hosts)
            return Stop()

        with mock.patch.object(serve, "make_server", side_effect=fake), mock.patch("builtins.print"):
            code = serve.main(["serve.py", "--port", "0", *args])
        seen["code"] = code
        return seen

    def test_the_host_that_was_bound_is_the_host_the_browser_is_allowed_to_send(self) -> None:
        seen = self.main_binds("--host", "127.1.2.3")
        self.assertEqual((seen["code"], seen["host"], seen["extra_hosts"]), (0, "127.1.2.3", {"127.1.2.3"}))
        self.assertTrue(serve.host_allowed("127.1.2.3:8765", seen["extra_hosts"]))
        self.assertFalse(serve.host_allowed("127.1.2.4:8765", seen["extra_hosts"]), "only the host that was bound")
        seen = self.main_binds("--host", "::1", "--allow-host", "office.internal")
        self.assertEqual(seen["extra_hosts"], {"[::1]", "office.internal"})
        with self.resolves("127.0.0.1"):
            seen = self.main_binds("--host", "MyBox.Local")
        self.assertEqual(seen["extra_hosts"], {"mybox.local"})

    def test_a_host_that_is_not_loopback_is_never_added_to_the_accepted_hosts(self) -> None:
        seen = self.main_binds("--host", "0.0.0.0", "--allow-remote")
        self.assertEqual((seen["host"], seen["extra_hosts"]), ("0.0.0.0", set()), "--allow-host is how an operator opts in")

    def test_the_host_header_spelling_of_an_address(self) -> None:
        self.assertEqual(
            [serve.host_header_name(host) for host in ("127.1.2.3", "::1", "fe80::1%eth0", "MyBox.Local", "FE80::1", "::")],
            ["127.1.2.3", "[::1]", "[fe80::1]", "mybox.local", "[fe80::1]", "[::]"],
        )

    def test_an_ipv6_host_is_accepted_in_the_form_a_browser_normalizes_it_to(self) -> None:
        for spelled, sent in (
            ("::ffff:127.0.0.1", "[::ffff:7f00:1]"),  # a browser never sends a dotted quad
            ("0:0:0:0:0:0:0:1", "[::1]"),
            ("2001:db8:0:0:1:0:0:1", "[2001:db8::1:0:0:1]"),  # the first of two equal runs of zeros is compressed
            ("2001:0db8:0:1:0:0:0:1", "[2001:db8:0:1::1]"),  # the longest run is compressed
            ("1:0:2:3:4:5:6:7", "[1:0:2:3:4:5:6:7]"),  # a single zero group is not compressed
        ):
            self.assertEqual(serve.host_header_name(spelled), sent, spelled)
        seen = self.main_binds("--host", "::ffff:127.0.0.1")
        self.assertEqual((seen["code"], seen["extra_hosts"]), (0, {"[::ffff:7f00:1]"}))
        self.assertTrue(serve.host_allowed("[::ffff:7f00:1]:8765", seen["extra_hosts"]))

    def test_the_printed_url_keeps_the_zone_of_a_scoped_address(self) -> None:
        self.assertEqual(
            [serve.url_host(host) for host in ("fe80::1%eth0", "::1", "127.0.0.1", "MyBox.Local", "::ffff:127.0.0.1")],
            ["[fe80::1%25eth0]", "[::1]", "127.0.0.1", "mybox.local", "[::ffff:7f00:1]"],
        )

    def test_a_remote_name_is_bound_by_the_address_it_resolves_to_so_the_family_follows_it(self) -> None:
        with self.resolves("2001:db8::1"):
            seen = self.main_binds("--host", "v6-only.example", "--allow-remote")
        self.assertEqual((seen["host"], seen["extra_hosts"]), ("2001:db8::1", set()), "an AAAA-only name needs an IPv6 socket")
        with self.resolves("2001:db8::1", "203.0.113.9"):
            self.assertEqual(self.main_binds("--host", "dual.example", "--allow-remote")["host"], "203.0.113.9", "IPv4 first")
        with mock.patch.object(serve.socket, "getaddrinfo", side_effect=OSError("no such host")):
            self.assertEqual(self.main_binds("--host", "gone.example", "--allow-remote")["host"], "gone.example")
        self.assertEqual(self.main_binds("--host", "fe80::1%eth0", "--allow-remote")["host"], "fe80::1%eth0", "a scope id is kept")
        self.assertEqual(self.main_binds("--host", "::", "--allow-remote")["host"], "::")

    def test_an_ipv6_literal_gets_an_ipv6_socket_and_anything_else_the_ipv4_one(self) -> None:
        self.assertEqual(serve.IPv6Server.address_family, serve.socket.AF_INET6)
        chosen: list[str] = []

        def recorder(label: str):
            def build(address, handler):
                chosen.append(label)
                return types.SimpleNamespace(daemon_threads=False)
            return build

        with mock.patch.object(serve, "IPv6Server", recorder("v6")), mock.patch.object(serve, "ThreadingHTTPServer", recorder("v4")):
            for host in ("::1", "127.0.0.1", "localhost"):
                serve.make_server(host, 0, Path("."), Path("."), Path("."))
        self.assertEqual(chosen, ["v6", "v4", "v4"])

    def test_an_ipv6_loopback_bind_starts_and_serves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            try:
                server = serve.make_server("::1", 0, base, base, base / "dist", {serve.host_header_name("::1")})
            except OSError as exc:  # a container without IPv6 has no ::1 to bind
                self.skipTest(f"no IPv6 loopback here: {exc}")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(lambda: (server.shutdown(), server.server_close(), thread.join(5)))
            port = server.server_address[1]
            connection = http.client.HTTPConnection("::1", port, timeout=10)
            try:
                connection.putrequest("GET", "/api/health", skip_host=True)
                connection.putheader("Host", f"[::1]:{port}")
                connection.endheaders()
                self.assertEqual(connection.getresponse().status, 200)
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
