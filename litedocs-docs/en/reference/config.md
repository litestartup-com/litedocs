---
title: config.json Reference
description: Full configuration schema for LiteDocs
---

# config.json Reference

## site

| Field         | Type   | Default | Description            |
|---------------|--------|---------|------------------------|
| `title`       | string | —       | Site title (required)  |
| `description` | string | `""`    | Site description       |
| `url`         | string | `""`    | Production URL         |
| `favicon`     | string | `""`    | Favicon path           |
| `logo`        | string | `""`    | Logo image path        |

## locales

| Field       | Type     | Default | Description              |
|-------------|----------|---------|--------------------------|
| `default`   | string   | —       | Default locale (required)|
| `available` | string[] | —       | Available locales        |

## theme

| Field           | Type    | Default      | Description          |
|-----------------|---------|--------------|----------------------|
| `name`          | string  | `"default"`  | Theme package name   |
| `primary_color` | string  | `"#3b82f6"`  | Primary color (hex)  |
| `dark_mode`     | boolean | `true`       | Enable dark mode     |

## footer

| Field       | Type     | Default | Description              |
|-------------|----------|---------|--------------------------|
| `copyright` | string   | `""`    | Copyright text           |
| `links`     | array    | `[]`    | Footer link objects      |

Each link: `{ "label": "Text", "href": "https://..." }`
