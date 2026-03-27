---
title: 快速开始
description: 学习如何设置和使用 LiteDocs
---

# 快速开始

本指南将带你完成第一个 LiteDocs 站点的搭建。

## 安装

通过 pip 安装 LiteDocs：

```bash
pip install litedocs
```

## 创建文档目录

创建以下目录结构：

```
my-docs/
├── config.json
└── en/
    ├── _nav.md
    ├── _sidebar.md
    └── index.md
```

## 启动服务器

运行开发服务器：

```bash
litedocs serve ./my-docs
```

访问 `http://localhost:8000` 查看你的文档。

> [!TIP]
> 使用 `--port 3000` 可以更改端口号。
