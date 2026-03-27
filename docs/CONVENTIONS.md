# LiteDocs - Format Conventions and Specifications

> Detailed specifications for all file formats, naming conventions, and parsing rules.

---

## 1. Folder Naming Conventions

### 1.1 Locale Directories

- Must be valid ISO 639-1 two-letter codes (lowercase): `en`, `zh`, `ja`, `ko`, `fr`, `de`, etc.
- Only directories matching configured `locales.available` in `config.json` are recognized
- Other directories at root level are ignored (except `assets/`)

### 1.2 Product Directories

- Any subdirectory inside a locale directory that contains a `_sidebar.md` is treated as a "product"
- Directory names must be lowercase, use hyphens for word separation: `product-a`, `api-reference`, `user-guide`
- No spaces, no uppercase, no special characters except hyphens

### 1.3 Content Files

- All content files use `.md` extension
- Filenames must be lowercase, hyphen-separated: `getting-started.md`, `api-authentication.md`
- `index.md` or `README.md` serves as the default page for a directory
- Files starting with `_` are special files (e.g., `_nav.md`, `_sidebar.md`) and are NOT rendered as content pages

---

## 2. `config.json` Full Specification

### 2.1 Complete Schema

```jsonc
{
  // REQUIRED
  "site": {
    "title": "string",              // REQUIRED - Site title shown in header and <title> tag
    "description": "string",        // Optional - Default meta description
    "url": "string",                // Optional - Canonical base URL (e.g. "https://docs.example.com")
    "favicon": "string",            // Optional - Path relative to docs root (default: none)
    "logo": "string"                // Optional - Path relative to docs root (default: none)
  },

  // REQUIRED
  "locales": {
    "default": "string",            // REQUIRED - Default locale code (e.g. "en")
    "available": ["string"]         // REQUIRED - List of available locale codes
  },

  // Optional
  "theme": {
    "primary_color": "string",      // CSS color value (default: "#3b82f6")
    "dark_mode": true               // Enable dark mode toggle (default: true)
  },

  // Optional
  "seo": {
    "auto_sitemap": true,           // Generate /sitemap.xml (default: true)
    "auto_robots_txt": true,        // Generate /robots.txt (default: true)
    "auto_llms_txt": true,          // Generate /llms.txt and /llms-full.txt (default: true)
    "og_image": "string",           // Path to default OG image (default: none)
    "structured_data": true,        // Add JSON-LD to pages (default: true)
    "geo": {
      "enabled": false,             // Enable GEO meta tags (default: false)
      "default_region": "string"    // ISO 3166-1 country code (default: none)
    }
  },

  // Optional
  "analytics": {
    "google_analytics": "string",   // GA4 measurement ID (e.g. "G-XXXXXXXXXX")
    "plausible": "string",          // Plausible domain
    "custom_head_scripts": [        // Additional <script> tags injected in <head>
      "<script src='...'></script>"
    ]
  },

  // Optional
  "footer": {
    "copyright": "string",          // Copyright text (default: none)
    "links": [                      // Footer links
      { "label": "string", "href": "string" }
    ]
  }
}
```

### 2.2 Minimal Valid `config.json`

```json
{
  "site": {
    "title": "My Docs"
  },
  "locales": {
    "default": "en",
    "available": ["en"]
  }
}
```

---

## 3. `_nav.md` Format Specification

### 3.1 Syntax

Top navigation is defined as a flat Markdown unordered list.

```markdown
- [Label](relative/path.md)
- [Label](relative/path.md) [badge:Text]
- [Label](https://external-url.com)
```

### 3.2 Parsing Rules

| Element | Format | Result |
|---------|--------|--------|
| Internal link | `- [Label](path.md)` | Nav tab pointing to `/{locale}/path` |
| External link | `- [Label](https://...)` | Nav link with external icon, opens in new tab |
| Badge | `[badge:Text]` after link | Colored inline badge next to label |

### 3.3 Path Resolution

- All paths in `_nav.md` are relative to the locale directory
- `product-a/index.md` resolves to `/{locale}/product-a/`
- `index.md` resolves to `/{locale}/`

### 3.4 Active State

- A nav item is "active" when the current URL starts with the nav item's resolved path
- Only one nav item can be active at a time (first match wins)

### 3.5 Example

```markdown
- [Home](index.md)
- [User Guide](guide/index.md)
- [API Reference](api/index.md) [badge:Beta]
- [GitHub](https://github.com/example/repo)
```

Renders as:

```
[Home] [User Guide] [API Reference (Beta)] [GitHub ↗]
```

---

## 4. `_sidebar.md` Format Specification

### 4.1 Syntax

Sidebar uses Markdown unordered list with nesting via indentation (2 spaces per level).

```markdown
- [Link Label](path.md)
- **Group Title**
  - [Child Link](path.md)
  - [Child Link](path.md) [badge:New]
  - Nested Group
    - [Deep Link](path.md) [method:GET]
```

### 4.2 Element Types

| Type | Format | Description |
|------|--------|-------------|
| Link | `- [Label](path.md)` | Clickable navigation link |
| Group header | `- **Bold Text**` | Non-clickable, collapsible section header |
| Plain group | `- Plain Text` (with children) | Non-clickable group, inferred from having child items |
| External link | `- [Label](https://...)` | Opens in new tab with external icon |
| Badge | `[badge:Text]` after link | Inline colored badge |
| Method tag | `[method:GET]` after link | HTTP method badge (colored by method) |

### 4.3 Method Tag Colors

| Method | Color |
|--------|-------|
| GET | Green (`#22c55e`) |
| POST | Blue (`#3b82f6`) |
| PUT | Orange (`#f59e0b`) |
| PATCH | Orange (`#f59e0b`) |
| DELETE | Red (`#ef4444`) |

### 4.4 Nesting Rules

- Indentation: 2 spaces per level
- Maximum recommended depth: 4 levels
- A group header or plain text item with indented children below it becomes a collapsible section
- Collapsible sections are **collapsed by default**, except the section containing the active page

### 4.5 Path Resolution

- All paths are relative to the directory containing the `_sidebar.md` file
- For locale-level `_sidebar.md` (e.g., `en/_sidebar.md`): paths relative to `en/`
- For product-level `_sidebar.md` (e.g., `en/api/_sidebar.md`): paths relative to `en/api/`

### 4.6 Active State

- The sidebar item whose resolved path matches the current URL gets `active` class
- All parent groups of the active item are auto-expanded
- Active item is scrolled into view on page load

### 4.7 Full Example

```markdown
- [Introduction](README.md)
- [Quick Start](quickstart.md)
- **Features**
  - [Email](features/email.md)
  - [Notifications](features/notifications.md) [badge:New]
  - [Webhooks](features/webhooks.md)
- **API Reference**
  - [Authentication](api/auth.md)
  - User Endpoints
    - [List Users](api/users-list.md) [method:GET]
    - [Create User](api/users-create.md) [method:POST]
    - [Delete User](api/users-delete.md) [method:DELETE]
  - [Error Codes](api/errors.md)
- **Links**
  - [GitHub](https://github.com/example/repo)
  - [Discord](https://discord.gg/example)
```

---

## 5. Content Markdown Specification

### 5.1 Frontmatter

Every `.md` content file MAY include YAML frontmatter:

```yaml
---
title: Page Title                   # Overrides first H1 as page title
description: Short description      # Used for meta description and search
icon: rocket                        # Lucide icon name (shown in sidebar if applicable)
badge: New                          # Badge text (shown in sidebar if applicable)
order: 10                           # Numeric sort order for auto-generated sidebar
noindex: false                      # If true, excluded from sitemap and search index
---
```

All fields are optional. If `title` is not set, the first H1 heading is used. If no H1 exists, the filename (de-hyphenated, title-cased) is used.

### 5.2 Callout / Admonition Syntax

Uses GitHub-style callout syntax:

```markdown
> [!NOTE]
> This is informational content.

> [!TIP]
> This is a helpful tip.

> [!IMPORTANT]
> Critical information.

> [!WARNING]
> Something to be cautious about.

> [!CAUTION]
> Dangerous action that may cause issues.
```

### 5.3 Callout Rendering

Each callout type renders with distinct styling:

| Type | Icon | Border Color | Background |
|------|------|-------------|------------|
| NOTE | `info` | Blue | Light blue |
| TIP | `lightbulb` | Green | Light green |
| IMPORTANT | `message-circle` | Purple | Light purple |
| WARNING | `alert-triangle` | Yellow | Light yellow |
| CAUTION | `octagon-x` | Red | Light red |

### 5.4 Heading Anchors

All headings (h1-h6) automatically receive an `id` attribute:
- Generated from heading text
- Lowercased, spaces replaced with hyphens
- Special characters removed
- Duplicate IDs get numeric suffix: `heading`, `heading-1`, `heading-2`

Example: `## Getting Started` becomes `<h2 id="getting-started">Getting Started</h2>`

### 5.5 Table of Contents (TOC) Extraction

- TOC is generated from h2, h3, and h4 headings only
- h1 is treated as page title, not included in TOC
- h5 and h6 are too deep for TOC
- Each TOC entry links to the heading's anchor ID

### 5.6 Code Blocks

````markdown
```python
def hello():
    print("world")
```
````

Renders with:
- Language label in top-right corner (e.g., "python")
- Copy button (clipboard icon)
- Syntax highlighting via highlight.js
- Rounded corners, subtle background

### 5.7 Images

```markdown
![Alt text](assets/screenshot.png)
```

- Relative paths resolved from the page's directory
- Images in `assets/` accessible via `/assets/` URL
- Images are rendered responsive (max-width: 100%)

### 5.8 Links

| Type | Format | Behavior |
|------|--------|----------|
| Internal | `[text](other-page.md)` | Navigate within docs, resolved relative to current file |
| Anchor | `[text](#heading-id)` | Scroll to heading on same page |
| External | `[text](https://...)` | Opens in new tab, external icon appended |

---

## 6. URL Conventions

### 6.1 Slug Generation

| File Path | URL |
|-----------|-----|
| `en/index.md` | `/en/` |
| `en/getting-started.md` | `/en/getting-started` |
| `en/product-a/index.md` | `/en/product-a/` |
| `en/product-a/setup.md` | `/en/product-a/setup` |
| `en/product-a/api/users.md` | `/en/product-a/api/users` |

### 6.2 Rules

- No `.md` extension in URLs
- No `.html` extension in URLs
- `index.md` and `README.md` resolve to directory path (trailing slash)
- All URLs are lowercase
- Files starting with `_` are never routable

---

## 7. Asset Conventions

### 7.1 Public Assets

Files in `{docs-root}/assets/` are served at `/assets/`:
- `assets/logo.svg` is at `/assets/logo.svg`
- `assets/img/screenshot.png` is at `/assets/img/screenshot.png`

### 7.2 Supported Static File Types

| Category | Extensions |
|----------|-----------|
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico` |
| Documents | `.pdf` |
| Data | `.json`, `.xml` |
| Other | `.txt`, `.css`, `.js` |

---

## 8. SEO File Conventions

### 8.1 `/sitemap.xml`

- Auto-generated at server startup and on content changes
- Includes all pages except those with `noindex: true`
- Uses `site.url` from config for absolute URLs
- Includes `<xhtml:link rel="alternate">` for each locale variant

### 8.2 `/robots.txt`

```
User-agent: *
Allow: /
Sitemap: {site.url}/sitemap.xml
```

### 8.3 `/llms.txt`

Follows the llms.txt specification (https://llmstxt.org/):

```
# {site.title}
> {site.description}

## Docs

- [{page.title}]({page.url}): {page.description}
- ...
```

### 8.4 `/llms-full.txt`

Full plain-text dump of all documentation content, separated by page headers:

```
# {page.title}
URL: {page.url}

{page plain text content, HTML stripped}

---

# {next page title}
...
```

---

## 9. Coding Conventions (Development)

### 9.1 General

- All code, comments, and documentation in **English** (per RULE.md)
- Conversations with AI in **Chinese** (per RULE.md)
- Python code follows PEP 8
- Type hints required on all function signatures
- Docstrings in Google style

### 9.2 Python

- Python 3.11+ features allowed
- Use `pathlib.Path` for all file system operations
- Use `pydantic.BaseModel` for all data models with validation
- Use `async def` for all FastAPI route handlers
- Imports sorted: stdlib, third-party, local (isort compatible)

### 9.3 JavaScript

- Vanilla ES modules (no framework, no bundler)
- `const` and `let` only (no `var`)
- Use `document.querySelector` / `querySelectorAll`
- Event delegation where possible
- No jQuery, no lodash, no utility libraries

### 9.4 CSS

- Tailwind utility classes in HTML templates
- Custom CSS only for things Tailwind cannot handle (e.g., Markdown content typography)
- CSS custom properties for theme colors (allows runtime primary color change)
- BEM-like naming for custom classes: `.ld-sidebar`, `.ld-toc`, `.ld-callout--warning`

### 9.5 Templates (Jinja2)

- Use template inheritance (`{% extends "base.html" %}`)
- Use macros for reusable components
- Use `{% include %}` for partials
- All user content escaped by default (Jinja2 auto-escape)
- Raw HTML from Markdown rendering marked as `{{ content | safe }}`

---

## 10. Testing Conventions

### 10.1 Test Structure

```
tests/
├── conftest.py              ← Shared fixtures
├── test_config.py           ← Config loading tests
├── test_parser.py           ← Markdown parsing tests
├── test_scanner.py          ← Directory scanning tests
├── test_seo.py              ← SEO generation tests
├── test_server.py           ← Route integration tests
└── fixtures/
    └── sample-docs/         ← Complete sample docs site
        ├── config.json
        ├── assets/
        ├── en/
        │   ├── _nav.md
        │   ├── _sidebar.md
        │   ├── index.md
        │   ├── getting-started.md
        │   └── api/
        │       ├── _sidebar.md
        │       ├── index.md
        │       └── users.md
        └── zh/
            ├── _nav.md
            ├── _sidebar.md
            └── index.md
```

### 10.2 Test Rules

- Every new feature must have unit tests (per RULE.md)
- Run `pytest tests/ -v` after every task
- Use `pytest-asyncio` for async test functions
- Use FastAPI `TestClient` for route tests
- Fixtures provide complete sample docs site
