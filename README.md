# LiteDocs

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-206_passed-brightgreen)]()

A lightweight, Markdown folder-based documentation tool. Write Markdown, organize in folders, get a beautiful docs site — zero build step, no npm, no bundler, pure Python.

**Built and maintained by [Litestartup](https://www.litestartup.com)** — the all-in-one platform for startups.

> **Looking for more?** Check out [Litestartup](https://www.litestartup.com) for email marketing, transactional APIs, live chat, AI agents, and growth tools designed for startups.

## Features

- **Zero Config Start** — Point at any Markdown folder; `config.json` and `_sidebar.md` are auto-generated
- **Convention over Configuration** — Folder structure IS the configuration
- **Multi-Language** — Built-in i18n via locale directories (`en/`, `zh/`, ...)
- **Flat Mode** — Works without locale directories — just put `.md` files in root
- **Multi-Doc** — Serve multiple doc directories simultaneously with doc switcher
- **Daemon Mode** — Background process management with `start`, `stop`, `restart`, `status`, `logs`
- **Reverse Proxy** — `--base-path /docs` for Nginx sub-path deployments
- **Themes** — Switchable theme packages with templates and static assets
- **Dark Mode** — System-aware dark mode with manual toggle
- **HTMX Navigation** — Instant page transitions without full reload
- **SEO** — Sitemap, robots.txt, llms.txt, meta tags, JSON-LD, hreflang
- **Client Search** — Full-text search via MiniSearch (Ctrl+K)
- **Hot Reload** — File watcher for instant development feedback

## Tech Stack

| Category | Technologies |
|---|---|
| **Language** | Python 3.11+ |
| **Web Framework** | FastAPI, Uvicorn |
| **Templating** | Jinja2 |
| **Markdown** | markdown-it-py, mdit-py-plugins |
| **Frontend** | HTMX, Tailwind CSS (CDN), Vanilla JS |
| **Search** | MiniSearch (CDN) |
| **CLI** | Typer |
| **Config** | Pydantic |

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/litestartup-com/litedocs.git
cd litedocs

# Install dependencies
pip install -e .

# Start the server (demo mode — showcases all features)
litedocs serve
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

> **Note:** No external services required. LiteDocs ships with built-in demo docs so you can explore every feature immediately.

### Serve Your Own Docs

```bash
# Serve a Markdown folder (foreground, with hot reload)
litedocs serve ./my-docs

# Start as a background daemon
litedocs start ./my-docs

# Serve multiple directories
litedocs serve ./docs-a ./docs-b
```

When pointing at any Markdown folder, `config.json` and `_sidebar.md` are auto-generated if missing.

## CLI Commands

| Command | Description |
|---|---|
| `litedocs serve [DIRS]` | Start server in the **foreground** (development mode, hot reload) |
| `litedocs start [DIRS]` | Start server as a **background daemon** |
| `litedocs stop` | Stop a daemon (`--port 8000` or `--all`) |
| `litedocs restart` | Restart a daemon (`--port 8000`) |
| `litedocs status` | Show all running daemon instances |
| `litedocs logs` | View daemon logs (`--follow`, `--lines 50`, `--port 8000`) |
| `litedocs --version` | Show version |

**Multi-instance**: Run multiple daemons on different ports:

```bash
litedocs start ./docs-a --port 8000
litedocs start ./docs-b --port 9000
litedocs status
litedocs stop --all
```

### CLI Options

```bash
litedocs serve <DOCS_DIRS>... [--host 127.0.0.1] [--port 8000] [--reload/--no-reload] [--base-path /prefix]
litedocs start <DOCS_DIRS>... [--host 127.0.0.1] [--port 8000] [--reload/--no-reload] [--base-path /prefix]
litedocs stop [--port 8000] [--all]
litedocs restart [--port 8000]
litedocs logs [--port 8000] [--follow/--no-follow] [--lines 50]
```

## Project Structure

```
litedocs/
├── litedocs/                   # Main Python package
│   ├── __init__.py             #   Version
│   ├── __main__.py             #   python -m litedocs.cli entry
│   ├── cli.py                  #   Typer CLI (serve, start, stop, restart, status, logs)
│   ├── process.py              #   Daemon process management (PID, spawn, kill)
│   ├── server.py               #   FastAPI app, routes, multi-doc
│   ├── config.py               #   Pydantic config models
│   ├── parser.py               #   Markdown, nav, sidebar parsing
│   ├── scanner.py              #   Filesystem scanning
│   ├── renderer.py             #   Jinja2 rendering
│   ├── scaffold.py             #   Auto-generate config, sidebar, index
│   ├── seo.py                  #   Sitemap, robots.txt, llms.txt
│   ├── search.py               #   Search index builder
│   └── themes/default/         #   Built-in theme (templates, CSS, JS)
├── tests/                      # 206 pytest tests
├── litedocs-docs/              # Official manual (multi-doc example)
├── docs/                       # Internal design documents
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Docs Directory Structure

Every documentation directory follows this convention:

```
my-docs/
├── config.json              # Auto-generated if missing
├── assets/                  # Optional — images, favicon, logo
├── en/                      # Locale directory (ISO 639-1 code)
│   ├── _nav.md              # Optional — top tabs (hidden if absent)
│   ├── _sidebar.md          # Auto-generated if missing
│   ├── index.md             # Landing page
│   ├── getting-started.md   # Regular page
│   └── guide/               # Section directory
│       ├── _sidebar.md      # Section-specific sidebar (overrides locale)
│       ├── index.md
│       └── installation.md
└── zh/                      # Another locale
    ├── _nav.md
    ├── _sidebar.md
    └── index.md
```

**Flat mode**: If no locale directories (e.g. `en/`, `zh/`) are found, LiteDocs treats the directory as a flat docs folder. It auto-generates `config.json` with `flat_mode: true` and `_sidebar.md` at the root, then serves all `.md` files directly. No locale support, no language switcher.

### config.json

```json
{
  "site": {
    "title": "My Docs",
    "description": "Product documentation",
    "url": "https://docs.example.com",
    "base_path": ""
  },
  "locales": {
    "default": "en",
    "available": ["en", "zh"]
  },
  "theme": {
    "name": "default",
    "primary_color": "#3b82f6",
    "dark_mode": true
  }
}
```

- **`site.base_path`** — URL prefix for reverse proxy deployment (e.g. `"/docs"`). Can also be set via `--base-path` CLI flag.
- **`site.url`** — Required for sitemap.xml, robots.txt, and llms.txt generation.

### _nav.md — Top Navigation Tabs

```markdown
- [Guide](index.md)
- [API Reference](api/index.md) [badge:Beta]
- [GitHub](https://github.com/example/my-docs)
```

**Syntax:** `- [Label](path.md)` — one item per line. External links auto-detect `https://`. Optional `[badge:Text]` annotation.

### _sidebar.md — Sidebar Menu

```markdown
- [Introduction](index.md)
- **Getting Started**
  - [Installation](guide/installation.md)
  - [Configuration](guide/configuration.md)
- **API**
  - [List Users](api/users.md) [method:GET]
  - [Create User](api/users-create.md) [method:POST]
```

**Syntax:**
- `- [Label](path.md)` — link item
- `- **Group Title**` — collapsible group header (bold text, no link)
- Indent with 2 spaces for nesting
- `[method:GET]` — HTTP method badge (GET/POST/PUT/DELETE)
- `[badge:Text]` — general badge

### Sidebar Resolution Order

When visiting `/{doc}/{locale}/guide/install`:

1. `en/guide/_sidebar.md` — section-specific (highest priority)
2. `en/_sidebar.md` — locale-level fallback

### Markdown Pages

Standard Markdown with YAML frontmatter:

```markdown
---
title: Page Title
description: SEO description
order: 1
---

# Page Title

Content here. Supports **bold**, `code`, tables, task lists, code blocks with syntax highlighting, and callouts:

> [!NOTE]
> This is a note callout.

> [!TIP]
> This is a tip.

> [!WARNING]
> This is a warning.
```

## Multi-Doc Mode

Serve multiple documentation directories at once:

```bash
litedocs serve ./docs-api ./docs-guide ./docs-manual
```

URL scheme: `/{directory-name}/{locale}/{path}`

When multiple docs are served, the header shows a doc switcher dropdown.

## Deployment

### Docker (Recommended)

```bash
# docker-compose
docker compose up -d

# Or plain Docker
docker build -t litedocs .
docker run -d -p 8000:8000 -v ./my-docs:/app/docs litedocs
```

### Daemon Mode

```bash
litedocs start ./my-docs --port 8000
litedocs status
litedocs stop --port 8000
```

Daemon metadata and logs are stored in `.litedocs/` in the current working directory.

### Reverse Proxy (Nginx)

```bash
litedocs start ./my-docs --base-path /docs --port 8000
```

```nginx
location /docs/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

All internal links, static assets, and search URLs automatically include the prefix.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Start dev server (demo mode)
litedocs serve

# Start dev server with specific docs
litedocs serve tests/fixtures/sample-docs litedocs-docs
```

## About Litestartup

**[Litestartup](https://www.litestartup.com)** is the all-in-one platform built for startups — email marketing, transactional email API, live chat & help desk, AI agents, and growth tools. LiteDocs is one of our open-source projects designed to help developers ship documentation faster.

Explore more from Litestartup:
- [Litestartup Platform](https://www.litestartup.com) — All-in-one startup toolkit
- [Documentation](https://www.litestartup.com/docs) — Guides and API references
- [Blog](https://www.litestartup.com/blog) — Engineering and product insights

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [MIT License](LICENSE).

---

Made with ❤️ by [Litestartup](https://www.litestartup.com)
