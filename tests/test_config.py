"""Tests for configuration loading and validation."""

import json
from pathlib import Path

import pytest

from litedocs.config import SiteConfig, load_config


class TestLoadConfig:
    """Tests for the load_config function."""

    def test_load_valid_config(self, sample_docs_path: Path) -> None:
        config = load_config(sample_docs_path)
        assert config.site.title == "LiteDocs Sample"
        assert config.locales.default == "en"
        assert config.locales.available == ["en", "zh"]
        assert config.theme.primary_color == "#3b82f6"
        assert config.theme.dark_mode is True

    def test_load_config_seo_fields(self, sample_docs_path: Path) -> None:
        config = load_config(sample_docs_path)
        assert config.seo.auto_sitemap is True
        assert config.seo.auto_robots_txt is True
        assert config.seo.auto_llms_txt is True
        assert config.seo.structured_data is True

    def test_load_config_footer(self, sample_docs_path: Path) -> None:
        config = load_config(sample_docs_path)
        assert config.footer.copyright == "© 2026 LiteDocs"
        assert len(config.footer.links) == 1
        assert config.footer.links[0].label == "GitHub"

    def test_missing_config_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="config.json not found"):
            load_config(tmp_path)

    def test_invalid_json(self, tmp_path: Path) -> None:
        (tmp_path / "config.json").write_text("{invalid json", encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_config(tmp_path)

    def test_missing_site_title(self, tmp_path: Path) -> None:
        config_data = {"site": {}, "locales": {"default": "en", "available": ["en"]}}
        (tmp_path / "config.json").write_text(json.dumps(config_data), encoding="utf-8")
        with pytest.raises(Exception):
            load_config(tmp_path)

    def test_minimal_config(self, tmp_path: Path) -> None:
        config_data = {
            "site": {"title": "Minimal"},
            "locales": {"default": "en", "available": ["en"]},
        }
        (tmp_path / "config.json").write_text(json.dumps(config_data), encoding="utf-8")
        config = load_config(tmp_path)
        assert config.site.title == "Minimal"
        assert config.site.description == ""
        assert config.theme.primary_color == "#3b82f6"
        assert config.seo.auto_sitemap is True
        assert config.footer.copyright == ""

    def test_default_locale_not_in_available(self, tmp_path: Path) -> None:
        config_data = {
            "site": {"title": "Test"},
            "locales": {"default": "fr", "available": ["en"]},
        }
        (tmp_path / "config.json").write_text(json.dumps(config_data), encoding="utf-8")
        with pytest.raises(Exception, match="Default locale"):
            load_config(tmp_path)


class TestSiteConfig:
    """Tests for SiteConfig model validation."""

    def test_defaults(self) -> None:
        config = SiteConfig(site={"title": "Test"})
        assert config.locales.default == "en"
        assert config.locales.available == ["en"]
        assert config.theme.dark_mode is True
        assert config.seo.geo.enabled is False

    def test_full_config(self) -> None:
        config = SiteConfig(
            site={"title": "Full", "description": "A full site", "url": "https://example.com"},
            locales={"default": "en", "available": ["en", "zh"]},
            theme={"primary_color": "#ff0000", "dark_mode": False},
            seo={"auto_sitemap": False, "geo": {"enabled": True, "default_region": "US"}},
            analytics={"google_analytics": "G-TEST123"},
            footer={"copyright": "Test", "links": [{"label": "Home", "href": "/"}]},
        )
        assert config.site.url == "https://example.com"
        assert config.theme.primary_color == "#ff0000"
        assert config.theme.dark_mode is False
        assert config.seo.auto_sitemap is False
        assert config.seo.geo.enabled is True
        assert config.seo.geo.default_region == "US"
        assert config.analytics.google_analytics == "G-TEST123"
        assert config.footer.links[0].label == "Home"
