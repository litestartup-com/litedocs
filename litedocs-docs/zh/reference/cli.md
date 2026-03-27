---
title: CLI 命令
description: LiteDocs 命令行接口参考
---

# CLI 命令

## litedocs serve

启动文档服务器。

```bash
litedocs serve [选项] 文档目录...
```

### 参数

| 参数       | 描述                       |
|------------|----------------------------|
| `文档目录` | 一个或多个文档目录路径     |

### 选项

| 选项                   | 默认值        | 描述           |
|------------------------|---------------|----------------|
| `--host`, `-h`         | `127.0.0.1`  | 绑定主机       |
| `--port`, `-p`         | `8000`        | 绑定端口       |
| `--reload/--no-reload` | `--reload`    | 启用热重载     |

### 示例

```bash
# 基本用法
litedocs serve ./docs

# 自定义主机和端口
litedocs serve ./docs --host 0.0.0.0 --port 3000

# 多文档目录
litedocs serve ./docs-api ./docs-guide
```

## litedocs --version

显示当前版本。

```bash
litedocs --version
```
