"""Tests for directory scanning and content discovery."""

from pathlib import Path

import pytest

from litedocs.scanner import (
    PageInfo,
    SiteStructure,
    _is_content_file,
    _make_slug,
    resolve_page,
    scan_docs,
)


class TestMakeSlug:
    """Tests for slug generation from file paths."""

    def test_index_md(self, tmp_path: Path) -> None:
        f = tmp_path / "index.md"
        f.touch()
        assert _make_slug(f, tmp_path) == ""

    def test_readme_md(self, tmp_path: Path) -> None:
        f = tmp_path / "README.md"
        f.touch()
        assert _make_slug(f, tmp_path) == ""

    def test_simple_file(self, tmp_path: Path) -> None:
        f = tmp_path / "getting-started.md"
        f.touch()
        assert _make_slug(f, tmp_path) == "getting-started"

    def test_nested_index(self, tmp_path: Path) -> None:
        d = tmp_path / "guide"
        d.mkdir()
        f = d / "index.md"
        f.touch()
        assert _make_slug(f, tmp_path) == "guide"

    def test_nested_file(self, tmp_path: Path) -> None:
        d = tmp_path / "guide"
        d.mkdir()
        f = d / "installation.md"
        f.touch()
        assert _make_slug(f, tmp_path) == "guide/installation"

    def test_deep_nested(self, tmp_path: Path) -> None:
        d = tmp_path / "api" / "v2"
        d.mkdir(parents=True)
        f = d / "users.md"
        f.touch()
        assert _make_slug(f, tmp_path) == "api/v2/users"


class TestIsContentFile:
    """Tests for content file detection."""

    def test_normal_md(self, tmp_path: Path) -> None:
        f = tmp_path / "page.md"
        f.touch()
        assert _is_content_file(f) is True

    def test_nav_file(self, tmp_path: Path) -> None:
        f = tmp_path / "_nav.md"
        f.touch()
        assert _is_content_file(f) is False

    def test_sidebar_file(self, tmp_path: Path) -> None:
        f = tmp_path / "_sidebar.md"
        f.touch()
        assert _is_content_file(f) is False

    def test_underscore_prefix(self, tmp_path: Path) -> None:
        f = tmp_path / "_hidden.md"
        f.touch()
        assert _is_content_file(f) is False

    def test_non_md_file(self, tmp_path: Path) -> None:
        f = tmp_path / "image.png"
        f.touch()
        assert _is_content_file(f) is False

    def test_directory(self, tmp_path: Path) -> None:
        d = tmp_path / "subdir"
        d.mkdir()
        assert _is_content_file(d) is False


class TestScanDocs:
    """Tests for the full directory scanning."""

    def test_scan_sample_docs(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en", "zh"])
        assert "en" in structure.locales
        assert "zh" in structure.locales

    def test_locale_info(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en", "zh"])
        en = structure.locales["en"]
        assert en.has_nav is True
        assert en.has_sidebar is True
        assert en.code == "en"

    def test_discovers_products(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        en = structure.locales["en"]
        assert "api" in en.products
        assert "guide" in en.products

    def test_product_has_sidebar(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        en = structure.locales["en"]
        assert en.products["api"].has_sidebar is True

    def test_locale_level_pages(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        en = structure.locales["en"]
        slugs = [p.slug for p in en.pages]
        assert "getting-started" in slugs
        assert "" in slugs  # index.md

    def test_product_pages(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        en = structure.locales["en"]
        api_pages = en.products["api"].pages
        api_slugs = [p.slug for p in api_pages]
        assert "api" in api_slugs  # api/index.md -> "api"
        assert "api/users" in api_slugs

    def test_ignores_unknown_locale(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["fr"])
        assert "fr" not in structure.locales

    def test_empty_directory(self, tmp_path: Path) -> None:
        (tmp_path / "en").mkdir()
        structure = scan_docs(tmp_path, ["en"])
        en = structure.locales["en"]
        assert len(en.pages) == 0
        assert len(en.products) == 0


class TestResolvePage:
    """Tests for page resolution from URL paths."""

    def test_resolve_index(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        page = resolve_page(structure, "en", "")
        assert page is not None
        assert page.slug == ""
        assert page.file_path.name == "index.md"

    def test_resolve_simple_page(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        page = resolve_page(structure, "en", "getting-started")
        assert page is not None
        assert page.slug == "getting-started"

    def test_resolve_product_index(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        page = resolve_page(structure, "en", "api")
        assert page is not None
        assert page.slug == "api"

    def test_resolve_product_page(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        page = resolve_page(structure, "en", "api/users")
        assert page is not None
        assert page.slug == "api/users"
        assert page.product == "api"

    def test_resolve_nonexistent(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        page = resolve_page(structure, "en", "nonexistent")
        assert page is None

    def test_resolve_invalid_locale(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        page = resolve_page(structure, "fr", "index")
        assert page is None

    def test_resolve_with_trailing_slash(self, sample_docs_path: Path) -> None:
        structure = scan_docs(sample_docs_path, ["en"])
        page = resolve_page(structure, "en", "getting-started/")
        assert page is not None
        assert page.slug == "getting-started"
