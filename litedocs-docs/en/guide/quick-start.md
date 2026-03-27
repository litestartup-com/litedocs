---
title: Quick Start
description: Set up your first LiteDocs site in 2 minutes
order: 1
---

# Quick Start

## 1. Install

```bash
pip install litedocs
```

## 2. Create Docs Folder

```
my-docs/
├── config.json
└── en/
    ├── _nav.md
    ├── _sidebar.md
    └── index.md
```

**config.json:**

```json
{
  "site": { "title": "My Docs" },
  "locales": { "default": "en", "available": ["en"] }
}
```

**en/_nav.md:**

```markdown
- [Guide](guide/index.md)
```

**en/_sidebar.md:**

```markdown
- [Home](index.md)
```

**en/index.md:**

```markdown
---
title: Home
---

# Welcome

Your documentation starts here.
```

## 3. Start Server

```bash
litedocs serve ./my-docs
```

Open `http://localhost:8000` in your browser.

> [!TIP]
> Add `--port 3000` to use a different port. Use `--no-reload` to disable file watching.
