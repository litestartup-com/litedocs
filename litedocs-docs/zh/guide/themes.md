---
title: 主题
description: 如何在 LiteDocs 中使用和创建主题
order: 4
---

# 主题

LiteDocs 支持可切换的主题。每个主题都是一个独立的目录，包含模板和静态资源。

## 选择主题

在 `config.json` 中设置 `theme.name`：

```json
{
  "theme": {
    "name": "default",
    "primary_color": "#8b5cf6"
  }
}
```

## 主题结构

```
litedocs/themes/default/
├── theme.json
├── templates/
│   ├── base.html
│   ├── page.html
│   └── partials/
│       ├── header.html
│       ├── sidebar.html
│       └── ...
└── static/
    ├── css/style.css
    └── js/app.js
```

## 创建自定义主题

1. 复制 `default` 主题目录
2. 重命名（如 `my-theme`）
3. 编辑 `theme.json` 设置主题元数据
4. 修改模板和 CSS
5. 在配置中设置 `"theme": { "name": "my-theme" }`

> [!TIP]
> 主题静态文件在 `/_themes/{name}/` 路径下提供服务。
