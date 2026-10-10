"""Tool Marketing Studio — the app. Run `python app.py` (or double-click start-app.bat).

Opens http://127.0.0.1:8765 in your browser. The server listens on this computer only:
it holds your API keys and can publish to your Facebook Page.
"""

import argparse
import sys
import threading
import webbrowser

from mkt.model import ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Tool Marketing Studio app")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser")
    args = parser.parse_args()
    try:
        import uvicorn

        from mkt.server import create_app
    except ImportError as exc:
        print(f"Missing package ({exc.name}). Run: pip install -r requirements.txt")
        return 1
    if not (ROOT / "web" / "dist" / "index.html").exists():
        print("web/dist is missing. Build it once: cd web && npm install && npm run build")
        return 1
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Tool Marketing Studio → {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    # 127.0.0.1 only — never 0.0.0.0: anyone on the same Wi-Fi could otherwise use your keys.
    uvicorn.run(create_app(ROOT, port=args.port), host="127.0.0.1", port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    sys.exit(main())
