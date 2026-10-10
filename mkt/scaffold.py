"""`studio.py new`: a brief, three positionings and a six-post campaign skeleton for a new tool."""

from __future__ import annotations

import shutil
from pathlib import Path

from .model import SLUG


class ScaffoldError(ValueError):
    pass


def _copy(source: Path, target: Path, tokens: dict[str, str]) -> list[Path]:
    made = []
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        destination = target / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in (".yaml", ".md", ".txt"):
            text = path.read_text(encoding="utf-8")
            for token, value in tokens.items():
                text = text.replace(token, value)
            destination.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(path, destination)
        made.append(destination)
    return made


def new_tool(root: Path, slug: str, name: str, repo: str = "") -> list[Path]:
    if not SLUG.match(slug):
        raise ScaffoldError("use a-z, 0-9 and - for the slug, e.g. excel-to-planner")
    tool, campaign = root / "tools" / slug, root / "campaigns" / slug
    for path in (tool, campaign):
        if path.exists():
            raise ScaffoldError(f"{path.relative_to(root)} already exists")
    tokens = {"__SLUG__": slug, "__NAME__": name.replace('"', "'"), "__REPO__": repo or "TODO owner/repo"}
    return (_copy(root / "tools" / "_template", tool, tokens)
            + _copy(root / "campaigns" / "_template", campaign, tokens))
