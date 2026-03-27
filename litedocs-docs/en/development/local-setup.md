---
title: Local Setup
description: Set up a local development environment for LiteDocs
order: 3
---

# Local Setup

## Prerequisites

- Python 3.11+
- pip

## Install in Development Mode

```bash
git clone https://github.com/example/litedocs.git
cd litedocs
pip install -e ".[dev]"
```

## Run the Dev Server

```bash
# Using sample docs fixture
python -c "from litedocs.cli import app; app()" serve tests/fixtures/sample-docs

# Multi-doc mode
python -c "from litedocs.cli import app; app()" serve tests/fixtures/sample-docs litedocs-docs
```

## Using Docker

```bash
docker compose up
```

This starts the server at `http://localhost:8000` with hot reload enabled.
