---
title: Configuration
description: How to configure LiteDocs via config.json
order: 3
---

# Configuration

All configuration is in `config.json` at the root of your docs directory.

## Minimal Config

```json
{
  "site": {
    "title": "My Documentation"
  },
  "locales": {
    "default": "en",
    "available": ["en"]
  }
}
```

## Full Config

```json
{
  "site": {
    "title": "My Documentation",
    "description": "Product docs for My Company",
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
  "footer": {
    "copyright": "© 2026 My Company",
    "links": [
      { "label": "GitHub", "href": "https://github.com/..." }
    ]
  }
}
```

## Fields

| Field                 | Required | Default      | Description                |
|-----------------------|----------|--------------|----------------------------|
| `site.title`          | Yes      | —            | Site title                 |
| `site.description`    | No       | `""`         | SEO description            |
| `site.url`            | No       | `""`         | Production URL             |
| `site.favicon`        | No       | `""`         | Path to favicon            |
| `site.logo`           | No       | `""`         | Path to logo image         |
| `locales.default`     | Yes      | —            | Default locale code        |
| `locales.available`   | Yes      | —            | List of locale codes       |
| `theme.name`          | No       | `"default"`  | Active theme name          |
| `theme.primary_color` | No       | `"#3b82f6"`  | Primary brand color        |
| `theme.dark_mode`     | No       | `true`       | Enable dark mode toggle    |

> [!IMPORTANT]
> `site.title` and `locales` are the only required fields.
