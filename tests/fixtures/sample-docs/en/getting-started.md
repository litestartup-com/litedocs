---
title: Getting Started
description: Learn how to set up and use LiteDocs
---

# Getting Started

This guide walks you through setting up your first LiteDocs site.

## Installation

Install LiteDocs via pip:

```bash
pip install litedocs
```

## Create Your Docs Folder

Create a new directory with the following structure:

```
my-docs/
├── config.json
└── en/
    ├── _nav.md
    ├── _sidebar.md
    └── index.md
```

## Start the Server

Run the development server:

```bash
litedocs serve ./my-docs
```

Visit `http://localhost:8000` to see your documentation.

> [!TIP]
> Use `--port 3000` to change the port number.
