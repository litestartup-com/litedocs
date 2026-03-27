"""Markdown parsing for navigation, sidebar, and content pages."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import frontmatter
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from litedocs.models import NavNode, PageContext, SidebarNode, TocHeading

# ---------------------------------------------------------------------------
# Shared markdown-it instance for content rendering
# ---------------------------------------------------------------------------

_md: MarkdownIt | None = None


def _get_md() -> MarkdownIt:
    """Return a lazily-initialized markdown-it instance with plugins."""
    global _md
    if _md is None:
        _md = MarkdownIt("commonmark", {"html": True, "typographer": True})
        _md.enable(["table", "strikethrough"])
        footnote_plugin(_md)
        tasklists_plugin(_md)
    return _md


# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# Matches: [Label](href)
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
# Matches: **Bold Text**
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
# Matches: [badge:Text]
_BADGE_RE = re.compile(r"\[badge:([^\]]+)\]")
# Matches: [method:GET]
_METHOD_RE = re.compile(r"\[method:([A-Z]+)\]")


def _is_external(href: str) -> bool:
    """Check if a href is an external URL."""
    return href.startswith("http://") or href.startswith("https://")


def _normalize_href(href: str, base_prefix: str) -> str:
    """Normalize a relative .md href into a URL path.

    Args:
        href: The raw href from markdown (e.g. "getting-started.md", "guide/index.md").
        base_prefix: The URL prefix to prepend (e.g. "/en", "/en/api").

    Returns:
        Normalized URL path (e.g. "/en/getting-started", "/en/api/").
    """
    if _is_external(href) or href.startswith("/") or href.startswith("#"):
        return href

    # Remove .md extension
    slug = href.removesuffix(".md")

    # index and README map to directory
    if slug.endswith("/index") or slug.endswith("/README"):
        slug = slug.rsplit("/", 1)[0]
    elif slug in ("index", "README"):
        slug = ""

    base = base_prefix.rstrip("/")
    if slug:
        return f"{base}/{slug}"
    return f"{base}/"


# ---------------------------------------------------------------------------
# Navigation (_nav.md) parsing
# ---------------------------------------------------------------------------


def parse_nav(
    content: str, locale: str, doc_slug: str = "", base_path: str = "",
) -> list[NavNode]:
    """Parse _nav.md content into a list of NavNode items.

    Args:
        content: Raw Markdown content of _nav.md.
        locale: The locale code (used for URL prefix).
        doc_slug: The doc directory slug for multi-doc URL prefix.
        base_path: URL prefix for reverse proxy (e.g. "/docs").

    Returns:
        List of NavNode items for the top navigation bar.
    """
    nodes: list[NavNode] = []
    base_prefix = f"{base_path}/{doc_slug}/{locale}" if doc_slug else f"{base_path}/{locale}"

    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue

        item_text = line[2:].strip()

        # Extract badge if present
        badge: str | None = None
        badge_match = _BADGE_RE.search(item_text)
        if badge_match:
            badge = badge_match.group(1)
            item_text = _BADGE_RE.sub("", item_text).strip()

        # Try to match a link
        link_match = _LINK_RE.search(item_text)
        if link_match:
            label = link_match.group(1)
            href = link_match.group(2)
            is_ext = _is_external(href)
            resolved_href = href if is_ext else _normalize_href(href, base_prefix)
            nodes.append(
                NavNode(
                    label=label,
                    href=resolved_href,
                    is_external=is_ext,
                    badge=badge,
                )
            )
        else:
            # Plain text nav item (no link)
            nodes.append(NavNode(label=item_text, badge=badge))

    return nodes


# ---------------------------------------------------------------------------
# Sidebar (_sidebar.md) parsing
# ---------------------------------------------------------------------------


def parse_sidebar(
    content: str,
    locale: str,
    product: str | None = None,
    doc_slug: str = "",
    base_path: str = "",
) -> list[SidebarNode]:
    """Parse _sidebar.md content into a tree of SidebarNode items.

    Supports nested lists via 2-space indentation, bold group headers,
    badges, and method tags.

    Args:
        content: Raw Markdown content of _sidebar.md.
        locale: The locale code (used for URL prefix).
        product: The product name if this is a product-level sidebar.
        doc_slug: The doc directory slug for multi-doc URL prefix.
        base_path: URL prefix for reverse proxy (e.g. "/docs").

    Returns:
        List of top-level SidebarNode items (with nested children).
    """
    prefix = f"{base_path}/{doc_slug}/{locale}" if doc_slug else f"{base_path}/{locale}"
    if product:
        base_prefix = f"{prefix}/{product}"
    else:
        base_prefix = prefix

    lines = content.splitlines()
    root_nodes: list[SidebarNode] = []

    # Stack: list of (indent_level, nodes_list) for building the tree
    # We use a stack approach to handle nesting
    stack: list[tuple[int, list[SidebarNode]]] = [(-1, root_nodes)]

    for line in lines:
        # Skip empty lines
        stripped = line.strip()
        if not stripped or not stripped.startswith("- "):
            continue

        # Calculate indentation level (number of leading spaces / 2)
        indent = len(line) - len(line.lstrip())
        level = indent // 2

        item_text = stripped[2:].strip()

        # Extract badge
        badge: str | None = None
        badge_match = _BADGE_RE.search(item_text)
        if badge_match:
            badge = badge_match.group(1)
            item_text = _BADGE_RE.sub("", item_text).strip()

        # Extract method tag
        method: str | None = None
        method_match = _METHOD_RE.search(item_text)
        if method_match:
            method = method_match.group(1)
            item_text = _METHOD_RE.sub("", item_text).strip()

        # Check if it's a bold group header: **Title**
        bold_match = _BOLD_RE.match(item_text)
        if bold_match:
            node = SidebarNode(
                label=bold_match.group(1),
                is_group=True,
                badge=badge,
            )
        else:
            # Try link
            link_match = _LINK_RE.search(item_text)
            if link_match:
                label = link_match.group(1)
                href = link_match.group(2)
                is_ext = _is_external(href)
                resolved_href = href if is_ext else _normalize_href(href, base_prefix)
                node = SidebarNode(
                    label=label,
                    href=resolved_href,
                    is_external=is_ext,
                    badge=badge,
                    method=method,
                )
            else:
                # Plain text group (will become a group if it has children)
                node = SidebarNode(
                    label=item_text,
                    is_group=True,
                    badge=badge,
                    method=method,
                )

        # Find the correct parent for this node based on indentation
        while len(stack) > 1 and stack[-1][0] >= level:
            stack.pop()

        # Append to the current parent's children list
        parent_children = stack[-1][1]
        parent_children.append(node)

        # Push this node's children list onto the stack
        stack.append((level, node.children))

    return root_nodes


# ---------------------------------------------------------------------------
# Content page parsing
# ---------------------------------------------------------------------------

# Callout / admonition pattern: > [!TYPE]
_CALLOUT_RE = re.compile(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", re.MULTILINE)

_CALLOUT_ICONS = {
    "NOTE": "info",
    "TIP": "lightbulb",
    "IMPORTANT": "message-circle",
    "WARNING": "alert-triangle",
    "CAUTION": "octagon-x",
}

_CALLOUT_CLASSES = {
    "NOTE": "ld-callout--note",
    "TIP": "ld-callout--tip",
    "IMPORTANT": "ld-callout--important",
    "WARNING": "ld-callout--warning",
    "CAUTION": "ld-callout--caution",
}


def _preprocess_callouts(content: str) -> str:
    """Convert GitHub-style callouts to HTML before markdown-it processing.

    Transforms:
        > [!NOTE]
        > Some content here.

    Into a blockquote with a data attribute that can be styled via CSS.
    """
    lines = content.split("\n")
    result: list[str] = []
    i = 0

    while i < len(lines):
        match = _CALLOUT_RE.match(lines[i])
        if match:
            callout_type = match.group(1)
            css_class = _CALLOUT_CLASSES.get(callout_type, "ld-callout--note")
            icon = _CALLOUT_ICONS.get(callout_type, "info")

            # Collect all subsequent lines that start with >
            callout_lines: list[str] = []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                # Remove the leading > and optional space
                line_content = lines[i][1:].lstrip(" ") if len(lines[i]) > 1 else ""
                callout_lines.append(line_content)
                i += 1

            body = "\n".join(callout_lines).strip()
            md = _get_md()
            body_html = md.render(body)

            result.append(
                f'<div class="ld-callout {css_class}" data-callout="{callout_type.lower()}">'
                f'<div class="ld-callout-title">'
                f'<span class="ld-callout-icon" data-icon="{icon}"></span>'
                f"{callout_type.title()}"
                f"</div>"
                f'<div class="ld-callout-body">{body_html}</div>'
                f"</div>\n"
            )
        else:
            result.append(lines[i])
            i += 1

    return "\n".join(result)


# Heading extraction regex (from rendered HTML)
_HEADING_RE = re.compile(r"<h([2-4])\s+id=\"([^\"]+)\"[^>]*>(.*?)</h\1>", re.DOTALL)
# Strip HTML tags for clean heading text
_TAG_RE = re.compile(r"<[^>]+>")


def _add_heading_ids(html: str) -> tuple[str, list[TocHeading]]:
    """Add id attributes to headings and extract TOC entries.

    markdown-it-py does not add IDs to headings by default, so we post-process
    the HTML to add them.
    """
    toc: list[TocHeading] = []
    seen_ids: dict[str, int] = {}

    def _slugify(text: str) -> str:
        """Convert heading text to a URL-friendly slug."""
        text = _TAG_RE.sub("", text).strip()
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s]+", "-", text)
        text = text.strip("-")
        return text

    def _replacer(match: re.Match) -> str:
        level = int(match.group(1))
        raw_text = match.group(2)  # This will be the content between tags
        full_match = match.group(0)

        # For headings that already have id, extract text differently
        return full_match

    # First pass: find headings without IDs and add them
    heading_no_id = re.compile(r"<h([1-6])(?![^>]*\bid=)(.*?)>(.*?)</h\1>", re.DOTALL)

    def _add_id(match: re.Match) -> str:
        level = int(match.group(1))
        attrs = match.group(2)
        text = match.group(3)
        clean_text = _TAG_RE.sub("", text).strip()
        slug = _slugify(clean_text)

        if not slug:
            slug = "heading"

        # Handle duplicate IDs
        if slug in seen_ids:
            seen_ids[slug] += 1
            slug = f"{slug}-{seen_ids[slug]}"
        else:
            seen_ids[slug] = 0

        # Add to TOC (h2-h4 only)
        if 2 <= level <= 4:
            toc.append(TocHeading(id=slug, text=clean_text, level=level))

        return f'<h{level}{attrs} id="{slug}">{text}</h{level}>'

    html = heading_no_id.sub(_add_id, html)

    return html, toc


def parse_page(file_path: Path, locale: str, slug: str, product: str | None = None) -> PageContext:
    """Parse a Markdown content file into a PageContext.

    Args:
        file_path: Path to the .md file.
        locale: The locale code.
        slug: The resolved URL slug.
        product: The product name if applicable.

    Returns:
        A PageContext with parsed frontmatter, HTML content, and TOC.
    """
    raw = file_path.read_text(encoding="utf-8")

    # Parse frontmatter
    post = frontmatter.loads(raw)
    fm: dict[str, Any] = dict(post.metadata)
    body = post.content

    # Preprocess callouts
    body = _preprocess_callouts(body)

    # Render markdown to HTML
    md = _get_md()
    html = md.render(body)

    # Add heading IDs and extract TOC
    html, toc = _add_heading_ids(html)

    # Extract title: frontmatter > first H1 > filename
    title = fm.get("title", "")
    if not title:
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
        if h1_match:
            title = _TAG_RE.sub("", h1_match.group(1)).strip()
        else:
            title = slug.split("/")[-1].replace("-", " ").title() if slug else "Index"

    # Extract description: frontmatter > first 160 chars
    description = fm.get("description", "")
    if not description:
        plain = _TAG_RE.sub("", html).strip()
        description = plain[:160].rsplit(" ", 1)[0] if len(plain) > 160 else plain

    return PageContext(
        slug=slug,
        locale=locale,
        product=product,
        title=title,
        description=description,
        icon=fm.get("icon"),
        frontmatter=fm,
        toc=toc,
        html_content=html,
    )


def load_nav(
    locale_dir: Path, locale: str, doc_slug: str = "", base_path: str = "",
) -> list[NavNode]:
    """Load and parse _nav.md from a locale directory.

    Returns an empty list if the file does not exist.
    """
    nav_file = locale_dir / "_nav.md"
    if not nav_file.is_file():
        return []
    content = nav_file.read_text(encoding="utf-8")
    return parse_nav(content, locale, doc_slug=doc_slug, base_path=base_path)


def load_sidebar(
    locale_dir: Path,
    locale: str,
    product: str | None = None,
    doc_slug: str = "",
    base_path: str = "",
) -> list[SidebarNode]:
    """Load and parse _sidebar.md with fallback resolution.

    Resolution order:
        1. {locale_dir}/{product}/_sidebar.md (if product specified)
        2. {locale_dir}/_sidebar.md
        3. Empty list (fallback)

    Returns:
        List of SidebarNode items.
    """
    if product:
        product_sidebar = locale_dir / product / "_sidebar.md"
        if product_sidebar.is_file():
            content = product_sidebar.read_text(encoding="utf-8")
            return parse_sidebar(
                content, locale, product, doc_slug=doc_slug, base_path=base_path,
            )

    locale_sidebar = locale_dir / "_sidebar.md"
    if locale_sidebar.is_file():
        content = locale_sidebar.read_text(encoding="utf-8")
        return parse_sidebar(content, locale, doc_slug=doc_slug, base_path=base_path)

    return []
