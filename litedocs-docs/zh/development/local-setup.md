---
title: 本地搭建
description: 搭建 LiteDocs 本地开发环境
order: 3
---

# 本地搭建

## 前置条件

- Python 3.11+
- pip

## 开发模式安装

```bash
git clone https://github.com/litestartup-com/litedocs.git
cd litedocs
pip install -e ".[dev]"
```

## 运行开发服务器

```bash
python -c "from litedocs.cli import app; app()" serve tests/fixtures/sample-docs

# 多文档模式
python -c "from litedocs.cli import app; app()" serve tests/fixtures/sample-docs litedocs-docs
```

## 使用 Docker

```bash
docker compose up
```

服务器启动在 `http://localhost:8000`，支持热重载。
