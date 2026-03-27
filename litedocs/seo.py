"""SEO utilities: sitemap, robots.txt, llms.txt, meta tags for LiteDocs."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring

import frontmatter

from litedocs.scanner import PageInfo, SiteStructure

_TAG_RE = re.compile(r"<[^>]+>")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _collect_pages(
    structure: SiteStructure,
    available_locales: list[str],
) -> list[PageInfo]:
    """Collect all content pages across locales and products."""
    pages: list[PageInfo] = []
    for locale_code in available_locales:
        locale_info = structure.locales.get(locale_code)
        if locale_info is None:
            continue
        pages.extend(locale_info.pages)
        for product in locale_info.products.values():
            pages.extend(product.pages)
    return pages


def _read_frontmatter(page: PageInfo) -> dict[str, Any]:
    """Read frontmatter from a page file. Returns empty dict on failure."""
    try:
        raw = page.file_path.read_text(encoding="utf-8")
        post = frontmatter.loads(raw)
        return dict(post.metadata)
    except Exception:
        return {}


def _is_noindex(page: PageInfo) -> bool:
    """Check if a page has noindex set in frontmatter."""
    fm = _read_frontmatter(page)
    return bool(fm.get("noindex", False))


def _page_url(site_url: str, doc_slug: str, page: PageInfo) -> str:
    """Build the full canonical URL for a page."""
    base = site_url.rstrip("/")
    slug_part = f"/{page.slug}" if page.slug else "/"
    return f"{base}/{doc_slug}/{page.locale}{slug_part}"


def _page_lastmod(page: PageInfo) -> str:
    """Get the last modified date of a page file in YYYY-MM-DD format."""
    try:
        mtime = page.file_path.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def _strip_html(html: str) -> str:
    """Strip HTML tags and collapse whitespace."""
    text = _TAG_RE.sub("", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _page_plain_text(page: PageInfo) -> str:
    """Read a page and return its plain text content (stripped markdown/html)."""
    try:
        raw = page.file_path.read_text(encoding="utf-8")
        post = frontmatter.loads(raw)
        # Simple: strip markdown formatting for plain text
        text = post.content
        # Remove common markdown syntax
        text = re.sub(r"#{1,6}\s+", "", text)  # headings
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # bold
        text = re.sub(r"\*(.+?)\*", r"\1", text)  # italic
        text = re.sub(r"`(.+?)`", r"\1", text)  # inline code
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)  # images
        text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)  # blockquotes
        text = re.sub(r"^-\s+", "", text, flags=re.MULTILINE)  # list items
        text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)  # ordered list
        text = re.sub(r"```[\s\S]*?```", "", text)  # code blocks
        text = re.sub(r"\n{3,}", "\n\n", text)  # collapse blank lines
        return text.strip()
    except Exception:
        return ""


def _page_title(page: PageInfo) -> str:
    """Extract the title from frontmatter or slug."""
    fm = _read_frontmatter(page)
    title = fm.get("title", "")
    if not title:
        title = page.slug.split("/")[-1].replace("-", " ").title() if page.slug else "Index"
    return title


def _page_description(page: PageInfo) -> str:
    """Extract the description from frontmatter or first 160 chars."""
    fm = _read_frontmatter(page)
    desc = fm.get("description", "")
    if not desc:
        text = _page_plain_text(page)
        desc = text[:160].rsplit(" ", 1)[0] if len(text) > 160 else text
    return desc


# ---------------------------------------------------------------------------
# Sitemap XML generation
# ---------------------------------------------------------------------------


def generate_sitemap(
    site_url: str,
    doc_slug: str,
    structure: SiteStructure,
    available_locales: list[str],
) -> str:
    """Generate a sitemap.xml string for a single doc.

    Args:
        site_url: The base URL of the site (e.g. "https://docs.example.com").
        doc_slug: The doc directory slug.
        structure: The scanned site structure.
        available_locales: List of available locale codes.

    Returns:
        XML string for sitemap.xml.
    """
    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
    XHTML_NS = "http://www.w3.org/1999/xhtml"

    urlset = Element("urlset")
    urlset.set("xmlns", SITEMAP_NS)
    urlset.set("xmlns:xhtml", XHTML_NS)

    all_pages = _collect_pages(structure, available_locales)

    for page in all_pages:
        if _is_noindex(page):
            continue

        url_el = SubElement(urlset, "url")
        loc = SubElement(url_el, "loc")
        loc.text = _page_url(site_url, doc_slug, page)

        lastmod = SubElement(url_el, "lastmod")
        lastmod.text = _page_lastmod(page)

        changefreq = SubElement(url_el, "changefreq")
        changefreq.text = "weekly"

        priority = SubElement(url_el, "priority")
        priority.text = "1.0" if not page.slug else "0.8"

        # Add alternate language links
        for alt_locale in available_locales:
            if alt_locale == page.locale:
                continue
            xhtml_link = SubElement(url_el, "xhtml:link")
            xhtml_link.set("rel", "alternate")
            xhtml_link.set("hreflang", alt_locale)
            slug_part = f"/{page.slug}" if page.slug else "/"
            xhtml_link.set("href", f"{site_url.rstrip('/')}/{doc_slug}/{alt_locale}{slug_part}")

    xml_bytes = tostring(urlset, encoding="unicode", xml_declaration=False)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_bytes}'


# ---------------------------------------------------------------------------
# robots.txt generation
# ---------------------------------------------------------------------------


def generate_robots_txt(site_url: str) -> str:
    """Generate robots.txt content.

    Args:
        site_url: The base URL of the site.

    Returns:
        robots.txt content string.
    """
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {site_url.rstrip('/')}/sitemap.xml",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# llms.txt generation
# ---------------------------------------------------------------------------


def generate_llms_txt(
    site_title: str,
    site_description: str,
    site_url: str,
    doc_slugs_and_structures: list[tuple[str, SiteStructure, list[str]]],
) -> str:
    """Generate llms.txt — a structured index of all documentation.

    Args:
        site_title: Title to display at the top.
        site_description: Site description.
        site_url: Base URL.
        doc_slugs_and_structures: List of (doc_slug, structure, available_locales).

    Returns:
        llms.txt content string.
    """
    lines: list[str] = [
        f"# {site_title}",
        f"> {site_description}" if site_description else "",
        "",
        "## Docs",
    ]

    for doc_slug, structure, available_locales in doc_slugs_and_structures:
        all_pages = _collect_pages(structure, available_locales)
        for page in all_pages:
            if _is_noindex(page):
                continue
            title = _page_title(page)
            desc = _page_description(page)
            url = _page_url(site_url, doc_slug, page)
            desc_part = f": {desc}" if desc else ""
            lines.append(f"- [{title}]({url}){desc_part}")

    return "\n".join(lines)


def generate_llms_full_txt(
    site_title: str,
    doc_slugs_and_structures: list[tuple[str, SiteStructure, list[str]]],
) -> str:
    """Generate llms-full.txt — full plain text content of all pages.

    Args:
        site_title: Title to display at the top.
        doc_slugs_and_structures: List of (doc_slug, structure, available_locales).

    Returns:
        llms-full.txt content string.
    """
    sections: list[str] = [f"# {site_title}\n"]

    for doc_slug, structure, available_locales in doc_slugs_and_structures:
        all_pages = _collect_pages(structure, available_locales)
        for page in all_pages:
            if _is_noindex(page):
                continue
            title = _page_title(page)
            text = _page_plain_text(page)
            if text:
                sections.append(f"## {title}\n\n{text}\n")

    return "\n".join(sections)
