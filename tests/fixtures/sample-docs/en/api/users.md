---
title: List Users
description: Retrieve a list of all users
---

# List Users

`GET /api/users`

Returns a paginated list of users.

## Response

```json
{
  "users": [
    { "id": 1, "name": "Alice" },
    { "id": 2, "name": "Bob" }
  ],
  "total": 2
}
```
