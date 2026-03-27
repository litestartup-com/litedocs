---
title: 项目结构
description: LiteDocs 代码库布局和模块概述
order: 1
---

# 项目结构

```
litedocs/
├── litedocs/               # 主包
│   ├── __init__.py         # 版本号
│   ├── cli.py              # Typer CLI（serve 命令）
│   ├── server.py           # FastAPI 应用、路由、多文档注册
│   ├── config.py           # Pydantic 配置模型
│   ├── parser.py           # Markdown、导航、侧边栏解析
│   ├── scanner.py          # 文件系统扫描和页面解析
│   ├── renderer.py         # Jinja2 渲染和模板上下文
│   └── themes/
│       └── default/        # 内置主题
│           ├── theme.json
│           ├── templates/
│           └── static/
├── tests/                  # Pytest 测试套件
├── litedocs-docs/          # 官方手册（多文档示例）
├── docs/                   # 内部设计文档
└── docker-compose.yml
```

## 核心模块

| 模块         | 职责                           |
|--------------|--------------------------------|
| `cli.py`     | CLI 入口，参数解析             |
| `server.py`  | FastAPI 应用创建、路由、静态文件|
| `config.py`  | `config.json` 模式和验证       |
| `parser.py`  | Markdown 转 HTML、导航解析     |
| `scanner.py` | 文件系统扫描、页面解析         |
| `renderer.py`| Jinja2 上下文组装、active 标记 |

## 请求流程

1. 浏览器请求 `/{doc_slug}/{locale}/{path}`
2. `server.py` 路由到对应的 `DocsApp` 实例
3. `scanner.py` 解析 Markdown 文件
4. `parser.py` 转换 Markdown 为 HTML
5. `renderer.py` 组装模板上下文
6. Jinja2 渲染 HTML 响应
