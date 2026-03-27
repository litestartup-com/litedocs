---
title: 编写内容
description: 如何为 LiteDocs 编写 Markdown 内容
order: 3
---

# 编写内容

LiteDocs 渲染标准 Markdown 并支持一些扩展。

## Frontmatter

每个页面顶部可以包含 YAML frontmatter：

```yaml
---
title: 我的页面标题
description: 简短描述，用于 SEO
order: 1
---
```

## 提示框

LiteDocs 支持五种提示框类型：

> [!NOTE]
> 这是一个笔记提示框，用于一般信息。

> [!TIP]
> 这是一个提示框，用于有用的建议。

> [!WARNING]
> 这是一个警告提示框，用于潜在问题。

## 代码块

支持语法高亮的代码块：

```python
def hello():
    print("Hello from LiteDocs!")
```

## 表格

| 功能     | 状态 |
|----------|------|
| Markdown | 完成 |
| 暗色模式 | 完成 |
| 搜索     | 测试 |
| 多文档   | 完成 |
