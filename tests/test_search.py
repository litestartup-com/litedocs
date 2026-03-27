"""Tests for search index builder."""

from pathlib import Path

import pytest

from litedocs.config import load_config
from litedocs.scanner import scan_docs
from litedocs.search import build_search_index, build_search_index_json

DOC_SLUG = "sample-docs"


@pytest.fixture
def structure(sample_docs_path: Path):
    """Build a SiteStructure from the sample docs fixture."""
    config = load_config(sample_docs_path)
    return scan_docs(sample_docs_path, config.locales.available)


@pytest.fixture
def config(sample_docs_path: Path):
    return load_config(sample_docs_path)


class TestSearchIndex:
    """Tests for search index generation."""

    def test_returns_list(self, structure, config) -> None:
        entries = build_search_index(DOC_SLUG, structure, config.locales.available)
        assert isinstance(entries, list)
        assert len(entries) > 0

    def test_entry_has_required_fields(self, structure, config) -> None:
        entries = build_search_index(DOC_SLUG, structure, config.locales.available)
        entry = entries[0]
        assert "id" in entry
        assert "title" in entry
        assert "description" in entry
        assert "headings" in entry
        assert "body" in entry
        assert "locale" in entry
        assert "product" in entry

    def test_entry_id_is_url_path(self, structure, config) -> None:
        entries = build_search_index(DOC_SLUG, structure, config.locales.available)
        for entry in entries:
            assert entry["id"].startswith(f"/{DOC_SLUG}/")

    def test_entries_have_locale(self, structure, config) -> None:
        entries = build_search_index(DOC_SLUG, structure, config.locales.available)
        locales_found = set(e["locale"] for e in entries)
        assert "en" in locales_found

    def test_body_not_empty(self, structure, config) -> None:
        entries = build_search_index(DOC_SLUG, structure, config.locales.available)
        # At least some entries should have body text
        has_body = [e for e in entries if e["body"]]
        assert len(has_body) > 0

    def test_body_max_500_chars(self, structure, config) -> None:
        entries = build_search_index(DOC_SLUG, structure, config.locales.available)
        for entry in entries:
            assert len(entry["body"]) <= 500

    def test_title_not_empty(self, structure, config) -> None:
        entries = build_search_index(DOC_SLUG, structure, config.locales.available)
        for entry in entries:
            assert entry["title"]


class TestSearchIndexJSON:
    """Tests for JSON serialization."""

    def test_returns_valid_json(self, structure, config) -> None:
        import json
        json_str = build_search_index_json(DOC_SLUG, structure, config.locales.available)
        data = json.loads(json_str)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_json_contains_entries(self, structure, config) -> None:
        import json
        json_str = build_search_index_json(DOC_SLUG, structure, config.locales.available)
        data = json.loads(json_str)
        assert data[0]["id"].startswith(f"/{DOC_SLUG}/")
