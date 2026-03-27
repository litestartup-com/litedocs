"""Search index builder for LiteDocs."""

from __future__ import annotations

import json
import re
from typing import Any

import frontmatter
from markdown_it import MarkdownIt

from litedocs.scanner import PageInfo, SiteStructure

_TAG_RE = re.compile(r"<[^>]+>")
_HEADING_RE = re.compile(r"<h[1-6][^>]*>(.*?)</h[1-6]>", re.DOTALL)


def _extract_headings_text(html: str) -> str:
    """Extract heading text from rendered HTML, joined by comma."""
    matches = _HEADING_RE.findall(html)
    texts = [_TAG_RE.sub("", m).strip() for m in matches]
    return ", ".join(texts)


def _render_to_html(content: str) -> str:
    """Render markdown content to HTML (lightweight, no plugins needed)."""
    md = MarkdownIt("commonmark", {"html": True})
    md.enable(["table", "strikethrough"])
    return md.render(content)


def _strip_html(html: str) -> str:
    """Strip HTML tags and collapse whitespace."""
    text = _TAG_RE.sub("", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_search_index(
    doc_slug: str,
    structure: SiteStructure,
    available_locales: list[str],
) -> list[dict[str, Any]]:
    """Build a search index for a single doc directory.

    Each entry contains: id, title, description, headings, body, locale, product.

    Args:
        doc_slug: The doc directory slug.
        structure: The scanned site structure.
        available_locales: List of available locale codes.

    Returns:
        List of search index entries.
    """
    entries: list[dict[str, Any]] = []

    for locale_code in available_locales:
        locale_info = structure.locales.get(locale_code)
        if locale_info is None:
            continue

        # Collect all pages for this locale
        pages: list[PageInfo] = list(locale_info.pages)
        for product in locale_info.products.values():
            pages.extend(product.pages)

        for page in pages:
            entry = _build_entry(page, doc_slug)
            if entry:
                entries.append(entry)

    return entries


def _build_entry(page: PageInfo, doc_slug: str) -> dict[str, Any] | None:
    """Build a single search index entry from a page."""
    try:
        raw = page.file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    post = frontmatter.loads(raw)
    fm: dict[str, Any] = dict(post.metadata)

    # Skip noindex pages
    if fm.get("noindex", False):
        return None

    # Render to HTML for heading extraction
    html = _render_to_html(post.content)

    # Extract title
    title = fm.get("title", "")
    if not title:
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
        if h1_match:
            title = _TAG_RE.sub("", h1_match.group(1)).strip()
        else:
            title = page.slug.split("/")[-1].replace("-", " ").title() if page.slug else "Index"

    # Extract description
    description = fm.get("description", "")

    # Extract headings
    headings = _extract_headings_text(html)

    # Extract body text (first 500 chars)
    body_text = _strip_html(html)
    body = body_text[:500]

    # Build the page ID as URL path
    slug_part = f"/{page.slug}" if page.slug else ""
    page_id = f"/{doc_slug}/{page.locale}{slug_part}"

    return {
        "id": page_id,
        "title": title,
        "description": description,
        "headings": headings,
        "body": body,
        "locale": page.locale,
        "product": page.product or "",
    }


def build_search_index_json(
    doc_slug: str,
    structure: SiteStructure,
    available_locales: list[str],
) -> str:
    """Build search index and return as JSON string."""
    entries = build_search_index(doc_slug, structure, available_locales)
    return json.dumps(entries, ensure_ascii=False)
