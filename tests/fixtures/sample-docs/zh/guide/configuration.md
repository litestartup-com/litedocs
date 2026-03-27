---
title: 配置
description: 如何配置 LiteDocs
order: 2
---

# 配置

LiteDocs 通过文档根目录下的 `config.json` 文件进行配置。

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

## 主题配置

```json
{
  "theme": {
    "name": "default",
    "primary_color": "#3b82f6",
    "dark_mode": true
  }
}
```
