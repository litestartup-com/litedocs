---
title: Create User
description: Create a new user via the API
---

# Create User

`POST /api/users`

Creates a new user account.

## Request Body

```json
{
  "name": "Charlie",
  "email": "charlie@example.com"
}
```

| Field   | Type   | Required | Description       |
|---------|--------|----------|-------------------|
| `name`  | string | Yes      | Display name      |
| `email` | string | Yes      | Email address     |

## Response

```json
{
  "id": 3,
  "name": "Charlie",
  "email": "charlie@example.com",
  "created_at": "2026-01-15T10:30:00Z"
}
```

> [!NOTE]
> The `created_at` field is automatically set by the server.
