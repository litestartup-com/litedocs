---
title: config.json 参考
description: LiteDocs 完整配置模式
---

# config.json 参考

## site

| 字段          | 类型   | 默认值 | 描述               |
|---------------|--------|--------|--------------------|
| `title`       | string | —      | 站点标题（必填）   |
| `description` | string | `""`   | 站点描述           |
| `url`         | string | `""`   | 生产环境 URL       |
| `favicon`     | string | `""`   | Favicon 路径       |
| `logo`        | string | `""`   | Logo 图片路径      |

## locales

| 字段        | 类型     | 默认值 | 描述                 |
|-------------|----------|--------|----------------------|
| `default`   | string   | —      | 默认语言代码（必填） |
| `available` | string[] | —      | 可用语言列表         |

## theme

| 字段            | 类型    | 默认值       | 描述           |
|-----------------|---------|--------------|----------------|
| `name`          | string  | `"default"`  | 主题包名称     |
| `primary_color` | string  | `"#3b82f6"`  | 主色调（hex）  |
| `dark_mode`     | boolean | `true`       | 启用暗色模式   |

## footer

| 字段        | 类型   | 默认值 | 描述           |
|-------------|--------|--------|----------------|
| `copyright` | string | `""`   | 版权文字       |
| `links`     | array  | `[]`   | 底部链接数组   |

每个链接格式：`{ "label": "文本", "href": "https://..." }`
