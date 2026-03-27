# LiteDocs - Product Design Document

> A lightweight, Markdown folder-based static documentation rendering tool.

## 1. Product Overview

### 1.1 Vision

LiteDocs is a minimal, fast, and beautiful documentation server that renders Markdown files from a folder into a modern Fumadocs-style website. It prioritizes **simplicity**, **zero configuration**, and **convention over configuration**.

### 1.2 Core Principles

- **Lightweight**: Minimal dependencies, pure Python backend, native JS frontend
- **Convention over Configuration**: Folder structure IS the configuration
- **Beautiful by Default**: Fumadocs-inspired clean, modern UI with dark mode
- **SEO-First**: Auto-generated sitemap, meta tags, structured data, llms.txt, GEO optimization
- **Multi-language**: Built-in i18n support via folder structure

### 1.3 Non-Goals (Out of Scope)

- Plugin system / extensible architecture (keep it simple)
- User authentication / access control
- CMS / editing interface
- Database or persistent storage

---

## 2. Technology Stack

| Component        | Choice                         | Rationale                                    |
|------------------|--------------------------------|----------------------------------------------|
| Language         | Python 3.11+                   | Ecosystem, readability, fast dev             |
| Web Framework    | FastAPI + Uvicorn              | Async, lightweight, built-in OpenAPI         |
| Template Engine  | Jinja2                         | Native FastAPI integration, mature           |
| Markdown Parser  | markdown-it-py + plugins       | Best Python MD ecosystem, extensible         |
| Frontmatter      | python-frontmatter (PyYAML)    | Parse YAML frontmatter in .md files          |
| CLI              | typer                          | Minimal, type-hint based CLI                 |
| Hot Reload       | watchfiles                     | Async file watching, fast                    |
| Partial Refresh  | HTMX                           | Lightweight (~14KB), no build step           |
| Styling          | Tailwind CSS (CDN/standalone)  | Utility-first, custom Fumadocs-like theme    |
| Icons            | Lucide (SVG inline)            | Consistent, lightweight                      |
| Client JS        | Vanilla JS (ES modules)        | Zero build step, no framework overhead       |
| Search           | minisearch (client-side)       | Tiny (~7KB), no server dependency            |
| Code Highlight   | highlight.js (CDN)             | Wide language support, themeable             |

### 2.1 Dependency Policy

- **Backend**: Only 6 core packages: `fastapi`, `uvicorn`, `jinja2`, `markdown-it-py`, `python-frontmatter`, `typer`, `watchfiles`
- **Frontend**: Zero build step. All assets via CDN or inline. No npm, no bundler.
- **Total pip dependencies**: Target < 15 (including transitive)

---

## 3. Folder Convention

### 3.1 Root Structure

```
my-docs/                          ← User-specified root directory
├── config.json                   ← Global configuration (required)
├── assets/                       ← Public static files: images, favicon, etc. (optional)
├── en/                           ← Language directory (ISO 639-1 code)
│   ├── _nav.md                   ← Top navigation (defines product/topic groups)
│   ├── _sidebar.md               ← Default sidebar (fallback)
│   ├── index.md                  ← Landing page for this locale
│   ├── product-a/
│   │   ├── _sidebar.md           ← Product-specific sidebar (highest priority)
│   │   ├── index.md
│   │   └── getting-started.md
│   └── product-b/
│       ├── _sidebar.md
│       └── ...
└── zh/
    ├── _nav.md
    ├── _sidebar.md
    └── ...                       ← Mirror structure of en/ (partial overlap OK)
```

### 3.2 Special Files

| File             | Scope            | Purpose                                    |
|------------------|------------------|--------------------------------------------|
| `config.json`    | Global           | Site title, locales, theme, SEO, analytics |
| `_nav.md`        | Per locale       | Top navigation bar items                   |
| `_sidebar.md`    | Per locale/topic | Left sidebar menu tree                     |
| `index.md`       | Per directory    | Default page for that path                 |
| `assets/`        | Global           | Static files served at `/assets/`          |

### 3.3 Sidebar Resolution Order

When user visits `/{doc}/{locale}/{product}/{slug}`:

1. `{locale}/{product}/_sidebar.md` ← Product-specific (highest priority)
2. `{locale}/_sidebar.md` ← Locale-level fallback
3. Auto-generated from folder structure ← Last resort fallback

---

## 4. Configuration Schema (`config.json`)

```json
{
  "site": {
    "title": "My Documentation",
    "description": "Product documentation for My Company",
    "url": "https://docs.example.com",
    "favicon": "assets/favicon.ico",
    "logo": "assets/logo.svg"
  },
  "locales": {
    "default": "en",
    "available": ["en", "zh"]
  },
  "theme": {
    "name": "default",
    "primary_color": "#3b82f6",
    "dark_mode": true
  },
  "seo": {
    "auto_sitemap": true,
    "auto_robots_txt": true,
    "auto_llms_txt": true,
    "og_image": "assets/og-image.png",
    "structured_data": true,
    "geo": {
      "enabled": true,
      "default_region": "US"
    }
  },
  "analytics": {
    "google_analytics": "",
    "plausible": "",
    "custom_head_scripts": []
  },
  "footer": {
    "copyright": "© 2026 My Company",
    "links": []
  }
}
```

All fields except `site.title` and `locales` are optional with sensible defaults.

---

## 5. Navigation & Sidebar Format Specification

### 5.1 `_nav.md` Format

Top navigation uses a flat Markdown list. Each item is a tab/link in the top bar.

```markdown
- [Introduction](index.md)
- [Product A](product-a/index.md)
- [Product B](product-b/index.md)
- [API Reference](api/index.md) [badge:Beta]
- [GitHub](https://github.com/my/repo)
```

**Rules**:
- Each `- [Label](path)` becomes a top nav tab
- External URLs (starting with `http`) render with an external-link icon
- `[badge:Text]` after a link adds a colored badge
- The nav item matching the current path gets `active` state

### 5.2 `_sidebar.md` Format

Sidebar uses Markdown list with **bold group titles** as separators.

```markdown
- [Introduction](README.md)
- [Quickstart](quickstart.md)
- **Features Guide**
  - [Mailbox](features/emails.md)
  - [Notifications](features/notifications.md)
- **API Reference**
  - [Introduction](api/README.md)
  - [Authentication](api/auth.md)
  - API Endpoints
    - [Users](api/users.md) [badge:New]
    - [Posts](api/posts.md) [method:POST]
- **Links**
  - [Twitter](https://x.com/example)
  - [Sitemap](/sitemap.xml)
```

**Rules**:
- `**Bold Text**` = Non-clickable group header (collapsible section)
- `- [Label](path.md)` = Clickable sidebar link
- Indentation (2 spaces) = Nesting level (supports unlimited depth)
- `[badge:Text]` = Inline badge (e.g., "New", "Beta", "Deprecated")
- `[method:POST]` = HTTP method badge for API docs (colored: GET=green, POST=blue, PUT=orange, DELETE=red)
- External URLs auto-detected, shown with external icon
- The sidebar item matching the current path gets `active` + `highlighted` state

### 5.3 Markdown Content Features

Standard Markdown plus:

| Feature             | Syntax                                 | Implementation              |
|---------------------|----------------------------------------|-----------------------------|
| Frontmatter         | `---\ntitle: ...\n---`                 | python-frontmatter          |
| Callout/Admonition  | `> [!NOTE]`, `> [!WARNING]`, etc.      | markdown-it-py plugin       |
| Task lists          | `- [x] Done item`                      | markdown-it-py plugin       |
| Tables              | Standard GFM tables                    | markdown-it-py plugin       |
| Code blocks         | ` ```lang ` with syntax highlight      | highlight.js (client-side)  |
| Footnotes           | `[^1]` references                      | markdown-it-py plugin       |
| Heading anchors     | Auto-generated `id` for each heading   | markdown-it-py plugin       |
| Image sizing        | `![alt](url =300x200)`                 | markdown-it-py attrs plugin |

### 5.4 Frontmatter Schema

```yaml
---
title: Getting Started              # Page title (overrides H1)
description: Learn how to start     # SEO meta description
icon: rocket                        # Lucide icon name (optional)
badge: New                          # Badge shown in sidebar (optional)
order: 1                            # Sort order in auto-generated sidebar (optional)
noindex: false                      # Exclude from sitemap/search (optional)
---
```

---

## 6. URL Routing

### 6.1 Route Patterns

| Pattern                            | Description                          |
|------------------------------------|--------------------------------------|
| `/`                                | Redirect to `/{default_locale}/`     |
| `/{locale}/`                       | Locale landing page (`index.md`)     |
| `/{locale}/{slug}`                 | Content page                         |
| `/{locale}/{product}/{slug}`       | Product-scoped content page          |
| `/assets/{path}`                   | Static files from `assets/` folder   |
| `/api/search-index.json`           | Search index for minisearch          |
| `/sitemap.xml`                     | Auto-generated sitemap               |
| `/robots.txt`                      | Auto-generated robots.txt            |
| `/llms.txt`                        | LLM-friendly site description        |
| `/llms-full.txt`                   | Full content dump for LLM crawlers   |

### 6.2 Slug Resolution

For a request to `/{locale}/{path}`:

1. Try `{locale}/{path}.md`
2. Try `{locale}/{path}/index.md`
3. Try `{locale}/{path}/README.md`
4. Return 404

### 6.3 Language Switching

When user switches from `/en/product-a/getting-started` to `zh`:
1. Try `/zh/product-a/getting-started` (same slug)
2. If not found, redirect to `/zh/` (locale root)

---

## 7. Page Layout & UI Design

### 7.1 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  [Logo] [Nav Tab 1] [Nav Tab 2] [Nav Tab 3]  🌐 🌙 🔍  │  ← Header
├──────────┬──────────────────────────────┬───────────────┤
│          │                              │               │
│ Sidebar  │     Main Content Area        │   TOC         │
│          │                              │  (right side) │
│ - Group  │  # Page Title                │               │
│   - Link │                              │  - Heading 1  │
│   - Link │  Content rendered from .md   │  - Heading 2  │
│ - Group  │                              │    - H3       │
│   - Link │                              │  - Heading 3  │
│          │                              │               │
│          │  ┌─────────┬─────────────┐   │               │
│          │  │ ← Prev  │ Next →      │   │               │
│          │  └─────────┴─────────────┘   │               │
├──────────┴──────────────────────────────┴───────────────┤
│  Footer: copyright, links                               │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Responsive Behavior

| Breakpoint   | Sidebar        | TOC            | Header Nav      |
|--------------|----------------|----------------|-----------------|
| Desktop ≥1280| Visible (left) | Visible (right)| Full tabs       |
| Tablet 768-1279| Collapsible overlay | Hidden    | Hamburger menu  |
| Mobile <768  | Collapsible overlay | Hidden    | Hamburger menu  |

### 7.3 Dark Mode

- Toggle button in header (sun/moon icon)
- Persisted in `localStorage`
- Respects `prefers-color-scheme` on first visit
- Tailwind `dark:` classes for all components

### 7.4 UI Style Guide (Fumadocs-Inspired)

- **Font**: System font stack (`-apple-system, BlinkMacSystemFont, Segoe UI, ...`)
- **Content max-width**: 768px
- **Sidebar width**: 280px
- **TOC width**: 220px
- **Border radius**: `0.5rem` (rounded-lg)
- **Colors**: Neutral grays + single primary accent color from config
- **Transitions**: Subtle 150ms ease for hover/active states
- **Code blocks**: Rounded, with language label and copy button

---

## 8. SEO & GEO Optimization

### 8.1 Auto-Generated Meta Tags

Every page outputs:
```html
<title>{page.title} - {site.title}</title>
<meta name="description" content="{page.description or auto-excerpt}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{site.url}/{locale}/{slug}">

<!-- Open Graph -->
<meta property="og:title" content="{page.title}">
<meta property="og:description" content="{page.description}">
<meta property="og:url" content="{site.url}/{locale}/{slug}">
<meta property="og:image" content="{seo.og_image}">
<meta property="og:type" content="article">
<meta property="og:locale" content="{locale}">

<!-- Alternate languages -->
<link rel="alternate" hreflang="en" href="{site.url}/en/{slug}">
<link rel="alternate" hreflang="zh" href="{site.url}/zh/{slug}">
<link rel="alternate" hreflang="x-default" href="{site.url}/en/{slug}">

<!-- JSON-LD Structured Data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "{page.title}",
  "description": "{page.description}",
  "inLanguage": "{locale}",
  "url": "{canonical_url}"
}
</script>
```

### 8.2 `/sitemap.xml`

Auto-generated from all non-`noindex` pages:
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://docs.example.com/en/getting-started</loc>
    <lastmod>2026-03-18</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="zh" href="https://docs.example.com/zh/getting-started"/>
  </url>
  ...
</urlset>
```

### 8.3 `/robots.txt`

```
User-agent: *
Allow: /
Sitemap: https://docs.example.com/sitemap.xml
```

### 8.4 `/llms.txt` (LLM-Friendly Crawling)

Following the emerging `llms.txt` standard:
```
# My Documentation
> Product documentation for My Company

## Docs
- [Getting Started](https://docs.example.com/en/getting-started): Learn how to start
- [API Reference](https://docs.example.com/en/api/): Complete API documentation
...
```

### 8.5 `/llms-full.txt`

Full concatenated content of all pages (plain text, no HTML) for LLM training/indexing. Gated by config flag.

### 8.6 GEO Optimization

- `hreflang` tags on all pages (multi-language alternate links)
- `og:locale` meta tag
- Structured data with `inLanguage`
- Geographic region hints in config (optional `meta geo.*` tags)

---

## 9. Search

### 9.1 Architecture

- **Index Build**: Server generates `/api/search-index.json` at startup (and on file change)
- **Index Content**: Page title, description, headings, first 500 chars of body, slug, locale
- **Client**: minisearch loads index on first search interaction (lazy)
- **UI**: Search modal (triggered by `Ctrl+K` or search icon), shows results with title + excerpt + breadcrumb

### 9.2 Search Index Schema

```json
[
  {
    "id": "en/product-a/getting-started",
    "title": "Getting Started",
    "description": "Learn how to start",
    "headings": "Installation, Configuration, First Steps",
    "body": "First 500 characters...",
    "locale": "en",
    "product": "product-a"
  }
]
```

---

## 10. Core Data Models

### 10.1 Server-Side (Python)

```
SiteConfig
  ├── title: str
  ├── description: str
  ├── url: str
  ├── favicon: str
  ├── logo: str
  ├── default_locale: str
  ├── available_locales: list[str]
  ├── primary_color: str
  ├── dark_mode: bool
  ├── seo: SEOConfig
  ├── analytics: AnalyticsConfig
  └── footer: FooterConfig

NavNode
  ├── label: str
  ├── href: str | None
  ├── is_external: bool
  ├── badge: str | None
  └── is_active: bool

SidebarNode
  ├── label: str
  ├── href: str | None
  ├── is_group: bool          ← True for **Bold Group** headers
  ├── is_external: bool
  ├── badge: str | None
  ├── method: str | None      ← HTTP method badge (GET/POST/PUT/DELETE)
  ├── is_active: bool
  ├── is_expanded: bool
  └── children: list[SidebarNode]

PageContext
  ├── slug: str
  ├── locale: str
  ├── product: str | None
  ├── title: str
  ├── description: str
  ├── icon: str | None
  ├── frontmatter: dict
  ├── toc: list[TocHeading]
  ├── html_content: str
  ├── prev_page: NavLink | None
  └── next_page: NavLink | None

TocHeading
  ├── id: str                  ← Anchor ID
  ├── text: str
  └── level: int               ← 2-6

LocaleContext
  ├── locale: str
  ├── nav_items: list[NavNode]
  ├── sidebar_tree: list[SidebarNode]
  └── current_product: str | None
```

---

## 11. Runtime Flow

### 11.1 Startup

```
1. CLI: `litedocs serve /path/to/docs [--port 8000] [--host 0.0.0.0]`
2. Load & validate config.json → SiteConfig
3. Scan all locale directories → build locale map
4. Parse all _nav.md and _sidebar.md → cache NavNode/SidebarNode trees
5. Build search index → cache as JSON
6. Start FastAPI server with uvicorn
7. Start watchfiles watcher → invalidate cache on file changes
```

### 11.2 Request Handling

```
GET /{locale}/{path}
  │
  ├── Resolve locale → 404 if invalid
  ├── Resolve slug → find .md file (see §6.2)
  ├── Load _nav.md for locale → mark active item
  ├── Resolve sidebar (see §3.3) → mark active item
  ├── Parse .md → frontmatter + HTML + TOC
  ├── Determine prev/next pages from sidebar order
  ├── Render Jinja2 template with full context
  └── Return HTML (with HTMX partial support)
```

### 11.3 HTMX Partial Loading

- Sidebar link clicks use `hx-get` + `hx-target="#content"` for instant navigation
- Full page is loaded on direct URL access or hard refresh
- Browser URL updated via `hx-push-url`
- Language switch triggers full page reload (nav + sidebar change)

---

## 12. Project Source Structure

```
litedocs/
├── litedocs/                     ← Python package
│   ├── __init__.py
│   ├── cli.py                    ← Typer CLI (serve, build commands)
│   ├── config.py                 ← SiteConfig loading & validation (Pydantic)
│   ├── scanner.py                ← Directory scanning, locale/product discovery
│   ├── parser.py                 ← Markdown parsing (nav, sidebar, content)
│   ├── models.py                 ← Data models (NavNode, SidebarNode, PageContext, etc.)
│   ├── server.py                 ← FastAPI app, routes, middleware
│   ├── renderer.py               ← Jinja2 rendering, template context assembly
│   ├── seo.py                    ← Sitemap, robots.txt, llms.txt, meta tag generation
│   ├── search.py                 ← Search index builder
│   ├── watcher.py                ← File watcher for hot reload
│   └── templates/                ← Jinja2 templates
│       ├── base.html             ← Full page layout
│       ├── page.html             ← Content page (extends base)
│       ├── partials/
│       │   ├── header.html       ← Top navigation bar
│       │   ├── sidebar.html      ← Left sidebar
│       │   ├── toc.html          ← Right-side table of contents
│       │   ├── content.html      ← Main content area (HTMX target)
│       │   ├── footer.html       ← Footer
│       │   ├── search_modal.html ← Search overlay
│       │   └── pagination.html   ← Prev/Next navigation
│       └── errors/
│           └── 404.html
├── litedocs/static/              ← Built-in static assets
│   ├── css/
│   │   └── style.css             ← Custom styles (Tailwind utilities + overrides)
│   ├── js/
│   │   ├── app.js                ← Main JS (dark mode, TOC scroll spy, sidebar toggle)
│   │   ├── search.js             ← Search modal + minisearch integration
│   │   └── copy-code.js          ← Code block copy button
│   └── icons/                    ← Lucide SVG icons (inline subset)
├── tests/                        ← Unit tests
│   ├── test_config.py
│   ├── test_parser.py
│   ├── test_scanner.py
│   ├── test_seo.py
│   ├── test_server.py
│   └── fixtures/                 ← Test docs folder fixtures
│       └── sample-docs/
├── pyproject.toml                ← Package config, dependencies
├── README.md
├── RULE.md
├── LICENSE
└── docs/
    ├── REQUIEMENT.md
    ├── DESIGN.md                 ← This file
    ├── TASKS.md                  ← Development task breakdown
    └── CONVENTIONS.md            ← Format specs & conventions
```

---

## 13. Performance Considerations

- **Caching**: All parsed nav/sidebar trees and rendered pages cached in memory; invalidated by file watcher
- **Lazy parsing**: Content .md files parsed on first request, then cached
- **Search index**: Built once at startup, rebuilt on file changes
- **Static assets**: Served with cache headers (1 hour for dev, configurable)
- **Tailwind**: Use CDN (play CDN) for dev, standalone CLI for production build (optional)

---

## 14. Theme Architecture

### 14.1 Theme Directory Structure

Themes are stored under `litedocs/themes/`. Each theme is a self-contained directory:

```
litedocs/themes/
├── __init__.py
└── default/
    ├── theme.json                ← Theme metadata
    ├── templates/
    │   ├── base.html             ← Full HTML shell
    │   ├── page.html             ← Extends base, three-column layout
    │   ├── partials/
    │   │   ├── header.html       ← Two-row header (logo+search+toggles / nav tabs)
    │   │   ├── sidebar.html
    │   │   ├── content.html
    │   │   ├── toc.html
    │   │   ├── pagination.html
    │   │   ├── footer.html
    │   │   └── search_modal.html
    │   └── errors/
    │       └── 404.html
    └── static/
        ├── css/style.css
        └── js/
            ├── app.js
            └── copy-code.js
```

### 14.2 Theme Selection

The active theme is set in `config.json` via `theme.name` (default: `"default"`).
Templates load from `themes/{name}/templates/`, static assets are served at `/_themes/{name}/`.

### 14.3 Creating a Custom Theme

1. Copy `themes/default/` to `themes/my-theme/`
2. Edit `theme.json` metadata
3. Modify templates and static assets
4. Set `"theme": { "name": "my-theme" }` in `config.json`

---

## 15. Multi-Doc Support

### 15.1 URL Scheme

All page URLs follow the pattern: `/{doc_slug}/{locale}/{path}`

- `doc_slug` — derived from the docs directory name
- `locale` — language code (e.g. `en`, `zh`)
- `path` — page path within the locale

### 15.2 CLI Usage

```bash
# Single doc directory
litedocs serve ./my-docs

# Multiple doc directories
litedocs serve ./docs-api ./docs-guide
```

### 15.3 Root Redirect

- **Single doc**: `/ → /{doc_slug}/{default_locale}/`
- **Multiple docs**: `/ → /_docs` (listing page)

### 15.4 Doc Switcher UI

When multiple docs are served, the header displays a doc switcher dropdown
allowing users to navigate between documentation sites.

### 15.5 Asset Isolation

Each doc directory's assets are mounted at `/{doc_slug}/assets/`.
Theme static files are shared and served at `/_themes/{theme_name}/`.

---

## 16. Future Considerations (Not in MVP)

- `litedocs build` - Static site export (HTML files)
- Mermaid diagram support
- Versioned documentation
- Runtime theme switching via UI
- Plugin hooks for custom markdown extensions
- PDF export
