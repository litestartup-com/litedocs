---
title: Themes
description: How to use and create themes in LiteDocs
order: 4
---

# Themes

LiteDocs supports switchable themes. Each theme is a self-contained directory with templates and static assets.

## Selecting a Theme

Set `theme.name` in your `config.json`:

```json
{
  "theme": {
    "name": "default",
    "primary_color": "#8b5cf6"
  }
}
```

## Theme Structure

```
litedocs/themes/default/
├── theme.json
├── templates/
│   ├── base.html
│   ├── page.html
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

## Creating a Custom Theme

1. Copy the `default` theme directory
2. Rename it (e.g. `my-theme`)
3. Edit `theme.json` with your theme's metadata
4. Modify templates and CSS as needed
5. Set `"theme": { "name": "my-theme" }` in config

> [!TIP]
> Theme static files are served at `/_themes/{name}/`, so you can reference them in templates.
