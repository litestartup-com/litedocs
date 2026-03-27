---
title: 多文档
description: 如何同时运行多个文档目录
order: 5
---

# 多文档支持

LiteDocs 可以同时运行多个文档目录。

## 用法

```bash
# 单个目录
litedocs serve ./my-docs

# 多个目录
litedocs serve ./docs-api ./docs-guide
```

## URL 格式

所有页面遵循以下格式：

```
/{doc_slug}/{locale}/{path}
```

- **doc_slug** — 目录名称（如 `docs-api`）
- **locale** — 语言代码（如 `en`、`zh`）
- **path** — 语言目录内的页面路径

## 根路径行为

| 模式     | 根 URL（`/`）行为                |
|----------|----------------------------------|
| 单文档   | 重定向到 `/{slug}/{locale}/`     |
| 多文档   | 重定向到 `/_docs` 列表页         |

## 文档切换器

当运行多个文档时，Header 会自动显示一个下拉菜单用于切换文档。

> [!NOTE]
> 每个文档目录必须包含独立的 `config.json`。
