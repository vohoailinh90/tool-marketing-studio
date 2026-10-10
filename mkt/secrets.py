"""API credentials: read from the environment or a local `.env` file, never from YAML,
never written by the studio, and redacted from every message it prints."""

from __future__ import annotations

import os
from pathlib import Path

KEYS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "FB_PAGE_ID", "FB_PAGE_TOKEN", "FB_GRAPH_VERSION")
SECRET_KEYS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "FB_PAGE_TOKEN")


def load_env(root: Path) -> None:
    """Load `KEY=VALUE` lines from `<root>/.env` into os.environ without overriding what is set."""
    path = root / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip().removeprefix("export ").strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def secret_values() -> list[str]:
    return [value for value in (get(key) for key in SECRET_KEYS) if len(value) >= 6]


def redact(text, secrets: list[str] | None = None) -> str:
    """Replace every exact secret value with ***. Exact values, not patterns: a token is whatever it is."""
    text = str(text)
    for value in sorted(secrets if secrets is not None else secret_values(), key=len, reverse=True):
        if value:
            text = text.replace(value, "***")
    return text
