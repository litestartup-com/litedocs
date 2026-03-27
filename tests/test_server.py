"""Tests for FastAPI server routes."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from litedocs.server import create_app

DOC_SLUG = "sample-docs"


@pytest.fixture
def client(sample_docs_path: Path) -> TestClient:
    """Create a test client with sample docs."""
    app = create_app([sample_docs_path])
    return TestClient(app)


class TestRootRoute:
    """Tests for the root redirect."""

    def test_root_redirects_to_default_locale(self, client: TestClient) -> None:
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == f"/{DOC_SLUG}/en/"


class TestPageRoute:
    """Tests for serving documentation pages."""

    def test_serve_locale_index(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert resp.status_code == 200
        assert "Welcome to LiteDocs" in resp.text

    def test_serve_simple_page(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/getting-started")
        assert resp.status_code == 200
        assert "Getting Started" in resp.text

    def test_serve_product_index(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/api/")
        assert resp.status_code == 200
        assert "API Reference" in resp.text

    def test_serve_product_page(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/api/users")
        assert resp.status_code == 200
        assert "List Users" in resp.text

    def test_serve_nested_page(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/guide/installation")
        assert resp.status_code == 200
        assert "Installation" in resp.text

    def test_serve_zh_locale(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/zh/")
        assert resp.status_code == 200

    def test_html_structure(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert resp.status_code == 200
        assert "<!DOCTYPE html>" in resp.text
        assert "<header" in resp.text
        assert 'id="sidebar"' in resp.text
        assert 'id="content"' in resp.text

    def test_nav_items_present(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert "Guide" in resp.text
        assert "API Reference" in resp.text

    def test_sidebar_items_present(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert "Introduction" in resp.text
        assert "Getting Started" in resp.text

    def test_toc_present(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert "On this page" in resp.text
        assert "Features" in resp.text

    def test_meta_tags(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert '<meta name="description"' in resp.text
        assert '<meta property="og:title"' in resp.text

    def test_dark_mode_toggle(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert "toggleDarkMode" in resp.text

    def test_search_modal(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert 'id="search-modal"' in resp.text

    def test_doc_slug_in_urls(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/")
        assert f"/{DOC_SLUG}/en/" in resp.text


class TestErrorHandling:
    """Tests for error responses."""

    def test_404_nonexistent_page(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/nonexistent-page")
        assert resp.status_code == 404

    def test_404_invalid_locale(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/fr/")
        assert resp.status_code == 404

    def test_404_page_content(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/nonexistent")
        assert resp.status_code == 404
        assert "404" in resp.text
        assert "Page Not Found" in resp.text

    def test_404_unknown_doc(self, client: TestClient) -> None:
        resp = client.get("/unknown-doc/en/")
        assert resp.status_code == 404


class TestHTMXPartial:
    """Tests for HTMX partial content loading."""

    def test_htmx_request_returns_partial(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/getting-started", headers={"HX-Request": "true"})
        assert resp.status_code == 200
        # Partial should NOT contain full HTML shell
        assert "<!DOCTYPE html>" not in resp.text
        # But should contain page content
        assert "Getting Started" in resp.text

    def test_normal_request_returns_full_page(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/en/getting-started")
        assert resp.status_code == 200
        assert "<!DOCTYPE html>" in resp.text


class TestStaticFiles:
    """Tests for static file serving."""

    def test_theme_css(self, client: TestClient) -> None:
        resp = client.get("/_themes/default/css/style.css")
        assert resp.status_code == 200
        assert "ld-content" in resp.text

    def test_theme_js(self, client: TestClient) -> None:
        resp = client.get("/_themes/default/js/app.js")
        assert resp.status_code == 200
        assert "toggleDarkMode" in resp.text


class TestSEORoutes:
    """Tests for SEO-related routes."""

    def test_sitemap_xml(self, client: TestClient) -> None:
        resp = client.get("/sitemap.xml")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/xml"
        assert '<?xml version="1.0"' in resp.text
        assert "<urlset" in resp.text
        assert f"/{DOC_SLUG}/en/" in resp.text

    def test_robots_txt(self, client: TestClient) -> None:
        resp = client.get("/robots.txt")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]
        assert "User-agent: *" in resp.text
        assert "Sitemap:" in resp.text

    def test_llms_txt(self, client: TestClient) -> None:
        resp = client.get("/llms.txt")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]
        assert "# LiteDocs Sample" in resp.text
        assert "## Docs" in resp.text

    def test_llms_full_txt(self, client: TestClient) -> None:
        resp = client.get("/llms-full.txt")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]
        assert "# LiteDocs Sample" in resp.text
        assert len(resp.text) > 100

    def test_search_index_json(self, client: TestClient) -> None:
        resp = client.get(f"/{DOC_SLUG}/api/search-index.json")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/json"
        import json
        data = json.loads(resp.text)
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["id"].startswith(f"/{DOC_SLUG}/")

    def test_search_index_unknown_doc(self, client: TestClient) -> None:
        resp = client.get("/unknown-doc/api/search-index.json")
        assert resp.status_code == 404


class TestBasePath:
    """Tests for base_path (reverse proxy URL prefix) support."""

    @pytest.fixture
    def bp_client(self, sample_docs_path: Path) -> TestClient:
        app = create_app([sample_docs_path], base_path="/docs")
        return TestClient(app)

    def test_root_redirect_includes_base_path(self, bp_client: TestClient) -> None:
        resp = bp_client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"].startswith("/docs/")

    def test_page_links_include_base_path(self, bp_client: TestClient) -> None:
        resp = bp_client.get(f"/{DOC_SLUG}/en/")
        assert resp.status_code == 200
        # Sidebar links should include /docs/ prefix
        assert f"/docs/{DOC_SLUG}/en/" in resp.text

    def test_static_assets_include_base_path(self, bp_client: TestClient) -> None:
        resp = bp_client.get(f"/{DOC_SLUG}/en/")
        assert resp.status_code == 200
        assert "/docs/_themes/default/css/style.css" in resp.text
        assert "/docs/_themes/default/js/app.js" in resp.text

    def test_base_path_js_global(self, bp_client: TestClient) -> None:
        resp = bp_client.get(f"/{DOC_SLUG}/en/")
        assert resp.status_code == 200
        assert "window.__LD_BASE_PATH__ = '/docs'" in resp.text

    def test_base_path_from_config(self, sample_docs_path: Path) -> None:
        """When no CLI base_path, falls back to config.site.base_path."""
        import json
        config_file = sample_docs_path / "config.json"
        config_data = json.loads(config_file.read_text(encoding="utf-8"))
        config_data["site"]["base_path"] = "/api-docs"
        config_file.write_text(json.dumps(config_data), encoding="utf-8")
        try:
            app = create_app([sample_docs_path])
            c = TestClient(app)
            resp = c.get("/", follow_redirects=False)
            assert "/api-docs/" in resp.headers["location"]
        finally:
            # Restore original config
            config_data["site"]["base_path"] = ""
            config_file.write_text(json.dumps(config_data, indent=2), encoding="utf-8")

    def test_cli_base_path_overrides_config(self, sample_docs_path: Path) -> None:
        import json
        config_file = sample_docs_path / "config.json"
        config_data = json.loads(config_file.read_text(encoding="utf-8"))
        config_data["site"]["base_path"] = "/api-docs"
        config_file.write_text(json.dumps(config_data), encoding="utf-8")
        try:
            app = create_app([sample_docs_path], base_path="/my-prefix")
            c = TestClient(app)
            resp = c.get("/", follow_redirects=False)
            assert "/my-prefix/" in resp.headers["location"]
        finally:
            config_data["site"]["base_path"] = ""
            config_file.write_text(json.dumps(config_data, indent=2), encoding="utf-8")


class TestFlatMode:
    """Tests for flat mode (non-standard directory without locale subdirs)."""

    @pytest.fixture
    def flat_docs(self, tmp_path: Path) -> Path:
        docs = tmp_path / "my-flat-docs"
        docs.mkdir()
        (docs / "index.md").write_text("---\ntitle: Welcome\n---\n# Welcome\n\nFlat mode.", encoding="utf-8")
        (docs / "setup.md").write_text("---\ntitle: Setup\n---\n# Setup\n\nSetup page.", encoding="utf-8")
        sub = docs / "guide"
        sub.mkdir()
        (sub / "install.md").write_text("---\ntitle: Install\n---\n# Install\n\nSteps.", encoding="utf-8")
        # Auto-scaffold config and sidebar
        from litedocs.scaffold import ensure_config, ensure_sidebar
        from litedocs.config import load_config
        ensure_config(docs)
        cfg = load_config(docs)
        ensure_sidebar(docs, cfg.locales.available, flat_mode=cfg.flat_mode)
        return docs

    @pytest.fixture
    def flat_client(self, flat_docs: Path) -> TestClient:
        app = create_app([flat_docs])
        return TestClient(app)

    def test_root_redirect(self, flat_client: TestClient, flat_docs: Path) -> None:
        resp = flat_client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert f"/{flat_docs.name}/_flat/" in resp.headers["location"]

    def test_serve_index(self, flat_client: TestClient, flat_docs: Path) -> None:
        resp = flat_client.get(f"/{flat_docs.name}/_flat/")
        assert resp.status_code == 200
        assert "Welcome" in resp.text

    def test_serve_page(self, flat_client: TestClient, flat_docs: Path) -> None:
        resp = flat_client.get(f"/{flat_docs.name}/_flat/setup")
        assert resp.status_code == 200
        assert "Setup" in resp.text

    def test_serve_nested_page(self, flat_client: TestClient, flat_docs: Path) -> None:
        resp = flat_client.get(f"/{flat_docs.name}/_flat/guide/install")
        assert resp.status_code == 200
        assert "Install" in resp.text

    def test_sidebar_present(self, flat_client: TestClient, flat_docs: Path) -> None:
        resp = flat_client.get(f"/{flat_docs.name}/_flat/")
        assert resp.status_code == 200
        assert "setup.md" in (flat_docs / "_sidebar.md").read_text(encoding="utf-8")

    def test_no_language_switcher(self, flat_client: TestClient, flat_docs: Path) -> None:
        resp = flat_client.get(f"/{flat_docs.name}/_flat/")
        assert resp.status_code == 200
        assert "lang-switcher" not in resp.text

    def test_config_has_flat_mode(self, flat_docs: Path) -> None:
        import json
        data = json.loads((flat_docs / "config.json").read_text(encoding="utf-8"))
        assert data["flat_mode"] is True
        assert data["locales"]["available"] == ["_flat"]


class TestMultiDoc:
    """Tests for multi-doc support."""

    def test_single_doc_root_redirect(self, client: TestClient) -> None:
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert DOC_SLUG in resp.headers["location"]

    def test_multi_doc_listing(self, sample_docs_path: Path) -> None:
        app = create_app([sample_docs_path, sample_docs_path])
        # Note: same path twice creates slug collision, but tests the listing route
        c = TestClient(app)
        resp = c.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "/_docs"
