---
title: 创建用户
description: 通过 API 创建新用户
---

# 创建用户

`POST /api/users`

创建一个新用户账户。

## 请求体

```json
{
  "name": "Charlie",
  "email": "charlie@example.com"
}
```

| 字段    | 类型   | 必填 | 描述     |
|---------|--------|------|----------|
| `name`  | string | 是   | 显示名称 |
| `email` | string | 是   | 邮箱地址 |

## 响应

```json
{
  "id": 3,
  "name": "Charlie",
  "email": "charlie@example.com",
  "created_at": "2026-01-15T10:30:00Z"
}
```

> [!NOTE]
> `created_at` 字段由服务器自动设置。
