"""What each platform accepts. Text limits are checked by `studio.py check`, not by eye."""

from __future__ import annotations

PLATFORMS = {
    # Facebook: personal profiles and Groups cannot be posted to by API — only Pages.
    "facebook": {
        "fields": ("caption", "first_comment", "hashtags"),
        "required": ("caption",),
        "caption_limit": 63206,
        "api": "facebook_page",
    },
    "linkedin": {
        "fields": ("caption", "hashtags"),
        "required": ("caption",),
        "caption_limit": 3000,
        "api": None,           # manual pack: the API is version-gated and untestable here
    },
    "x": {
        "fields": ("thread",),
        "required": ("thread",),
        "item_limit": 280,
        "max_images": 4,
        "api": None,           # manual pack: posting by API is paid
    },
}


def hashtag_line(tags) -> str:
    return " ".join("#" + str(tag).lstrip("#").replace(" ", "") for tag in (tags or []) if str(tag).strip())


def platform_texts(platform: str, spec: dict, link: str) -> dict[str, str]:
    """The text files a platform pack carries, with `{link}` filled in (or left out when unset)."""
    def fill(text: str) -> str:
        return str(text or "").replace("{link}", link or "").rstrip() + "\n"

    if platform == "x":
        parts = [fill(item).strip() for item in spec.get("thread") or []]
        return {"x-thread.txt": "\n\n---\n\n".join(parts) + "\n"}
    caption = fill(spec.get("caption", ""))
    tags = hashtag_line(spec.get("hashtags"))
    files = {f"{platform}.txt": caption + (f"\n{tags}\n" if tags else "")}
    if spec.get("first_comment"):
        files[f"{platform}-comment.txt"] = fill(spec["first_comment"])
    return files
