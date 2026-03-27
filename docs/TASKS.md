# LiteDocs - Development Tasks

> Task breakdown by phase. Each task includes scope, acceptance criteria, and estimated effort.

---

## Phase 1: Foundation and MVP (Single Language)

**Goal**: A working server that renders Markdown from a folder with basic Fumadocs-style UI.

### Task 1.1: Project Scaffolding

**Effort**: 0.5 day

**Scope**:
- Create `pyproject.toml` with all dependencies and metadata
- Create package structure (`litedocs/` with all module files as empty stubs)
- Create `litedocs/cli.py` with `serve` command skeleton (typer)
- Verify `pip install -e .` works and `litedocs serve` command is available

**Acceptance Criteria**:
- Running `litedocs --help` shows usage info
- Running `litedocs serve /path/to/docs` starts without error (even if no rendering yet)

**Dependencies**: `fastapi`, `uvicorn[standard]`, `jinja2`, `markdown-it-py`, `mdit-py-plugins`, `python-frontmatter`, `typer`, `watchfiles`, `pydantic>=2.0`

---

### Task 1.2: Configuration Loading

**Effort**: 0.5 day

**Scope**:
- Implement `config.py` with Pydantic v2 models for `SiteConfig`, `SEOConfig`, `AnalyticsConfig`, `FooterConfig`
- Load and validate `config.json` from docs root
- Provide sensible defaults for all optional fields
- Error messages for missing required fields

**Acceptance Criteria**:
- Valid `config.json` loads into `SiteConfig` model
- Missing optional fields use defaults
- Missing `site.title` or `locales` raises clear error
- Unit tests: `tests/test_config.py`

---

### Task 1.3: Data Models

**Effort**: 0.5 day

**Scope**:
- Implement `models.py` with all data classes: `NavNode`, `SidebarNode`, `PageContext`, `TocHeading`, `LocaleContext`, `NavLink`
- Use Pydantic models or dataclasses

**Acceptance Criteria**:
- All models defined per DESIGN.md section 10
- Models are serializable (for template context passing)
- Unit tests for model creation and validation

---

### Task 1.4: Directory Scanner

**Effort**: 1 day

**Scope**:
- Implement `scanner.py`
- Scan docs root to discover: available locales (folders matching ISO 639-1 codes), products (subdirectories with `_sidebar.md`), all `.md` files
- Build a `SiteMap` structure: `{locale: {product: [pages]}}`
- Handle edge cases: empty directories, missing `_nav.md`, etc.

**Acceptance Criteria**:
- Given a sample docs folder, correctly identifies locales, products, pages
- Ignores non-markdown files and hidden directories
- Unit tests: `tests/test_scanner.py` with `tests/fixtures/sample-docs/`

---

### Task 1.5: Markdown Parser - Navigation and Sidebar

**Effort**: 1.5 days

**Scope**:
- Implement nav/sidebar parsing in `parser.py`
- Parse `_nav.md` into `list[NavNode]`
- Parse `_sidebar.md` into `list[SidebarNode]` (recursive tree)
- Handle: group headers (`**Bold**`), links, external links, badges (`[badge:X]`), method tags (`[method:POST]`), nested indentation

**Acceptance Criteria**:
- `_nav.md` sample from DESIGN.md section 5.1 parses correctly
- `_sidebar.md` sample from DESIGN.md section 5.2 parses correctly
- Nested sidebar items maintain correct parent-child hierarchy
- Badges and method tags extracted into model fields
- Unit tests: `tests/test_parser.py` with multiple fixture files

---

### Task 1.6: Markdown Parser - Content Pages

**Effort**: 1 day

**Scope**:
- Extend `parser.py` for content `.md` files
- Parse YAML frontmatter via `python-frontmatter`
- Render Markdown to HTML via `markdown-it-py` with plugins: tables, footnotes, task lists, strikethrough, heading anchors (auto `id`), callout/admonition (`> [!NOTE]`, `> [!WARNING]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!CAUTION]`)
- Extract TOC (list of `TocHeading`) from rendered headings
- Return `PageContext` with all fields populated

**Acceptance Criteria**:
- Frontmatter parsed into dict, `title`/`description` extracted
- HTML output contains proper heading IDs for TOC linking
- Callouts render as styled div blocks
- TOC contains all h2-h4 headings with correct nesting
- Code blocks have language class for highlight.js
- Unit tests with various `.md` fixtures

---

### Task 1.7: FastAPI Server and Routes

**Effort**: 1.5 days

**Scope**:
- Implement `server.py` with FastAPI app
- Routes:
  - `GET /` - redirect to `/{default_locale}/`
  - `GET /{locale}/{path:path}` - content page
  - `GET /assets/{path:path}` - static files from docs `assets/`
  - Built-in static files (CSS/JS) served from `litedocs/static/`
- Slug resolution logic (see DESIGN.md section 6.2)
- 404 handling with friendly error page
- Integrate with `cli.py` to start uvicorn

**Acceptance Criteria**:
- `/` redirects to `/en/` (or configured default locale)
- `/en/getting-started` finds and renders `en/getting-started.md`
- `/en/product-a/` finds `en/product-a/index.md`
- `/assets/logo.png` serves file from docs `assets/` folder
- 404 page shown for missing pages
- Static CSS/JS files accessible

---

### Task 1.8: Jinja2 Templates - Base Layout

**Effort**: 2 days

**Scope**:
- Create all Jinja2 templates per DESIGN.md section 12
- `base.html`: Full HTML shell with Tailwind CDN, highlight.js CDN, HTMX CDN, meta tags, dark mode class on `<html>`
- `page.html`: Extends base, three-column layout (sidebar + content + TOC)
- `partials/header.html`: Logo, nav tabs, language switcher, dark mode toggle, search button
- `partials/sidebar.html`: Recursive sidebar tree with collapsible groups
- `partials/toc.html`: Right-side table of contents
- `partials/content.html`: Main content area (HTMX target)
- `partials/footer.html`: Copyright and links
- `partials/pagination.html`: Prev/Next page links
- `errors/404.html`: Friendly 404 page

**Acceptance Criteria**:
- Full page renders with all layout sections visible
- Sidebar shows tree structure with proper indentation
- TOC shows heading hierarchy
- Header shows nav tabs from `_nav.md`
- Responsive: sidebar collapses on mobile
- Clean, Fumadocs-inspired visual style

---

### Task 1.9: Renderer Integration

**Effort**: 1 day

**Scope**:
- Implement `renderer.py`
- Assemble full template context: `SiteConfig` + `LocaleContext` + `PageContext`
- Mark active nav/sidebar items based on current path
- Determine prev/next pages from sidebar order
- Render Jinja2 template and return HTML string

**Acceptance Criteria**:
- Active nav item highlighted
- Active sidebar item highlighted and parent groups expanded
- Prev/Next links point to correct adjacent pages in sidebar order
- All template variables populated

---

### Task 1.10: Static Assets - CSS

**Effort**: 1.5 days

**Scope**:
- Create `litedocs/static/css/style.css`
- Tailwind-based styles for: layout grid, sidebar, TOC, content typography, code blocks, callouts/admonitions, badges, method tags, dark mode overrides, responsive breakpoints, scrollbar styling, transition animations
- Fumadocs-inspired color scheme and spacing

**Acceptance Criteria**:
- Pages look clean and modern, visually similar to Fumadocs
- Dark mode fully styled
- Mobile responsive
- Code blocks have language label and proper styling
- Callouts have colored left border and icon

---

### Task 1.11: Static Assets - JavaScript

**Effort**: 1 day

**Scope**:
- `litedocs/static/js/app.js`: Dark mode toggle (localStorage persistence, system preference detection), TOC scroll spy (IntersectionObserver), sidebar toggle (mobile), smooth scroll to anchor
- `litedocs/static/js/copy-code.js`: Add copy button to all code blocks, clipboard API

**Acceptance Criteria**:
- Dark mode toggles and persists across page loads
- TOC highlights current section while scrolling
- Sidebar opens/closes on mobile
- Copy button appears on code blocks and copies content

---

### Task 1.12: Hot Reload (File Watcher)

**Effort**: 0.5 day

**Scope**:
- Implement `watcher.py` using `watchfiles`
- Watch docs root for `.md`, `.json`, and asset file changes
- On change: invalidate relevant caches (nav tree, sidebar tree, page cache, search index)
- Optionally trigger browser reload via SSE or simple polling

**Acceptance Criteria**:
- Edit a `.md` file, refresh browser, see updated content
- Edit `_sidebar.md`, refresh browser, see updated sidebar
- Edit `config.json`, server reloads configuration

---

**Phase 1 Total Estimated Effort: ~12 days**

---

## Phase 2: Multi-Language and Product Scoping

**Goal**: Full i18n support, product-specific sidebars, language switching.

### Task 2.1: Multi-Locale Routing

**Effort**: 1 day

**Scope**:
- Update router to validate locale against `available_locales`
- Language switcher dropdown in header (shows available locales)
- Language switch preserves current slug when possible (fallback to locale root)
- Invalid locale returns 404

**Acceptance Criteria**:
- `/zh/getting-started` serves Chinese version
- Language switcher shows all available locales
- Switching lang on `/en/product-a/intro` goes to `/zh/product-a/intro` if exists, else `/zh/`

---

### Task 2.2: Product-Scoped Sidebar Resolution

**Effort**: 0.5 day

**Scope**:
- Implement sidebar resolution order from DESIGN.md section 3.3
- When URL contains a product path, look for product-specific `_sidebar.md` first
- Fallback chain: product sidebar, locale sidebar, auto-generated

**Acceptance Criteria**:
- `/en/product-a/intro` uses `en/product-a/_sidebar.md`
- `/en/intro` uses `en/_sidebar.md`
- If no sidebar file exists, auto-generate from folder contents

---

### Task 2.3: Auto-Generated Sidebar Fallback

**Effort**: 0.5 day

**Scope**:
- When no `_sidebar.md` exists, auto-generate sidebar from directory structure
- Use frontmatter `order` field for sorting, then alphabetical
- Use frontmatter `title` or first H1 as label

**Acceptance Criteria**:
- Folder with `.md` files but no `_sidebar.md` shows a working sidebar
- Order field respected
- Titles extracted from frontmatter or content

---

### Task 2.4: HTMX Partial Navigation

**Effort**: 1 day

**Scope**:
- Sidebar links use `hx-get` with partial content target
- Server detects HTMX requests (`HX-Request` header) and returns only `partials/content.html` + updated TOC
- Browser URL updated via `hx-push-url`
- Sidebar active state updated client-side or via HTMX swap

**Acceptance Criteria**:
- Clicking sidebar links loads content without full page reload
- URL updates in browser address bar
- Back/forward browser buttons work correctly
- Active sidebar item updates on navigation

---

**Phase 2 Total Estimated Effort: ~3 days**

---

## Phase 3: SEO, Search, and Polish

**Goal**: Production-ready SEO, search functionality, and UI polish.

### Task 3.1: SEO Meta Tags

**Effort**: 1 day

**Scope**:
- Implement `seo.py`
- Generate `<title>`, `<meta description>`, Open Graph tags, `hreflang` alternate links, canonical URL, JSON-LD structured data
- Auto-excerpt from content if no `description` in frontmatter (first 160 chars of text)
- All meta tags injected via Jinja2 template

**Acceptance Criteria**:
- View page source shows all SEO meta tags per DESIGN.md section 8.1
- `hreflang` tags list all available locale versions
- JSON-LD structured data validates at schema.org validator
- Pages without description use auto-excerpt

---

### Task 3.2: Sitemap Generation

**Effort**: 0.5 day

**Scope**:
- Auto-generate `/sitemap.xml` from all pages
- Include `lastmod` (file modification time), `changefreq`, `priority`
- Include `xhtml:link` alternates for each locale version
- Exclude pages with `noindex: true` in frontmatter
- Gated by `seo.auto_sitemap` config flag

**Acceptance Criteria**:
- `/sitemap.xml` returns valid XML sitemap
- All public pages listed with correct URLs
- Multi-language alternates included
- `noindex` pages excluded

---

### Task 3.3: robots.txt Generation

**Effort**: 0.25 day

**Scope**:
- Auto-generate `/robots.txt`
- Include sitemap reference
- Gated by `seo.auto_robots_txt` config flag

**Acceptance Criteria**:
- `/robots.txt` returns valid robots.txt with sitemap link

---

### Task 3.4: llms.txt and llms-full.txt

**Effort**: 0.5 day

**Scope**:
- Generate `/llms.txt` following the llms.txt standard: site title, description, list of all pages with title + URL + description
- Generate `/llms-full.txt`: concatenated plain-text content of all pages (stripped HTML)
- Gated by `seo.auto_llms_txt` config flag

**Acceptance Criteria**:
- `/llms.txt` returns structured index of all documentation
- `/llms-full.txt` returns full text content
- Both respect `noindex` flag

---

### Task 3.5: Client-Side Search

**Effort**: 1.5 days

**Scope**:
- Implement `search.py` - builds JSON search index at startup
- Endpoint `GET /api/search-index.json` serves the index
- `litedocs/static/js/search.js`: search modal UI, `Ctrl+K` keyboard shortcut, minisearch integration, result display with title + excerpt + breadcrumb, locale-aware (only search current locale)
- `partials/search_modal.html`: overlay with input and results list

**Acceptance Criteria**:
- `Ctrl+K` opens search modal
- Typing queries shows results in real-time
- Clicking a result navigates to the page
- Results scoped to current locale
- Empty state and no-results state handled

---

### Task 3.6: Callout and Admonition Styling

**Effort**: 0.5 day

**Scope**:
- Style the 5 callout types: NOTE (blue), TIP (green), IMPORTANT (purple), WARNING (yellow), CAUTION (red)
- Each with: colored left border, background tint, icon, title
- Dark mode variants

**Acceptance Criteria**:
- All 5 callout types visually distinct
- Icons rendered (Lucide SVG inline)
- Looks good in both light and dark mode

---

### Task 3.7: Mobile UI Polish

**Effort**: 1 day

**Scope**:
- Hamburger menu in header (mobile)
- Sidebar slides in as overlay with backdrop
- Touch-friendly tap targets (min 44px)
- Search modal fullscreen on mobile
- Scroll lock when modal/sidebar overlay open

**Acceptance Criteria**:
- Usable on 375px width screens
- Sidebar overlay smooth animation
- No content shift when sidebar opens
- All interactive elements easily tappable

---

### Task 3.8: Error Pages and Edge Cases

**Effort**: 0.5 day

**Scope**:
- Styled 404 page with: site header, search suggestion, link to home, language switcher
- Handle: empty docs folder, missing config.json (helpful error), malformed Markdown (graceful degradation)

**Acceptance Criteria**:
- 404 page matches site theme
- Server does not crash on malformed input
- Clear error messages in terminal for configuration issues

---

**Phase 3 Total Estimated Effort: ~6 days**

---

## Phase Summary

| Phase | Description                     | Effort     | Cumulative |
|-------|---------------------------------|------------|------------|
| 1     | Foundation and MVP              | ~12 days   | 12 days    |
| 2     | Multi-Language and Products     | ~3 days    | 15 days    |
| 3     | SEO, Search, and Polish         | ~6 days    | 21 days    |

**Total Estimated Effort: ~21 working days (roughly 1 month)**

---

## Testing Strategy

- **Unit tests** for each module: config, parser, scanner, seo, search
- **Integration tests** for server routes (FastAPI TestClient)
- **Fixture-based**: `tests/fixtures/sample-docs/` with a complete sample documentation site
- **Run with**: `pytest tests/ -v`
- **Test on every task completion** per RULE.md

---

## Definition of Done (Per Task)

1. Code implemented and working
2. Unit tests written and passing
3. Manual verification in browser (for UI tasks)
4. No regressions in existing tests
5. Code follows project conventions (English code/comments, per RULE.md)
