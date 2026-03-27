"""Tests for SEO utilities: sitemap, robots.txt, llms.txt."""

from pathlib import Path

import pytest

from litedocs.config import load_config
from litedocs.scanner import scan_docs
from litedocs.seo import (
    generate_llms_full_txt,
    generate_llms_txt,
    generate_robots_txt,
    generate_sitemap,
)


@pytest.fixture
def structure(sample_docs_path: Path):
    """Build a SiteStructure from the sample docs fixture."""
    config = load_config(sample_docs_path)
    return scan_docs(sample_docs_path, config.locales.available)


@pytest.fixture
def config(sample_docs_path: Path):
    return load_config(sample_docs_path)


DOC_SLUG = "sample-docs"
SITE_URL = "https://docs.example.com"


class TestSitemap:
    """Tests for sitemap.xml generation."""

    def test_returns_valid_xml(self, structure, config) -> None:
        xml = generate_sitemap(SITE_URL, DOC_SLUG, structure, config.locales.available)
        assert xml.startswith('<?xml version="1.0"')
        assert "<urlset" in xml
        assert "</urlset>" in xml

    def test_contains_page_urls(self, structure, config) -> None:
        xml = generate_sitemap(SITE_URL, DOC_SLUG, structure, config.locales.available)
        assert f"{SITE_URL}/{DOC_SLUG}/en/" in xml

    def test_contains_lastmod(self, structure, config) -> None:
        xml = generate_sitemap(SITE_URL, DOC_SLUG, structure, config.locales.available)
        assert "<lastmod>" in xml

    def test_contains_alternate_links(self, structure, config) -> None:
        xml = generate_sitemap(SITE_URL, DOC_SLUG, structure, config.locales.available)
        # Should have alternate links for zh locale
        assert 'hreflang="zh"' in xml

    def test_index_page_has_high_priority(self, structure, config) -> None:
        xml = generate_sitemap(SITE_URL, DOC_SLUG, structure, config.locales.available)
        assert "<priority>1.0</priority>" in xml

    def test_non_index_page_has_lower_priority(self, structure, config) -> None:
        xml = generate_sitemap(SITE_URL, DOC_SLUG, structure, config.locales.available)
        assert "<priority>0.8</priority>" in xml


class TestRobotsTxt:
    """Tests for robots.txt generation."""

    def test_contains_user_agent(self) -> None:
        content = generate_robots_txt(SITE_URL)
        assert "User-agent: *" in content

    def test_contains_allow(self) -> None:
        content = generate_robots_txt(SITE_URL)
        assert "Allow: /" in content

    def test_contains_sitemap_reference(self) -> None:
        content = generate_robots_txt(SITE_URL)
        assert f"Sitemap: {SITE_URL}/sitemap.xml" in content


class TestLlmsTxt:
    """Tests for llms.txt generation."""

    def test_contains_title(self, structure, config) -> None:
        data = [(DOC_SLUG, structure, config.locales.available)]
        content = generate_llms_txt(
            config.site.title, config.site.description, SITE_URL, data
        )
        assert f"# {config.site.title}" in content

    def test_contains_docs_section(self, structure, config) -> None:
        data = [(DOC_SLUG, structure, config.locales.available)]
        content = generate_llms_txt(
            config.site.title, config.site.description, SITE_URL, data
        )
        assert "## Docs" in content

    def test_contains_page_links(self, structure, config) -> None:
        data = [(DOC_SLUG, structure, config.locales.available)]
        content = generate_llms_txt(
            config.site.title, config.site.description, SITE_URL, data
        )
        assert SITE_URL in content
        assert DOC_SLUG in content


class TestLlmsFullTxt:
    """Tests for llms-full.txt generation."""

    def test_contains_title(self, structure, config) -> None:
        data = [(DOC_SLUG, structure, config.locales.available)]
        content = generate_llms_full_txt(config.site.title, data)
        assert f"# {config.site.title}" in content

    def test_contains_page_content(self, structure, config) -> None:
        data = [(DOC_SLUG, structure, config.locales.available)]
        content = generate_llms_full_txt(config.site.title, data)
        # Should contain some actual content from pages
        assert len(content) > 100
