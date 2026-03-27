---
title: 快速开始
description: 2 分钟搭建你的第一个 LiteDocs 站点
order: 1
---

# 快速开始

## 1. 安装

```bash
pip install litedocs
```

## 2. 创建文档目录

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
  "site": { "title": "我的文档" },
  "locales": { "default": "zh", "available": ["zh"] }
}
```

## 3. 启动服务器

```bash
litedocs serve ./my-docs
```

在浏览器打开 `http://localhost:8000`。

> [!TIP]
> 使用 `--port 3000` 可以更改端口。使用 `--no-reload` 可以禁用文件监听。
