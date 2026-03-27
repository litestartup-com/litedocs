---
title: Writing Content
description: How to write Markdown content for LiteDocs
order: 3
---

# Writing Content

LiteDocs renders standard Markdown with a few extensions.

## Frontmatter

Every page can include YAML frontmatter at the top:

```yaml
---
title: My Page Title
description: A short description for SEO
order: 1
---
```

| Field         | Required | Description                        |
|---------------|----------|------------------------------------|
| `title`       | Yes      | Page title shown in browser tab    |
| `description` | No       | Used for meta tags and search      |
| `order`       | No       | Sort order in auto-generated lists |

## Callouts

LiteDocs supports five callout types:

> [!NOTE]
> This is a note callout for general information.

> [!TIP]
> This is a tip callout for helpful suggestions.

> [!IMPORTANT]
> This is an important callout for critical details.

> [!WARNING]
> This is a warning callout for potential issues.

> [!CAUTION]
> This is a caution callout for dangerous actions.

## Code Blocks

Fenced code blocks with syntax highlighting:

```python
def hello():
    print("Hello from LiteDocs!")
```

```json
{
  "site": { "title": "My Docs" }
}
```

## Task Lists

- [x] Write documentation
- [x] Add code examples
- [ ] Publish to production

## Tables

| Feature       | Status |
|---------------|--------|
| Markdown      | Done   |
| Dark Mode     | Done   |
| Search        | Beta   |
| Multi-Doc     | Done   |
