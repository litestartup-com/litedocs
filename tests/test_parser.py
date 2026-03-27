"""Tests for Markdown parsing (nav, sidebar, content pages)."""

from pathlib import Path

import pytest

from litedocs.models import NavNode, SidebarNode
from litedocs.parser import (
    _normalize_href,
    load_nav,
    load_sidebar,
    parse_nav,
    parse_page,
    parse_sidebar,
)


class TestNormalizeHref:
    """Tests for href normalization."""

    def test_simple_file(self) -> None:
        assert _normalize_href("getting-started.md", "/en") == "/en/getting-started"

    def test_index_file(self) -> None:
        assert _normalize_href("index.md", "/en") == "/en/"

    def test_readme_file(self) -> None:
        assert _normalize_href("README.md", "/en") == "/en/"

    def test_nested_index(self) -> None:
        assert _normalize_href("guide/index.md", "/en") == "/en/guide"

    def test_nested_file(self) -> None:
        assert _normalize_href("api/users.md", "/en") == "/en/api/users"

    def test_external_url(self) -> None:
        url = "https://github.com/example"
        assert _normalize_href(url, "/en") == url

    def test_absolute_path(self) -> None:
        assert _normalize_href("/sitemap.xml", "/en") == "/sitemap.xml"

    def test_anchor(self) -> None:
        assert _normalize_href("#section", "/en") == "#section"

    def test_product_prefix(self) -> None:
        assert _normalize_href("users.md", "/en/api") == "/en/api/users"


class TestParseNav:
    """Tests for _nav.md parsing."""

    def test_simple_nav(self) -> None:
        content = "- [Home](index.md)\n- [Guide](guide/index.md)\n"
        nodes = parse_nav(content, "en")
        assert len(nodes) == 2
        assert nodes[0].label == "Home"
        assert nodes[0].href == "/en/"
        assert nodes[1].label == "Guide"
        assert nodes[1].href == "/en/guide"

    def test_external_link(self) -> None:
        content = "- [GitHub](https://github.com/example)\n"
        nodes = parse_nav(content, "en")
        assert len(nodes) == 1
        assert nodes[0].is_external is True
        assert nodes[0].href == "https://github.com/example"

    def test_badge(self) -> None:
        content = "- [API](api/index.md) [badge:Beta]\n"
        nodes = parse_nav(content, "en")
        assert len(nodes) == 1
        assert nodes[0].badge == "Beta"
        assert nodes[0].label == "API"

    def test_plain_text_item(self) -> None:
        content = "- Just Text\n"
        nodes = parse_nav(content, "en")
        assert len(nodes) == 1
        assert nodes[0].label == "Just Text"
        assert nodes[0].href is None

    def test_empty_content(self) -> None:
        nodes = parse_nav("", "en")
        assert nodes == []

    def test_skips_non_list_lines(self) -> None:
        content = "# Navigation\n\n- [Home](index.md)\nSome text\n"
        nodes = parse_nav(content, "en")
        assert len(nodes) == 1


class TestParseSidebar:
    """Tests for _sidebar.md parsing."""

    def test_flat_links(self) -> None:
        content = "- [Intro](index.md)\n- [Start](start.md)\n"
        nodes = parse_sidebar(content, "en")
        assert len(nodes) == 2
        assert nodes[0].label == "Intro"
        assert nodes[0].href == "/en/"

    def test_bold_group_header(self) -> None:
        content = "- **Features**\n  - [Email](email.md)\n"
        nodes = parse_sidebar(content, "en")
        assert len(nodes) == 1
        assert nodes[0].is_group is True
        assert nodes[0].label == "Features"
        assert len(nodes[0].children) == 1
        assert nodes[0].children[0].label == "Email"

    def test_nested_structure(self) -> None:
        content = (
            "- **API**\n"
            "  - [Auth](auth.md)\n"
            "  - Endpoints\n"
            "    - [Users](users.md)\n"
        )
        nodes = parse_sidebar(content, "en")
        assert len(nodes) == 1
        api_group = nodes[0]
        assert api_group.label == "API"
        assert len(api_group.children) == 2
        endpoints = api_group.children[1]
        assert endpoints.label == "Endpoints"
        assert endpoints.is_group is True
        assert len(endpoints.children) == 1

    def test_badge(self) -> None:
        content = "- [Feature](feature.md) [badge:New]\n"
        nodes = parse_sidebar(content, "en")
        assert nodes[0].badge == "New"

    def test_method_tag(self) -> None:
        content = "- [List Users](users.md) [method:GET]\n"
        nodes = parse_sidebar(content, "en")
        assert nodes[0].method == "GET"

    def test_badge_and_method(self) -> None:
        content = "- [Create](create.md) [method:POST] [badge:New]\n"
        nodes = parse_sidebar(content, "en")
        assert nodes[0].method == "POST"
        assert nodes[0].badge == "New"

    def test_external_link(self) -> None:
        content = "- [GitHub](https://github.com/example)\n"
        nodes = parse_sidebar(content, "en")
        assert nodes[0].is_external is True

    def test_product_prefix(self) -> None:
        content = "- [Overview](index.md)\n"
        nodes = parse_sidebar(content, "en", product="api")
        assert nodes[0].href == "/en/api/"

    def test_empty_content(self) -> None:
        nodes = parse_sidebar("", "en")
        assert nodes == []


class TestLoadNav:
    """Tests for loading _nav.md from disk."""

    def test_load_sample_nav(self, sample_docs_path: Path) -> None:
        locale_dir = sample_docs_path / "en"
        nodes = load_nav(locale_dir, "en")
        assert len(nodes) == 3
        assert nodes[0].label == "Guide"
        assert nodes[1].badge == "Beta"
        assert nodes[2].is_external is True

    def test_load_nonexistent(self, tmp_path: Path) -> None:
        nodes = load_nav(tmp_path, "en")
        assert nodes == []


class TestLoadSidebar:
    """Tests for loading _sidebar.md with fallback."""

    def test_load_locale_sidebar(self, sample_docs_path: Path) -> None:
        locale_dir = sample_docs_path / "en"
        nodes = load_sidebar(locale_dir, "en")
        assert len(nodes) > 0

    def test_load_product_sidebar(self, sample_docs_path: Path) -> None:
        locale_dir = sample_docs_path / "en"
        nodes = load_sidebar(locale_dir, "en", product="api")
        assert len(nodes) > 0
        # Should have method tags from api/_sidebar.md
        has_method = any(
            n.method is not None
            for n in nodes
            for child in ([n] + list(n.children))
            if hasattr(child, 'method')
        )

    def test_fallback_to_locale_sidebar(self, sample_docs_path: Path) -> None:
        locale_dir = sample_docs_path / "en"
        # "guide" directory has no _sidebar.md
        nodes = load_sidebar(locale_dir, "en", product="guide")
        # Should fallback to en/_sidebar.md
        assert len(nodes) > 0

    def test_empty_fallback(self, tmp_path: Path) -> None:
        nodes = load_sidebar(tmp_path, "en")
        assert nodes == []


class TestParsePage:
    """Tests for content page parsing."""

    def test_parse_with_frontmatter(self, sample_docs_path: Path) -> None:
        file_path = sample_docs_path / "en" / "index.md"
        page = parse_page(file_path, "en", "")
        assert page.title == "Welcome to LiteDocs"
        assert "lightweight documentation tool" in page.description
        assert page.locale == "en"
        assert page.slug == ""

    def test_html_content_generated(self, sample_docs_path: Path) -> None:
        file_path = sample_docs_path / "en" / "index.md"
        page = parse_page(file_path, "en", "")
        assert "<h1" in page.html_content
        assert "LiteDocs" in page.html_content

    def test_toc_extraction(self, sample_docs_path: Path) -> None:
        file_path = sample_docs_path / "en" / "index.md"
        page = parse_page(file_path, "en", "")
        assert len(page.toc) > 0
        toc_texts = [h.text for h in page.toc]
        assert "Features" in toc_texts
        assert "Quick Start" in toc_texts

    def test_heading_ids(self, sample_docs_path: Path) -> None:
        file_path = sample_docs_path / "en" / "index.md"
        page = parse_page(file_path, "en", "")
        assert 'id="features"' in page.html_content
        assert 'id="quick-start"' in page.html_content

    def test_callout_rendering(self, sample_docs_path: Path) -> None:
        file_path = sample_docs_path / "en" / "index.md"
        page = parse_page(file_path, "en", "")
        assert "ld-callout" in page.html_content
        assert "ld-callout--note" in page.html_content

    def test_code_block_rendering(self, sample_docs_path: Path) -> None:
        file_path = sample_docs_path / "en" / "getting-started.md"
        page = parse_page(file_path, "en", "getting-started")
        assert "<code" in page.html_content

    def test_frontmatter_dict(self, sample_docs_path: Path) -> None:
        file_path = sample_docs_path / "en" / "guide" / "installation.md"
        page = parse_page(file_path, "en", "guide/installation", product="guide")
        assert page.frontmatter.get("order") == 1
        assert page.product == "guide"

    def test_title_fallback_to_h1(self, tmp_path: Path) -> None:
        md_file = tmp_path / "test.md"
        md_file.write_text("# My Title\n\nSome content.\n", encoding="utf-8")
        page = parse_page(md_file, "en", "test")
        assert page.title == "My Title"

    def test_title_fallback_to_filename(self, tmp_path: Path) -> None:
        md_file = tmp_path / "my-page.md"
        md_file.write_text("Just content, no heading.\n", encoding="utf-8")
        page = parse_page(md_file, "en", "my-page")
        assert page.title == "My Page"

    def test_auto_description(self, tmp_path: Path) -> None:
        md_file = tmp_path / "test.md"
        md_file.write_text("# Title\n\nThis is the first paragraph of content.\n", encoding="utf-8")
        page = parse_page(md_file, "en", "test")
        assert "first paragraph" in page.description
