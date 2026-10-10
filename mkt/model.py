"""Loads the studio's YAML: config, tool briefs and positioning, campaigns and their posts.

Layout on disk:
  tools/<tool>/brief.yaml                 language-neutral facts
  tools/<tool>/positioning/<lang>.yaml    complete positioning, written for one language
  campaigns/<slug>/campaign.yaml          languages, platforms, links, schedule, thresholds
  campaigns/<slug>/posts/<lang>/<id>.yaml one complete post in one language
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .i18n import LANGS

ROOT = Path(__file__).resolve().parent.parent
POST_STATUSES = ("draft", "ready", "posted")
TOOL_STATUSES = ("idea", "prototype", "beta", "launched")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class SpecError(ValueError):
    pass


def load_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SpecError(f"{path}: invalid YAML: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise SpecError(f"{path}: expected a mapping at the top level")
    return data


def dump_yaml(data: dict) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)


def load_config(root: Path = ROOT) -> dict:
    path = root / "studio.yaml"
    return load_yaml(path) if path.exists() else {}


@dataclass
class Post:
    id: str
    lang: str
    path: Path
    data: dict

    @property
    def status(self) -> str:
        return self.data.get("status", "draft")

    @property
    def format(self) -> str:
        return self.data.get("format", "portrait")

    @property
    def slides(self) -> list:
        slides = self.data.get("slides")
        return slides if isinstance(slides, list) else []

    @property
    def platforms(self) -> dict:
        platforms = self.data.get("platforms")
        return platforms if isinstance(platforms, dict) else {}

    @property
    def key(self) -> str:
        return f"{self.id}/{self.lang}"


@dataclass
class Campaign:
    slug: str
    root: Path
    dir: Path
    data: dict
    tool: str
    brief: dict
    positioning: dict[str, dict] = field(default_factory=dict)
    posts: list[Post] = field(default_factory=list)

    @property
    def langs(self) -> list[str]:
        return [lang for lang in (self.data.get("langs") or LANGS)]

    @property
    def platforms(self) -> list[str]:
        return list(self.data.get("platforms") or ["facebook"])

    @property
    def tool_dir(self) -> Path:
        return self.root / "tools" / self.tool

    @property
    def tool_name(self) -> str:
        return str(self.brief.get("name") or self.tool)

    @property
    def brand(self) -> dict:
        brand = self.brief.get("brand")
        return brand if isinstance(brand, dict) else {}

    @property
    def slots(self) -> list[str]:
        return sorted({post.id for post in self.posts})

    def post(self, post_id: str, lang: str) -> Post:
        for post in self.posts:
            if post.id == post_id and post.lang == lang:
                return post
        raise SpecError(f"campaign '{self.slug}' has no post '{post_id}' in '{lang}'")

    def post_path(self, post_id: str, lang: str) -> Path:
        return self.dir / "posts" / lang / f"{post_id}.yaml"

    def export_dir(self, post: Post) -> Path:
        return self.dir / "export" / post.lang / post.id


def campaign_slugs(root: Path = ROOT) -> list[str]:
    base = root / "campaigns"
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir()
                  if p.is_dir() and not p.name.startswith("_") and (p / "campaign.yaml").exists())


def tool_slugs(root: Path = ROOT) -> list[str]:
    base = root / "tools"
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir()
                  if p.is_dir() and not p.name.startswith("_") and (p / "brief.yaml").exists())


def load_brief(root: Path, tool: str) -> dict:
    path = root / "tools" / tool / "brief.yaml"
    return load_yaml(path) if path.exists() else {}


def load_positioning(root: Path, tool: str) -> dict[str, dict]:
    base = root / "tools" / tool / "positioning"
    return {lang: load_yaml(base / f"{lang}.yaml") for lang in LANGS if (base / f"{lang}.yaml").exists()}


def load_campaign(root: Path, slug: str) -> Campaign:
    if not SLUG.match(slug):
        raise SpecError(f"invalid campaign name '{slug}' (use a-z, 0-9 and -)")
    directory = root / "campaigns" / slug
    spec = directory / "campaign.yaml"
    if not spec.exists():
        raise SpecError(f"no campaign at {spec}")
    data = load_yaml(spec)
    tool = str(data.get("tool") or slug)
    if not SLUG.match(tool):
        raise SpecError(f"{spec}: invalid tool name '{tool}'")
    posts = []
    for lang in LANGS:
        for path in sorted((directory / "posts" / lang).glob("*.yaml")):
            posts.append(Post(id=path.stem, lang=lang, path=path, data=load_yaml(path)))
    return Campaign(slug=slug, root=root, dir=directory, data=data, tool=tool,
                    brief=load_brief(root, tool), positioning=load_positioning(root, tool), posts=posts)
