---
title: Theme System
description: How the LiteDocs theme architecture works internally
order: 2
---

# Theme System

## Directory Layout

Each theme lives under `litedocs/themes/{name}/`:

```
litedocs/themes/default/
├── theme.json              # Theme metadata
├── templates/
│   ├── base.html           # HTML shell
│   ├── page.html           # Full page (extends base)
│   ├── macros/
│   │   └── sidebar_node.html  # Reusable sidebar macro
│   ├── partials/
│   │   ├── header.html
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

## Static Asset Serving

Theme static files are mounted at `/_themes/{name}/`. Templates reference them as:

```html
<link rel="stylesheet" href="/_themes/default/css/style.css">
```

## Template Context

The renderer provides these variables to all templates:

| Variable          | Type        | Description                    |
|-------------------|-------------|--------------------------------|
| `page`            | `Page`      | Current page data              |
| `config`          | `SiteConfig`| Site configuration             |
| `nav_items`       | `list`      | Top nav items with active state|
| `sidebar`         | `list`      | Sidebar nodes with active state|
| `locale`          | `str`       | Current locale code            |
| `doc_slug`        | `str`       | Current doc directory name     |
| `doc_list`        | `list`      | All registered docs            |
| `current_path`    | `str`       | Current URL path               |
| `available_locales`| `list`     | All available locales          |
