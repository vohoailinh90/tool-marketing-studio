"""Tracked links: every post, language and platform gets its own, so a sign-up can be
traced to the post that earned it. Links are never written into post text: a post says
`{link}` and the campaign's `links:` decides the URL."""

from __future__ import annotations

from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

PLACEHOLDER = "REPLACE_ME"


def is_configured(url) -> bool:
    return isinstance(url, str) and url.startswith(("https://", "http://")) and PLACEHOLDER not in url


def source_tag(campaign: str, post: str, lang: str, platform: str) -> str:
    return f"{campaign}-{post}-{lang}-{platform}"


def tracked_link(url, *, campaign: str, post: str, lang: str, platform: str, utm: dict | None = None) -> str:
    """Tag `url` for one post, language and platform; "" while the URL is still a placeholder.

    A URL containing `{source}` (a Google Forms pre-filled link, say) gets the tag
    substituted there. Any other URL gets utm_* parameters, without overriding a
    parameter it already carries.
    """
    if not is_configured(url):
        return ""
    tag = source_tag(campaign, post, lang, platform)
    if "{source}" in url:
        return url.replace("{source}", quote(tag))
    utm = utm or {}
    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    present = {key for key, _ in query}
    wanted = {
        "utm_source": platform,
        "utm_medium": utm.get("medium", "social"),
        "utm_campaign": utm.get("campaign", campaign),
        "utm_content": f"{post}-{lang}",
    }
    query += [(key, value) for key, value in wanted.items() if key not in present]
    return urlunsplit(parts._replace(query=urlencode(query)))


def post_link(campaign, post, platform: str) -> str:
    """The tracked link a post points at; `link:` in the post names a key of the campaign's `links:`."""
    target = post.data.get("link", "survey")
    if not target:
        return ""
    url = (campaign.data.get("links") or {}).get(target)
    return tracked_link(url, campaign=campaign.slug, post=post.id, lang=post.lang,
                        platform=platform, utm=campaign.data.get("utm"))


def qr_svg(link: str) -> str:
    if not link:
        return ""
    import segno  # imported here so checks and tests do not need it
    return segno.make(link, error="m").svg_inline(scale=10, border=0, dark="#0f172a", omitsize=True)
