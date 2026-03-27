# Changelog

## v0.4.0 - Daemon Process Management

### Added

- **`litedocs start`**: Start the server as a background daemon. Supports specifying directories, host, port, and base path. Multiple instances on different ports are supported.
- **`litedocs stop`**: Stop a running daemon by port (`--port`), or stop all instances (`--all`).
- **`litedocs restart`**: Restart a daemon (stop + start). Re-reads config and re-scans documents.
- **`litedocs status`**: Show all daemon instances with PID, port, status (running/dead), uptime, and URL.
- **`litedocs logs`**: View daemon logs with tail/follow support (`--follow`, `--lines`).
- **New module**: `litedocs/process.py` — cross-platform (macOS/Linux/Windows) PID file management, process spawning via `subprocess.Popen`, and status queries.
- **`litedocs/__main__.py`**: Enables `python -m litedocs.cli` for daemon subprocess invocation.
- **Multi-instance support**: Each instance keyed by port, metadata stored in `.litedocs/instance-{port}.json`, logs in `.litedocs/instance-{port}.log`.
- **New tests**: `test_process.py` (16 tests), `test_cli_commands.py` (19 tests). Total: **206 tests**.

### Changed

- CLI `serve` is now explicitly "foreground mode" in its help text.
- CLI `start` defaults to `--no-reload` (appropriate for daemon mode).
- Shared CLI helpers extracted: `_resolve_docs_dirs()`, `_normalize_base_path()`, `_scaffold()`, `_print_startup_info()`.

---

## v0.3.0 - SEO, Search, Base Path & Auto-Scaffold

### Added

- **SEO Routes**: Auto-generated `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/llms-full.txt`. Controlled by `config.seo.*` flags; requires `site.url` to be set.
- **Client-Side Search**: Full-text search powered by MiniSearch (CDN). Search modal triggered by `Ctrl+K`. Index served at `/{doc_slug}/api/search-index.json`. Locale-aware filtering, keyboard navigation, debounced input.
- **Base Path / Reverse Proxy**: New `--base-path` CLI flag and `site.base_path` config field. All internal URLs (nav, sidebar, static assets, search, SEO) automatically include the prefix. Nginx `proxy_pass` compatible.
- **Auto-Scaffold**: Missing `config.json` and `_sidebar.md` auto-generated on first run. Title derived from directory name. Sidebar built by scanning `.md` files.
- **Flat Mode**: Docs directories without locale subdirectories are treated as non-standard; `config.json` is auto-generated with `flat_mode: true`. The docs root itself is used as the content directory (no `_flat/` subdirectory created). `_sidebar.md` is generated at the docs root. CLI startup prints a warning with a link to the documentation.
- **Optional `_nav.md`**: Top navigation tabs hidden when `_nav.md` is absent — useful for simple single-section docs.
- **`flat_mode` config flag**: New `flat_mode: bool` field in `SiteConfig`. When true, language switcher is hidden and the docs root is scanned directly.
- **Demo Mode**: `litedocs serve` with no arguments serves the built-in demo docs (`litedocs-docs` + `sample-docs`), showcasing all features out of the box.
- **Auto-generate `index.md`**: In flat mode, if no `index.md` or `README.md` exists, a minimal welcome page is created automatically.
- **New module**: `litedocs/scaffold.py` — `ensure_config()`, `ensure_index()`, `ensure_sidebar()`.
- **New tests**: `test_scaffold.py` (27 tests), `TestFlatMode` in `test_server.py` (7 tests), `TestBasePath` (6 tests), `test_seo.py` (11 tests), `test_search.py` (10 tests), SEO route tests (6 tests). Total: **171 tests**.

### Changed

- `create_app()` accepts optional `base_path` parameter.
- `DocsApp.__init__()` accepts optional `base_path` parameter.
- `parse_nav()`, `parse_sidebar()`, `load_nav()`, `load_sidebar()` accept optional `base_path` parameter for URL prefix.
- CLI `serve` command no longer requires `config.json` to exist — auto-generates it.
- CLI `serve` `docs_dirs` argument is now optional; defaults to built-in demo directories.
- All templates use `{{ base_path }}` prefix for internal links and static assets.
- `search.js` reads `window.__LD_BASE_PATH__` for base-path-aware URL construction.
- 404 error template uses `base_path` for asset and link URLs.
- `scanner.py`: flat mode (`_flat` locale) uses `docs_path` itself as the locale directory.
- Locale detection uses strict ISO 639-1 / BCP 47 regex instead of length heuristic.
- Header template hides language switcher when `flat_mode` is true.

---

## v0.2.0 - Theme Architecture & Multi-Doc Support

### Added

- **Theme Architecture**: Templates and static assets moved to `litedocs/themes/default/`. Each theme is a self-contained directory with `theme.json`, `templates/`, and `static/`.
- **Theme Selection**: New `theme.name` field in `config.json` to select the active theme (default: `"default"`).
- **Multi-Doc Support**: CLI now accepts multiple documentation directories (`litedocs serve ./docs-a ./docs-b`).
- **Multi-Doc URL Scheme**: All page URLs now follow `/{doc_slug}/{locale}/{path}` pattern.
- **Doc Switcher UI**: Header displays a doc switcher dropdown when multiple docs are served.
- **Doc Listing Page**: `/_docs` route shows a listing of all documentation sites in multi-doc mode.
- **Windsurf-Style Header**: Two-row header layout — top row with logo, search bar, language/dark mode toggles; bottom row with nav tabs.
- **Wider Layout**: Content max-width increased to 860px, page max-width to `screen-2xl` (1536px).
- **New Tests**: `TestMultiDoc`, `TestStaticFiles` (theme paths), `test_404_unknown_doc`, `test_doc_slug_in_urls`.

### Changed

- `create_app()` now accepts `list[Path]` instead of a single `Path`.
- `run_server()` parameter renamed from `docs_path` to `docs_paths` (list).
- `DocsApp.__init__()` now requires a `slug` parameter.
- `parse_nav()`, `parse_sidebar()`, `load_nav()`, `load_sidebar()` accept optional `doc_slug` parameter for URL prefix generation.
- `create_jinja_env()` accepts a `theme_name` parameter to load templates from the correct theme directory.
- Watcher updated to use `doc_registry` instead of single `docs_app`.
- Static assets served at `/_themes/{theme_name}/` instead of `/_static/`.
- CSS custom properties updated: `--ld-header-h: 6.5rem`, `--ld-content-max-w: 860px`, `--ld-sidebar-w: 256px`.

### Removed

- Old `litedocs/templates/` directory (migrated to `litedocs/themes/default/templates/`).
- Old `litedocs/static/` directory (migrated to `litedocs/themes/default/static/`).

---

## v0.1.0 - Initial MVP

### Added

- FastAPI server with Jinja2 template rendering
- Markdown parsing with markdown-it-py (tables, footnotes, task lists, strikethrough, callouts)
- YAML frontmatter support
- Navigation (`_nav.md`) and sidebar (`_sidebar.md`) parsing
- Multi-language support via folder structure
- Dark mode with localStorage persistence
- HTMX partial page navigation
- TOC scroll spy
- Code block copy buttons
- Hot reload file watcher
- SEO meta tags (Open Graph, description, canonical)
- Responsive mobile layout with sidebar overlay
- 404 error page
- 102 unit and integration tests
