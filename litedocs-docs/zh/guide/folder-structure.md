---
title: 目录结构
description: LiteDocs 如何组织文档文件
order: 2
---

# 目录结构

LiteDocs 使用目录约定代替复杂的配置文件。

## 布局

```
my-docs/
├── config.json           # 必需 - 站点配置
├── assets/               # 可选 - 图片、favicon 等
├── en/                   # 语言目录（ISO 639-1）
│   ├── _nav.md           # 顶部导航标签
│   ├── _sidebar.md       # 左侧边栏菜单
│   ├── index.md          # 首页
│   └── api/              # 产品/分区目录
│       ├── _sidebar.md   # 分区专属侧边栏
│       └── index.md
└── zh/                   # 其他语言
    ├── _nav.md
    └── ...
```

## 特殊文件

| 文件           | 范围     | 用途                   |
|----------------|----------|------------------------|
| `config.json`  | 全局     | 站点标题、语言、主题   |
| `_nav.md`      | 每语言   | 顶部导航栏             |
| `_sidebar.md`  | 每分区   | 左侧边栏菜单           |
| `index.md`     | 每目录   | 该路径的默认页面       |

> [!NOTE]
> 当目录中包含 `_sidebar.md` 文件时，该目录会被自动检测为独立分区。
