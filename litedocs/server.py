"""FastAPI server and route definitions for LiteDocs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from litedocs.config import SiteConfig, load_config
from litedocs.models import LocaleContext
from litedocs.parser import load_nav, load_sidebar, parse_page
from litedocs.renderer import build_render_context, create_jinja_env, get_theme_dir
from litedocs.scanner import SiteStructure, resolve_page, scan_docs
from litedocs.search import build_search_index_json
from litedocs.seo import (
    generate_llms_full_txt,
    generate_llms_txt,
    generate_robots_txt,
    generate_sitemap,
)


@dataclass
class DocInfo:
    """Metadata for a documentation directory used by the doc switcher UI."""

    slug: str
    title: str
    docs_path: Path


class DocsApp:
    """Core application state for a single documentation directory."""

    def __init__(self, docs_path: Path, slug: str, base_path: str = "") -> None:
        self.docs_path = docs_path
        self.slug = slug
        self.base_path = base_path
        self.config: SiteConfig = load_config(docs_path)
        self.structure: SiteStructure = scan_docs(
            docs_path, self.config.locales.available
        )
        theme_name = self.config.theme.name
        self.jinja_env = create_jinja_env(theme_name)
        self.theme_name = theme_name
        # Caches
        self._nav_cache: dict[str, list] = {}
        self._sidebar_cache: dict[str, list] = {}
        self._page_cache: dict[str, Any] = {}

    def reload(self) -> None:
        """Reload config and rescan docs directory (called by watcher)."""
        self.config = load_config(self.docs_path)
        self.structure = scan_docs(
            self.docs_path, self.config.locales.available
        )
        new_theme = self.config.theme.name
        if new_theme != self.theme_name:
            self.jinja_env = create_jinja_env(new_theme)
            self.theme_name = new_theme
        self._nav_cache.clear()
        self._sidebar_cache.clear()
        self._page_cache.clear()

    def invalidate_caches(self) -> None:
        """Clear all caches without full reload."""
        self._nav_cache.clear()
        self._sidebar_cache.clear()
        self._page_cache.clear()

    def get_nav(self, locale: str) -> list:
        """Get cached nav items for a locale."""
        if locale not in self._nav_cache:
            locale_info = self.structure.locales.get(locale)
            if locale_info:
                self._nav_cache[locale] = load_nav(
                    locale_info.dir_path, locale, doc_slug=self.slug,
                    base_path=self.base_path,
                )
            else:
                self._nav_cache[locale] = []
        return self._nav_cache[locale]

    def get_sidebar(self, locale: str, product: str | None = None) -> list:
        """Get cached sidebar items for a locale/product."""
        cache_key = f"{locale}:{product or ''}"
        if cache_key not in self._sidebar_cache:
            locale_info = self.structure.locales.get(locale)
            if locale_info:
                self._sidebar_cache[cache_key] = load_sidebar(
                    locale_info.dir_path, locale, product, doc_slug=self.slug,
                    base_path=self.base_path,
                )
            else:
                self._sidebar_cache[cache_key] = []
        return self._sidebar_cache[cache_key]


def create_app(docs_paths: list[Path], base_path: str = "") -> FastAPI:
    """Create and configure the FastAPI application with multi-doc support.

    Args:
        docs_paths: List of paths to documentation root directories.
        base_path: URL prefix for reverse proxy (e.g. "/docs"). Empty string
            means no prefix. CLI ``--base-path`` overrides ``config.site.base_path``.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(title="LiteDocs", docs_url=None, redoc_url=None)

    # Resolve effective base_path: CLI arg > first config > empty
    bp = base_path
    if not bp:
        first_config = load_config(docs_paths[0])
        bp = first_config.site.base_path.rstrip("/") if first_config.site.base_path else ""
    bp = bp.rstrip("/")
    if bp and not bp.startswith("/"):
        bp = "/" + bp

    app.state.base_path = bp

    # Build doc registry: slug -> DocsApp
    doc_registry: dict[str, DocsApp] = {}
    doc_list: list[DocInfo] = []

    for docs_path in docs_paths:
        config = load_config(docs_path)
        slug = docs_path.name
        docs_app = DocsApp(docs_path, slug, base_path=bp)
        doc_registry[slug] = docs_app
        doc_list.append(DocInfo(slug=slug, title=config.site.title, docs_path=docs_path))

    app.state.doc_registry = doc_registry
    app.state.doc_list = doc_list

    # Mount theme static files for each unique theme
    mounted_themes: set[str] = set()
    for docs_app in doc_registry.values():
        theme_name = docs_app.theme_name
        if theme_name not in mounted_themes:
            theme_dir = get_theme_dir(theme_name)
            static_dir = theme_dir / "static"
            if static_dir.is_dir():
                app.mount(
                    f"/_themes/{theme_name}",
                    StaticFiles(directory=str(static_dir)),
                    name=f"theme_{theme_name}",
                )
            mounted_themes.add(theme_name)

    # Mount user assets for each doc
    for slug, docs_app in doc_registry.items():
        assets_dir = docs_app.docs_path / "assets"
        if assets_dir.is_dir():
            app.mount(
                f"/{slug}/assets",
                StaticFiles(directory=str(assets_dir)),
                name=f"assets_{slug}",
            )

    # --- SEO Routes ---

    @app.get("/sitemap.xml")
    async def sitemap_xml() -> Response:
        """Serve auto-generated sitemap.xml combining all docs."""
        # Use the first doc's site_url; merge all docs' pages
        first_app = doc_registry[doc_list[0].slug]
        site_url = first_app.config.site.url
        if not site_url or not first_app.config.seo.auto_sitemap:
            return Response(status_code=404)

        # Combine sitemaps from all docs
        from xml.etree.ElementTree import Element, SubElement, tostring
        SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
        XHTML_NS = "http://www.w3.org/1999/xhtml"
        urlset = Element("urlset")
        urlset.set("xmlns", SITEMAP_NS)
        urlset.set("xmlns:xhtml", XHTML_NS)

        for d in doc_list:
            da = doc_registry[d.slug]
            if not da.config.seo.auto_sitemap:
                continue
            partial_xml = generate_sitemap(
                site_url, d.slug, da.structure, da.config.locales.available
            )
            # Parse partial and merge url elements
            from xml.etree.ElementTree import fromstring
            try:
                partial_root = fromstring(partial_xml)
                for url_el in partial_root:
                    urlset.append(url_el)
            except Exception:
                pass

        xml_str = tostring(urlset, encoding="unicode", xml_declaration=False)
        content = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
        return Response(content=content, media_type="application/xml")

    @app.get("/robots.txt")
    async def robots_txt() -> Response:
        """Serve auto-generated robots.txt."""
        first_app = doc_registry[doc_list[0].slug]
        site_url = first_app.config.site.url
        if not site_url or not first_app.config.seo.auto_robots_txt:
            return Response(status_code=404)
        content = generate_robots_txt(site_url)
        return Response(content=content, media_type="text/plain")

    @app.get("/llms.txt")
    async def llms_txt() -> Response:
        """Serve llms.txt — structured index for LLM crawlers."""
        first_app = doc_registry[doc_list[0].slug]
        site_url = first_app.config.site.url
        if not site_url or not first_app.config.seo.auto_llms_txt:
            return Response(status_code=404)
        data = [
            (d.slug, doc_registry[d.slug].structure, doc_registry[d.slug].config.locales.available)
            for d in doc_list
        ]
        content = generate_llms_txt(
            first_app.config.site.title,
            first_app.config.site.description,
            site_url,
            data,
        )
        return Response(content=content, media_type="text/plain; charset=utf-8")

    @app.get("/llms-full.txt")
    async def llms_full_txt() -> Response:
        """Serve llms-full.txt — full plain text content for LLM crawlers."""
        first_app = doc_registry[doc_list[0].slug]
        site_url = first_app.config.site.url
        if not site_url or not first_app.config.seo.auto_llms_txt:
            return Response(status_code=404)
        data = [
            (d.slug, doc_registry[d.slug].structure, doc_registry[d.slug].config.locales.available)
            for d in doc_list
        ]
        content = generate_llms_full_txt(
            first_app.config.site.title,
            data,
        )
        return Response(content=content, media_type="text/plain; charset=utf-8")

    # --- Search Route ---

    @app.get("/{doc_slug}/api/search-index.json")
    async def search_index(doc_slug: str) -> Response:
        """Serve the search index JSON for a specific doc."""
        da = doc_registry.get(doc_slug)
        if da is None:
            return Response(status_code=404)
        index_json = build_search_index_json(
            doc_slug, da.structure, da.config.locales.available
        )
        return Response(content=index_json, media_type="application/json")

    # --- Page Routes ---

    @app.get("/", response_class=RedirectResponse)
    async def root() -> RedirectResponse:
        """Redirect root to the first doc's default locale."""
        if len(doc_list) == 1:
            d = doc_list[0]
            da = doc_registry[d.slug]
            return RedirectResponse(
                url=f"{bp}/{d.slug}/{da.config.locales.default}/", status_code=302
            )
        # Multiple docs: redirect to a simple doc listing
        return RedirectResponse(url=f"{bp}/_docs", status_code=302)

    @app.get("/_docs", response_class=HTMLResponse)
    async def doc_listing() -> HTMLResponse:
        """Render a simple documentation listing page for multi-doc mode."""
        items = []
        for d in doc_list:
            da = doc_registry[d.slug]
            items.append(
                f'<a href="{bp}/{d.slug}/{da.config.locales.default}/" '
                f'class="block p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 '
                f'hover:border-primary-500 hover:shadow-lg transition-all">'
                f'<h2 class="text-lg font-semibold mb-1">{d.title}</h2>'
                f'<p class="text-sm text-zinc-500">{da.config.site.description}</p>'
                f"</a>"
            )
        html = (
            '<!DOCTYPE html><html class="scroll-smooth"><head>'
            '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
            "<title>Documentation</title>"
            '<script src="https://cdn.tailwindcss.com"></script>'
            '<script>tailwind.config={darkMode:"class"}</script>'
            "</head>"
            '<body class="bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 antialiased">'
            '<div class="max-w-2xl mx-auto px-4 py-16">'
            '<h1 class="text-3xl font-bold mb-8">Documentation</h1>'
            f'<div class="grid gap-4">{"".join(items)}</div>'
            "</div></body></html>"
        )
        return HTMLResponse(content=html)

    @app.get("/favicon.ico")
    async def favicon() -> Response:
        """Serve favicon from the first doc."""
        if doc_list:
            da = doc_registry[doc_list[0].slug]
            favicon_path = da.config.site.favicon
            if favicon_path:
                full_path = da.docs_path / favicon_path
                if full_path.is_file():
                    return Response(
                        content=full_path.read_bytes(),
                        media_type="image/x-icon",
                    )
        return Response(status_code=404)

    @app.get("/{doc_slug}/{locale}/{path:path}", response_class=HTMLResponse)
    async def serve_page(
        request: Request, doc_slug: str, locale: str, path: str = ""
    ) -> Response:
        """Serve a documentation page under /{doc}/{locale}/{path}."""
        # Validate doc slug
        docs_app = doc_registry.get(doc_slug)
        if docs_app is None:
            return _render_404_simple(request)

        config = docs_app.config

        # Validate locale
        if locale not in config.locales.available:
            return _render_404_themed(
                docs_app, request, locale=config.locales.default, doc_slug=doc_slug,
                doc_list=doc_list, base_path=bp,
            )

        # Resolve the page
        page_info = resolve_page(docs_app.structure, locale, path)
        if page_info is None:
            return _render_404_themed(
                docs_app, request, locale=locale, doc_slug=doc_slug,
                doc_list=doc_list, base_path=bp,
            )

        # Parse the page content
        cache_key = f"{doc_slug}:{locale}:{page_info.slug}:{page_info.file_path.stat().st_mtime}"
        if cache_key in docs_app._page_cache:
            page_ctx = docs_app._page_cache[cache_key]
        else:
            page_ctx = parse_page(
                page_info.file_path,
                locale,
                page_info.slug,
                page_info.product,
            )
            docs_app._page_cache[cache_key] = page_ctx

        # Build locale context
        nav_items = docs_app.get_nav(locale)
        sidebar_tree = docs_app.get_sidebar(locale, page_info.product)

        locale_ctx = LocaleContext(
            locale=locale,
            nav_items=nav_items,
            sidebar_tree=sidebar_tree,
            current_product=page_info.product,
        )

        # Build template context
        current_path = f"{bp}/{doc_slug}/{locale}/{path}".rstrip("/") if path else f"{bp}/{doc_slug}/{locale}"
        ctx = build_render_context(
            config, locale_ctx, page_ctx, current_path, config.locales.available
        )
        ctx["doc_slug"] = doc_slug
        ctx["doc_list"] = doc_list
        ctx["base_path"] = bp
        ctx["flat_mode"] = config.flat_mode

        # Check for HTMX partial request
        is_htmx = request.headers.get("HX-Request") == "true"
        template_name = "partials/content.html" if is_htmx else "page.html"

        template = docs_app.jinja_env.get_template(template_name)
        html = template.render(**ctx)
        return HTMLResponse(content=html)

    return app


def _render_404_simple(request: Request) -> HTMLResponse:
    """Render a minimal 404 error page (no theme context)."""
    return HTMLResponse(
        content=(
            "<html><body style='font-family:sans-serif;text-align:center;padding:4rem'>"
            "<h1 style='font-size:4rem;color:#ccc'>404</h1>"
            "<p>Page Not Found</p>"
            f"<p><code>{request.url.path}</code></p>"
            '<p><a href="/" style="color:#3b82f6">Go Home</a></p>'
            "</body></html>"
        ),
        status_code=404,
    )


def _render_404_themed(
    docs_app: DocsApp,
    request: Request,
    locale: str,
    doc_slug: str,
    doc_list: list[DocInfo],
    base_path: str = "",
) -> HTMLResponse:
    """Render the themed 404 error page."""
    config = docs_app.config
    try:
        template = docs_app.jinja_env.get_template("errors/404.html")
        html = template.render(
            config=config,
            locale=locale,
            available_locales=config.locales.available,
            current_path=str(request.url.path),
            doc_slug=doc_slug,
            doc_list=doc_list,
            base_path=base_path,
        )
        return HTMLResponse(content=html, status_code=404)
    except Exception:
        return _render_404_simple(request)


def run_server(
    app: FastAPI,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    docs_paths: list[Path] | None = None,
) -> None:
    """Run the FastAPI server with uvicorn.

    Args:
        app: The FastAPI application.
        host: Host to bind to.
        port: Port to bind to.
        reload: Enable hot reload via file watcher.
        docs_paths: List of paths to doc directories (for watcher).
    """
    if reload and docs_paths:
        from litedocs.watcher import start_watcher
        for docs_path in docs_paths:
            start_watcher(app, docs_path)

    uvicorn.run(app, host=host, port=port, log_level="info")
