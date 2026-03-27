---
title: 测试
description: 如何运行和编写 LiteDocs 测试
order: 4
---

# 测试

## 运行测试

```bash
pytest tests/ -v
```

## 测试结构

```
tests/
├── conftest.py          # 共享 fixtures
├── fixtures/
│   └── sample-docs/     # 测试文档目录
├── test_config.py       # 配置模型测试
├── test_parser.py       # 解析器测试
├── test_renderer.py     # 渲染器测试
├── test_scanner.py      # 文件扫描器测试
└── test_server.py       # HTTP 端点集成测试
```

## 编写测试

- 使用 `sample_docs_path` fixture 进行文件系统测试
- 使用 `client` fixture（FastAPI `TestClient`）进行 HTTP 测试
- 测试中英文两种语言
- 测试完整页面和 HTMX 局部响应

## 覆盖率

```bash
pytest tests/ -v --cov=litedocs --cov-report=term-missing
```
