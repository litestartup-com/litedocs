---
title: Folder Structure
description: How LiteDocs organizes documentation files
order: 2
---

# Folder Structure

LiteDocs uses folder conventions instead of complex configuration files.

## Layout

```
my-docs/
├── config.json           # Required - site configuration
├── assets/               # Optional - images, favicon, etc.
├── en/                   # Language directory (ISO 639-1)
│   ├── _nav.md           # Top navigation tabs
│   ├── _sidebar.md       # Left sidebar menu
│   ├── index.md          # Landing page
│   ├── getting-started.md
│   └── api/              # Product/section directory
│       ├── _sidebar.md   # Section-specific sidebar
│       ├── index.md
│       └── users.md
└── zh/                   # Another language
    ├── _nav.md
    └── ...
```

## Special Files

| File           | Scope        | Purpose                      |
|----------------|--------------|------------------------------|
| `config.json`  | Global       | Site title, locales, theme   |
| `_nav.md`      | Per locale   | Top navigation bar           |
| `_sidebar.md`  | Per section  | Left sidebar menu            |
| `index.md`     | Per directory| Default page for that path   |

## Sidebar Resolution

When visiting `/{doc}/{locale}/{section}/{page}`:

1. `{section}/_sidebar.md` — Section-specific (highest priority)
2. `{locale}/_sidebar.md` — Locale-level fallback

> [!NOTE]
> Section directories are auto-detected when they contain a `_sidebar.md` file.
