---
title: Multi-Doc
description: How to serve multiple documentation directories
order: 5
---

# Multi-Doc Support

LiteDocs can serve multiple documentation directories simultaneously.

## Usage

```bash
# Single directory
litedocs serve ./my-docs

# Multiple directories
litedocs serve ./docs-api ./docs-guide
```

## URL Scheme

All pages follow the pattern:

```
/{doc_slug}/{locale}/{path}
```

- **doc_slug** — The directory name (e.g. `docs-api`)
- **locale** — Language code (e.g. `en`, `zh`)
- **path** — Page path within the locale

## Root Behavior

| Mode        | Root URL (`/`) behavior               |
|-------------|---------------------------------------|
| Single doc  | Redirects to `/{slug}/{locale}/`      |
| Multi-doc   | Redirects to `/_docs` listing page    |

## Doc Switcher

When multiple docs are served, the header automatically shows a dropdown to switch between documentation sites.

> [!NOTE]
> Each doc directory must contain its own `config.json` with independent settings.
