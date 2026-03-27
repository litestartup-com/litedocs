---
title: Testing
description: How to run and write tests for LiteDocs
order: 4
---

# Testing

## Run Tests

```bash
pytest tests/ -v
```

## Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── fixtures/
│   └── sample-docs/     # Test doc directory
├── test_config.py       # Config model tests
├── test_parser.py       # Markdown/nav/sidebar parser tests
├── test_renderer.py     # Renderer and active state tests
├── test_scanner.py      # Filesystem scanner tests
└── test_server.py       # HTTP endpoint integration tests
```

## Writing Tests

- Use `sample_docs_path` fixture for filesystem tests
- Use `client` fixture (FastAPI `TestClient`) for HTTP tests
- Test both English and Chinese locales
- Test both full page and HTMX partial responses

## Coverage

```bash
pytest tests/ -v --cov=litedocs --cov-report=term-missing
```
