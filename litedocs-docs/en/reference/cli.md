---
title: CLI Commands
description: LiteDocs command-line interface reference
---

# CLI Commands

## litedocs serve

Start the documentation server.

```bash
litedocs serve [OPTIONS] DOCS_DIRS...
```

### Arguments

| Argument    | Description                          |
|-------------|--------------------------------------|
| `DOCS_DIRS` | One or more documentation directories|

### Options

| Option              | Default       | Description              |
|---------------------|---------------|--------------------------|
| `--host`, `-h`      | `127.0.0.1`  | Host to bind to          |
| `--port`, `-p`      | `8000`        | Port to bind to          |
| `--reload/--no-reload` | `--reload` | Enable hot reload        |

### Examples

```bash
# Basic usage
litedocs serve ./docs

# Custom host and port
litedocs serve ./docs --host 0.0.0.0 --port 3000

# Multiple doc directories
litedocs serve ./docs-api ./docs-guide

# Disable hot reload
litedocs serve ./docs --no-reload
```

## litedocs --version

Show the current version.

```bash
litedocs --version
```
