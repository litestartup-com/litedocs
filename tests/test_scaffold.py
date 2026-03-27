"""Tests for auto-scaffolding: config.json, _sidebar.md, flat locale."""

import json
import shutil
from pathlib import Path

import pytest

from litedocs.scaffold import (
    _detect_locales,
    _scan_for_sidebar,
    ensure_config,
    ensure_index,
    ensure_sidebar,
)


@pytest.fixture
def tmp_docs(tmp_path: Path) -> Path:
    """Create a minimal docs directory with locale subdirectories."""
    docs = tmp_path / "my-docs"
    docs.mkdir()
    en = docs / "en"
    en.mkdir()
    (en / "index.md").write_text("# Welcome\n\nHello world.", encoding="utf-8")
    (en / "getting-started.md").write_text("# Getting Started\n\nSetup guide.", encoding="utf-8")
    guide = en / "guide"
    guide.mkdir()
    (guide / "install.md").write_text("# Installation\n\nInstall steps.", encoding="utf-8")
    return docs


@pytest.fixture
def tmp_flat_docs(tmp_path: Path) -> Path:
    """Create a docs directory without locale subdirectories (flat mode)."""
    docs = tmp_path / "flat-docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Welcome\n\nFlat mode docs.", encoding="utf-8")
    (docs / "setup.md").write_text("# Setup\n\nSetup page.", encoding="utf-8")
    sub = docs / "advanced"
    sub.mkdir()
    (sub / "config.md").write_text("# Config\n\nAdvanced config.", encoding="utf-8")
    return docs


class TestEnsureConfig:
    """Tests for auto-generating config.json."""

    def test_creates_config_when_missing(self, tmp_docs: Path) -> None:
        assert not (tmp_docs / "config.json").exists()
        ensure_config(tmp_docs)
        assert (tmp_docs / "config.json").exists()

    def test_does_not_overwrite_existing(self, tmp_docs: Path) -> None:
        config_file = tmp_docs / "config.json"
        config_file.write_text('{"site": {"title": "Custom"}}', encoding="utf-8")
        ensure_config(tmp_docs)
        data = json.loads(config_file.read_text(encoding="utf-8"))
        assert data["site"]["title"] == "Custom"

    def test_generated_title_from_dirname(self, tmp_docs: Path) -> None:
        ensure_config(tmp_docs)
        data = json.loads((tmp_docs / "config.json").read_text(encoding="utf-8"))
        assert data["site"]["title"] == "My Docs"

    def test_detects_locale_directories(self, tmp_docs: Path) -> None:
        ensure_config(tmp_docs)
        data = json.loads((tmp_docs / "config.json").read_text(encoding="utf-8"))
        assert "en" in data["locales"]["available"]

    def test_flat_mode_when_no_locale_dirs(self, tmp_flat_docs: Path) -> None:
        ensure_config(tmp_flat_docs)
        data = json.loads((tmp_flat_docs / "config.json").read_text(encoding="utf-8"))
        assert data["locales"]["available"] == ["_flat"]
        assert data["locales"]["default"] == "_flat"
        assert data["flat_mode"] is True

    def test_standard_mode_no_flat_mode_key(self, tmp_docs: Path) -> None:
        ensure_config(tmp_docs)
        data = json.loads((tmp_docs / "config.json").read_text(encoding="utf-8"))
        assert "flat_mode" not in data

    def test_returns_true_when_generated(self, tmp_flat_docs: Path) -> None:
        assert ensure_config(tmp_flat_docs) is True

    def test_returns_false_when_exists(self, tmp_docs: Path) -> None:
        (tmp_docs / "config.json").write_text('{"site": {"title": "X"}}', encoding="utf-8")
        assert ensure_config(tmp_docs) is False


class TestDetectLocales:
    """Tests for locale directory detection."""

    def test_detects_en(self, tmp_docs: Path) -> None:
        locales = _detect_locales(tmp_docs)
        assert "en" in locales

    def test_returns_flat_when_no_locales(self, tmp_flat_docs: Path) -> None:
        locales = _detect_locales(tmp_flat_docs)
        assert locales == ["_flat"]

    def test_ignores_dot_dirs(self, tmp_docs: Path) -> None:
        (tmp_docs / ".hidden").mkdir()
        (tmp_docs / ".hidden" / "test.md").write_text("test", encoding="utf-8")
        locales = _detect_locales(tmp_docs)
        assert ".hidden" not in locales

    def test_ignores_assets_dir(self, tmp_docs: Path) -> None:
        assets = tmp_docs / "assets"
        assets.mkdir()
        (assets / "style.md").write_text("not a doc", encoding="utf-8")
        locales = _detect_locales(tmp_docs)
        assert "assets" not in locales


class TestEnsureSidebar:
    """Tests for auto-generating _sidebar.md."""

    def test_creates_sidebar_when_missing(self, tmp_docs: Path) -> None:
        en_dir = tmp_docs / "en"
        assert not (en_dir / "_sidebar.md").exists()
        ensure_sidebar(tmp_docs, ["en"])
        assert (en_dir / "_sidebar.md").exists()

    def test_does_not_overwrite_existing(self, tmp_docs: Path) -> None:
        en_dir = tmp_docs / "en"
        sidebar = en_dir / "_sidebar.md"
        sidebar.write_text("- [Custom](index.md)\n", encoding="utf-8")
        ensure_sidebar(tmp_docs, ["en"])
        assert "Custom" in sidebar.read_text(encoding="utf-8")

    def test_generated_sidebar_has_links(self, tmp_docs: Path) -> None:
        ensure_sidebar(tmp_docs, ["en"])
        content = (tmp_docs / "en" / "_sidebar.md").read_text(encoding="utf-8")
        assert "index.md" in content
        assert "getting-started.md" in content

    def test_generated_sidebar_has_groups(self, tmp_docs: Path) -> None:
        ensure_sidebar(tmp_docs, ["en"])
        content = (tmp_docs / "en" / "_sidebar.md").read_text(encoding="utf-8")
        assert "**Guide**" in content
        assert "install.md" in content


class TestEnsureSidebarFlat:
    """Tests for flat-mode sidebar generation at docs root."""

    def test_creates_sidebar_at_root(self, tmp_flat_docs: Path) -> None:
        assert not (tmp_flat_docs / "_sidebar.md").exists()
        ensure_sidebar(tmp_flat_docs, ["_flat"], flat_mode=True)
        assert (tmp_flat_docs / "_sidebar.md").exists()

    def test_sidebar_has_root_files(self, tmp_flat_docs: Path) -> None:
        ensure_sidebar(tmp_flat_docs, ["_flat"], flat_mode=True)
        content = (tmp_flat_docs / "_sidebar.md").read_text(encoding="utf-8")
        assert "index.md" in content
        assert "setup.md" in content

    def test_sidebar_has_subdir_group(self, tmp_flat_docs: Path) -> None:
        ensure_sidebar(tmp_flat_docs, ["_flat"], flat_mode=True)
        content = (tmp_flat_docs / "_sidebar.md").read_text(encoding="utf-8")
        assert "**Advanced**" in content
        assert "config.md" in content

    def test_does_not_overwrite_existing(self, tmp_flat_docs: Path) -> None:
        sidebar = tmp_flat_docs / "_sidebar.md"
        sidebar.write_text("- [Custom](index.md)\n", encoding="utf-8")
        ensure_sidebar(tmp_flat_docs, ["_flat"], flat_mode=True)
        assert "Custom" in sidebar.read_text(encoding="utf-8")


class TestEnsureIndex:
    """Tests for auto-generating index.md in flat mode."""

    def test_creates_index_when_missing(self, tmp_path: Path) -> None:
        docs = tmp_path / "no-index"
        docs.mkdir()
        (docs / "page.md").write_text("# Page\n\nContent.", encoding="utf-8")
        ensure_index(docs, flat_mode=True)
        assert (docs / "index.md").exists()

    def test_uses_dirname_as_title(self, tmp_path: Path) -> None:
        docs = tmp_path / "my-project"
        docs.mkdir()
        (docs / "page.md").write_text("# Page", encoding="utf-8")
        ensure_index(docs, flat_mode=True)
        content = (docs / "index.md").read_text(encoding="utf-8")
        assert "My Project" in content

    def test_does_not_overwrite_existing_index(self, tmp_flat_docs: Path) -> None:
        # tmp_flat_docs already has index.md
        original = (tmp_flat_docs / "index.md").read_text(encoding="utf-8")
        ensure_index(tmp_flat_docs, flat_mode=True)
        assert (tmp_flat_docs / "index.md").read_text(encoding="utf-8") == original

    def test_respects_readme(self, tmp_path: Path) -> None:
        docs = tmp_path / "has-readme"
        docs.mkdir()
        (docs / "README.md").write_text("# Readme", encoding="utf-8")
        ensure_index(docs, flat_mode=True)
        assert not (docs / "index.md").exists()

    def test_noop_for_standard_mode(self, tmp_path: Path) -> None:
        docs = tmp_path / "standard"
        docs.mkdir()
        ensure_index(docs, flat_mode=False)
        assert not (docs / "index.md").exists()


class TestScanForSidebar:
    """Tests for sidebar entry generation."""

    def test_scans_files(self, tmp_docs: Path) -> None:
        entries = _scan_for_sidebar(tmp_docs / "en")
        assert len(entries) > 0
        assert any("index.md" in e for e in entries)

    def test_groups_subdirs(self, tmp_docs: Path) -> None:
        entries = _scan_for_sidebar(tmp_docs / "en")
        assert any("**Guide**" in e for e in entries)
