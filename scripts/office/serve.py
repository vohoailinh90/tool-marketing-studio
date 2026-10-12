#!/usr/bin/env python3
"""Serve the agent-office dashboard: `/api/snapshot` plus the built page in `office/dist`.

Read-only by construction. It answers GET and HEAD, writes nothing, runs nothing
from the data it reads and shows only what `snapshot.py` derives. The data can
quote task descriptions, so the page is for the person running the checkout: it
binds to loopback unless `--allow-remote` is given (a name is resolved once and
the numeric address is bound), and refuses a `Host` header that is not loopback,
the loopback host you bound or listed with `--allow-host` (a page on another origin
cannot make a browser read it through DNS rebinding). On a VPS, reach it over an
SSH tunnel (`ssh -L 8765:127.0.0.1:8765 host`) rather than opening the port.

    python3 scripts/office/serve.py                    # http://127.0.0.1:8765
    python3 scripts/office/serve.py --team-home /srv/team --port 9000

    GET /api/health
    GET /api/snapshot?mode=claude|team[&at=<epoch>][&feature=<id>][&demo=<name>]

`office/dist` is built by `npm run build` in `office/`; without it the API still
works and `/` explains how to build the page.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import mimetypes
import re
import socket
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlsplit

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import snapshot  # noqa: E402  (sits beside this file)

DEFAULT_PORT = 8765
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "[::1]"}
FEATURE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
# Far enough either side of "now" for any real checkout; stops a huge number reaching datetime.
EPOCH_RANGE = (0.0, 4_102_444_800.0)
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
                                "script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; "
                                "form-action 'none'"),
}
MIME_FALLBACK = {".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css", ".json": "application/json",
                 ".svg": "image/svg+xml", ".woff2": "font/woff2", ".html": "text/html", ".map": "application/json"}
NO_BUILD_PAGE = """<!doctype html><meta charset="utf-8"><title>Agent office</title>
<body style="font:16px system-ui;max-width:42rem;margin:3rem auto;padding:0 1rem">
<h1>The page is not built yet</h1>
<p>The data is available at <a href="/api/snapshot?mode=claude">/api/snapshot</a>. Build the page once:</p>
<pre>cd office &amp;&amp; npm ci &amp;&amp; npm run build</pre>
<p>then reload. See docs/office-dashboard.md.</p>
"""


class LiveSource:
    """The real checkout's inputs, with the event log parsed again only when the file changed."""

    def __init__(self, root: Path, team_home: Path) -> None:
        self.root, self.team_home = root, team_home
        self._lock = threading.Lock()
        self._events_key: tuple[int, int] | None = None
        self._events: list[dict[str, Any]] = []

    def events(self) -> list[dict[str, Any]]:
        path = self.root / snapshot.EVENTS_RELATIVE
        key = []
        for candidate in (path.with_name(path.name + ".1"), path):
            try:
                stat = candidate.stat()
                key += [stat.st_mtime_ns, stat.st_size]
            except OSError:
                key += [0, 0]
        with self._lock:
            if tuple(key) != self._events_key:
                self._events = snapshot.read_events(path)
                self._events_key = tuple(key)
            return self._events

    def claude_inputs(self) -> dict[str, Any]:
        return {"events": self.events(), "ledger": snapshot.read_ledger(self.root),
                "agent_files": snapshot.read_agent_files(self.root)}

    def build(self, mode: str, at: float | None, feature: str | None) -> dict[str, Any]:
        roster = snapshot.load_roster()
        now = time.time()
        if mode == "claude":
            return snapshot.build_claude(self.claude_inputs(), roster, now if at is None else at, live=at is None)
        return snapshot.build_team(snapshot.load_team_features(self.team_home), roster, now, feature_id=feature, live=True)


class QueryError(ValueError):
    """The request's parameters are not acceptable; the message is safe to show."""


def parse_query(query: str) -> dict[str, Any]:
    params = {key: values[-1] for key, values in parse_qs(query, keep_blank_values=False).items()}
    mode = params.get("mode", "claude")
    if mode not in snapshot.MODES:
        raise QueryError("mode must be claude or team")
    parsed: dict[str, Any] = {"mode": mode, "at": None, "feature": None, "demo": None}
    if "at" in params:
        try:
            at = float(params["at"])
        except ValueError:
            raise QueryError("at must be a number (epoch seconds)") from None
        if not EPOCH_RANGE[0] <= at <= EPOCH_RANGE[1]:  # also rejects nan
            raise QueryError("at is outside the supported range")
        parsed["at"] = at
    if "feature" in params:
        if not FEATURE_RE.fullmatch(params["feature"]):
            raise QueryError("feature is not a valid feature id")
        parsed["feature"] = params["feature"]
    if "demo" in params:
        if params["demo"] not in snapshot.demo_names():
            raise QueryError("unknown demo")
        parsed["demo"] = params["demo"]
    return parsed


HOST_RE = re.compile(r"(\[[0-9a-f:.]+\]|[a-z0-9.-]+)(?::\d{1,5})?")


def host_allowed(header: str | None, extra: set[str]) -> bool:
    """The Host header names this machine: loopback, or a host the operator listed."""
    if not header:
        return False
    found = HOST_RE.fullmatch(header.strip().lower())
    return bool(found) and (found.group(1) in LOOPBACK_HOSTS or found.group(1) in extra)


def safe_file(dist: Path, request_path: str) -> Path | None:
    """The file under `dist` for a URL path, or None for anything that is not strictly inside it."""
    relative = unquote(request_path).lstrip("/")
    if "\x00" in relative or "\\" in relative:
        return None
    try:
        root = dist.resolve()
        target = (root / relative).resolve()
        target.relative_to(root)
    except (OSError, ValueError):
        return None
    return target if target.is_file() else None


class Handler(BaseHTTPRequestHandler):
    server_version = "agent-office/1"
    protocol_version = "HTTP/1.1"
    source: LiveSource
    dist: Path
    extra_hosts: set[str]
    verbose = False

    def log_message(self, fmt: str, *args: Any) -> None:
        if self.verbose:
            super().log_message(fmt, *args)

    # -- plumbing ---------------------------------------------------------

    def send(self, status: int, body: bytes, content_type: str, cache: str = "no-store", head: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def send_json(self, status: int, payload: Any, head: bool = False) -> None:
        self.send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", head=head)

    def refuse_method(self) -> None:
        self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_header("Allow", "GET, HEAD")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

    do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = refuse_method

    # -- routes -----------------------------------------------------------

    def do_HEAD(self) -> None:
        self.route(head=True)

    def do_GET(self) -> None:
        self.route(head=False)

    def route(self, head: bool) -> None:
        if not host_allowed(self.headers.get("Host"), self.extra_hosts):
            return self.send_json(HTTPStatus.FORBIDDEN, {"error": "host_not_allowed"}, head)
        parts = urlsplit(self.path)
        if parts.path == "/api/health":
            return self.send_json(HTTPStatus.OK, {"ok": True, "version": snapshot.SNAPSHOT_VERSION,
                                                  "demos": snapshot.demo_names()}, head)
        if parts.path == "/api/snapshot":
            return self.snapshot(parts.query, head)
        if parts.path.startswith("/api/"):
            return self.send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"}, head)
        self.static(parts.path, head)

    def snapshot(self, query: str, head: bool) -> None:
        try:
            params = parse_query(query)
        except QueryError as exc:
            return self.send_json(HTTPStatus.BAD_REQUEST, {"error": "bad_request", "detail": str(exc)}, head)
        try:
            if params["demo"]:
                demo = snapshot.load_demo(params["demo"])
                at = params["at"] if params["at"] is not None else demo["span"]["start"]
                snap = snapshot.build_demo(params["demo"], snapshot.load_roster(), at)
            else:
                snap = self.source.build(params["mode"], params["at"], params["feature"])
        except Exception as exc:  # a broken data file must not take the page down
            print(f"office: snapshot failed: {exc!r}", file=sys.stderr)
            return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "snapshot_failed"}, head)
        self.send_json(HTTPStatus.OK, snap, head)

    def static(self, path: str, head: bool) -> None:
        if not self.dist.is_dir():
            return self.send(HTTPStatus.OK, NO_BUILD_PAGE.encode("utf-8"), "text/html; charset=utf-8", head=head)
        target = safe_file(self.dist, path)
        if target is None:
            # A client-side route has no extension; anything that looks like a file is a real 404.
            if Path(unquote(path)).suffix:
                return self.send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"}, head)
            target = safe_file(self.dist, "index.html")
            if target is None:
                return self.send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"}, head)
        kind = mimetypes.guess_type(target.name)[0] or MIME_FALLBACK.get(target.suffix, "application/octet-stream")
        kind = MIME_FALLBACK.get(target.suffix, kind)
        hashed = "assets" in target.relative_to(self.dist.resolve()).parts  # Vite names these by content hash
        cache = "public, max-age=31536000, immutable" if hashed else "no-store"
        if kind.startswith("text/") or kind in ("application/json", "image/svg+xml"):
            kind += "; charset=utf-8" if "charset" not in kind else ""
        self.send(HTTPStatus.OK, target.read_bytes(), kind, cache=cache, head=head)


class IPv6Server(ThreadingHTTPServer):
    """`ThreadingHTTPServer` is an IPv4 socket; an IPv6 address needs the other family."""

    address_family = socket.AF_INET6


def make_server(host: str, port: int, root: Path, team_home: Path, dist: Path, extra_hosts: set[str] | None = None,
                verbose: bool = False) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (Handler,), {
        "source": LiveSource(root, team_home), "dist": dist, "extra_hosts": {item.lower() for item in (extra_hosts or set())},
        "verbose": verbose,
    })
    # Only an IPv6 address has a colon; `main` hands a name over as the address it resolves to.
    server_class = IPv6Server if ":" in host else ThreadingHTTPServer
    server = server_class((host, port), handler)
    server.daemon_threads = True
    return server


def is_loopback_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Loopback, an IPv4-mapped IPv6 address (`::ffff:127.0.0.1`) judged by the IPv4 address inside it.

    Python 3.13 does that itself; the CI interpreter (3.10) answers False, and the bind check must not
    depend on which one runs it.
    """
    mapped = getattr(address, "ipv4_mapped", None)
    return address.is_loopback or (mapped is not None and mapped.is_loopback)


def addresses_of(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """The addresses `host` names, IPv4 first: a literal is parsed, a name is resolved (one lookup).

    Empty when it names none. A scope id (`fe80::1%eth0`) is not part of the address.
    """
    try:
        return [ipaddress.ip_address(host.split("%", 1)[0])]
    except ValueError:
        pass
    try:
        found = {ipaddress.ip_address(item[4][0].split("%", 1)[0]) for item in socket.getaddrinfo(host, None)}
    except (OSError, UnicodeError, ValueError):
        return []
    return sorted(found, key=lambda address: (address.version != 4, address))


def loopback_bind(host: str) -> str | None:
    """The numeric loopback address to bind for `host`, or None when `host` is not loopback.

    A name is trusted only when every address it resolves to is loopback: a spelling proves nothing
    (`127.office.example` is an ordinary name), and a name that does not resolve is refused. The caller
    binds the address returned, never the name, so the socket cannot resolve it again to something else
    between this check and the bind. A name that has both families gets its IPv4 address, which is what
    the server bound before names were checked.
    """
    addresses = addresses_of(host)
    if not addresses or not all(is_loopback_address(address) for address in addresses):
        return None
    return str(addresses[0])


def remote_bind(host: str) -> str:
    """What to bind for a host that is not loopback (`--allow-remote`).

    A name becomes its numeric address, so the socket family follows what the name resolves to and not
    how it is spelled (an IPv6-only name has no colon). A literal, or a name that does not resolve, is
    bound as typed: the first keeps its scope id, the second fails in `bind` with the resolver's message.
    """
    try:
        ipaddress.ip_address(host.split("%", 1)[0])
    except ValueError:
        addresses = addresses_of(host)
        return str(addresses[0]) if addresses else host
    return host


def ipv6_text(address: ipaddress.IPv6Address) -> str:
    """An IPv6 address the way a browser writes it in a URL (WHATWG): lower-case hex groups, the first
    longest run of two or more zero groups as `::`, and never a dotted quad (`::ffff:7f00:1`)."""
    groups = [(address.packed[i] << 8) | address.packed[i + 1] for i in range(0, 16, 2)]
    best_start = best_length = 0
    index = 0
    while index < 8:
        if groups[index]:
            index += 1
            continue
        run = index
        while run < 8 and not groups[run]:
            run += 1
        if run - index > best_length:
            best_start, best_length = index, run - index
        index = run
    if best_length < 2:
        return ":".join(f"{group:x}" for group in groups)
    head = ":".join(f"{group:x}" for group in groups[:best_start])
    tail = ":".join(f"{group:x}" for group in groups[best_start + best_length:])
    return f"{head}::{tail}"


def host_header_name(host: str) -> str:
    """How a browser writes `host` in a Host header: lower case, an IPv6 literal in brackets and in the
    form the browser normalizes it to (`::ffff:127.0.0.1` is sent as `[::ffff:7f00:1]`)."""
    host = host.split("%", 1)[0].lower()
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return host
    return f"[{ipv6_text(address)}]" if address.version == 6 else str(address)


def url_host(host: str) -> str:
    """`host` as a URL spells it: the Host header form, plus the zone id of an IPv6 literal
    percent-encoded (RFC 6874), which a link-local address cannot be reached without."""
    name = host_header_name(host)
    zone = host.partition("%")[2]
    return f"{name[:-1]}%25{quote(zone, safe='')}]" if zone and name.startswith("[") else name


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--root", type=Path, default=snapshot.repo_root(), help="checkout holding artifacts/handoff")
    parser.add_argument("--team-home", type=Path, default=snapshot.team_home(), help="team.py home ($TEAM_HOME or /srv/team)")
    parser.add_argument("--dist", type=Path, default=None, help="built page (default: office/dist in the checkout)")
    parser.add_argument("--allow-remote", action="store_true", help="bind to a non-loopback address (there is no login)")
    parser.add_argument("--allow-host", action="append", default=[], help="an extra Host header to accept (repeatable)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv[1:])
    bind = loopback_bind(args.host)
    if bind is None and not args.allow_remote:
        print(f"office: refusing to bind {args.host}: the dashboard has no login. Use an SSH tunnel to reach a loopback "
              "bind, or pass --allow-remote if the network is yours alone.", file=sys.stderr)
        return 2
    dist = args.dist or args.root / "office" / "dist"
    extra_hosts = set(args.allow_host)
    if bind is not None:
        extra_hosts.add(host_header_name(args.host))  # the URL printed below is the one the browser will send
    server = make_server(bind or remote_bind(args.host), args.port, args.root, args.team_home, dist, extra_hosts, args.verbose)
    shown = url_host(args.host)
    print(f"agent office on http://{shown}:{server.server_address[1]}/  (read-only; Ctrl-C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
