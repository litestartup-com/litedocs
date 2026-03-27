---
title: 主题系统
description: LiteDocs 主题架构内部工作原理
order: 2
---

# 主题系统

## 目录结构

每个主题位于 `litedocs/themes/{name}/` 下：

```
litedocs/themes/default/
├── theme.json
├── templates/
│   ├── base.html
│   ├── page.html
│   ├── macros/
│   │   └── sidebar_node.html
│   ├── partials/
│   │   ├── header.html
│   │   ├── sidebar.html
│   │   └── ...
│   └── errors/
│       └── 404.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## 静态资源服务

主题静态文件挂载在 `/_themes/{name}/`。模板中引用方式：

```html
<link rel="stylesheet" href="/_themes/default/css/style.css">
```

## 模板上下文

渲染器为所有模板提供以下变量：

| 变量               | 类型        | 描述                 |
|--------------------|-------------|----------------------|
| `page`             | `Page`      | 当前页面数据         |
| `config`           | `SiteConfig`| 站点配置             |
| `nav_items`        | `list`      | 顶部导航项           |
| `sidebar`          | `list`      | 侧边栏节点           |
| `locale`           | `str`       | 当前语言代码         |
| `doc_slug`         | `str`       | 当前文档目录名       |
| `doc_list`         | `list`      | 所有注册的文档       |
