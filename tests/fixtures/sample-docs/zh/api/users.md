---
title: 获取用户列表
description: 获取所有用户列表
---

# 获取用户列表

`GET /api/users`

返回分页的用户列表。

## 响应

```json
{
  "users": [
    { "id": 1, "name": "Alice" },
    { "id": 2, "name": "Bob" }
  ],
  "total": 2
}
```
