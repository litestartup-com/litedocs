---
title: 配置
description: 如何通过 config.json 配置 LiteDocs
order: 3
---

# 配置

所有配置都在文档根目录的 `config.json` 文件中。

## 最小配置

```json
{
  "site": {
    "title": "我的文档"
  },
  "locales": {
    "default": "zh",
    "available": ["zh"]
  }
}
```

## 完整配置

```json
{
  "site": {
    "title": "我的文档",
    "description": "产品文档",
    "url": "https://docs.example.com"
  },
  "locales": {
    "default": "zh",
    "available": ["zh", "en"]
  },
  "theme": {
    "name": "default",
    "primary_color": "#3b82f6",
    "dark_mode": true
  },
  "footer": {
    "copyright": "© 2026 我的公司",
    "links": [
      { "label": "GitHub", "href": "https://github.com/..." }
    ]
  }
}
```

> [!IMPORTANT]
> `site.title` 和 `locales` 是唯一的必填字段。
