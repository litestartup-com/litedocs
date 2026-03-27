---
title: Project Structure
description: LiteDocs codebase layout and module overview
order: 1
---

# Project Structure

```
litedocs/
├── litedocs/               # Main package
│   ├── __init__.py         # Version
│   ├── cli.py              # Typer CLI (serve command)
│   ├── server.py           # FastAPI app, routes, multi-doc registry
│   ├── config.py           # Pydantic config models
│   ├── parser.py           # Markdown, nav, sidebar parsing
│   ├── scanner.py          # Filesystem scanning & page resolution
│   ├── renderer.py         # Jinja2 rendering & template context
│   └── themes/
│       └── default/        # Built-in theme
│           ├── theme.json
│           ├── templates/  # Jinja2 templates
│           └── static/     # CSS, JS
├── tests/                  # Pytest test suite
│   ├── fixtures/
│   │   └── sample-docs/    # Test fixture docs
│   └── test_*.py
├── litedocs-docs/          # Official manual (multi-doc example)
├── docs/                   # Internal design documents
│   ├── DESIGN.md
│   ├── TASKS.md
│   └── CONVENTIONS.md
└── docker-compose.yml
```

## Key Modules

| Module       | Responsibility                                    |
|--------------|---------------------------------------------------|
| `cli.py`     | CLI entry point, argument parsing                 |
| `server.py`  | FastAPI app creation, routing, static file mounts |
| `config.py`  | `config.json` schema and validation               |
| `parser.py`  | Markdown to HTML, nav/sidebar parsing             |
| `scanner.py` | Filesystem scanning, page resolution              |
| `renderer.py`| Jinja2 context assembly, active state marking     |

## Request Flow

1. Browser requests `/{doc_slug}/{locale}/{path}`
2. `server.py` routes to the correct `DocsApp` instance
3. `scanner.py` resolves the Markdown file
4. `parser.py` converts Markdown to HTML
5. `renderer.py` assembles template context
6. Jinja2 renders the HTML response
