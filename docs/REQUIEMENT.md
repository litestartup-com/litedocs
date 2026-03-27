想要实现的目标是一个**轻量、基于 Markdown 文件夹的静态文档渲染工具**，核心诉求是：

- 可以指定任意文件夹路径
- 文件夹内有 `config.json`（全局配置，SEO，主题色，追踪代码等）、多语言子目录（如 `en/`、`zh/`）
- 每个语言目录下有 `_nav.md`（顶部导航）、`_sidebar.md`（左侧菜单）
- 顶部导航（`_nav.md`）决定“文档主题/产品线”（类似多个独立文档集合）
- 切换语言 → 自动加载对应语言的 `_nav.md` 和 `_sidebar.md`
- 渲染风格尽量接近 Fumadocs（现代、干净、响应式、深色模式、TOC、搜索等）

下面给出一个**2026 年视角下比较务实、可维护、可逐步迭代**的设计方案（**不含代码，只讲结构、流程、权衡**）。

### 1. 整体架构分层（推荐）

```
项目类型建议：Python + FastAPI（异步API） + Jinja2 / HTMX（或纯前端） + Tailwind + DaisyUI / shadcn-tailwind 风格组件
```

分层建议（从外到内）：

| 层级           | 职责                               | 技术选型建议（2026主流轻量路线）                  | 是否必须 |
|----------------|------------------------------------|---------------------------------------------------|----------|
| 1. 启动层      | 读取命令行参数、指定目录           | typer / argparse / click                          | 是       |
| 2. 配置解析层  | 读取 config.json、全局规则         | pydantic v2                                       | 是       |
| 3. 内容扫描层  | 发现语言、主题、文件结构           | pathlib + 自定义 walker                           | 是       |
| 4. Markdown 处理层 | 解析 _nav.md / _sidebar.md / 普通 .md/.mdx | markdown-it-py + markdown-it-py插件（attrs、deflist、tasklists、footnote等） | 是       |
| 5. 导航树构建层 | 把 _nav.md / _sidebar.md 转成结构化数据 | 自定义树节点（标题、slug、层级、图标、折叠状态） | 是       |
| 6. 页面渲染层  | 组合 layout + sidebar + toc + content | Jinja2 + 宏 / HTMX partials / React-like组件思维 | 是       |
| 7. 静态资源层  | CSS / JS / 图标 / 图片             | Tailwind + daisyUI / shadcn-ui tailwind（推荐）   | 是       |
| 8. 服务层      | 提供 HTTP 服务 / 热重载 / 静态导出 | FastAPI + uvicorn + watchfiles（热重载）          | 推荐     |
| 9. 可选扩展    | 搜索、i18n切换动画、暗黑模式持久化 | lunr.js / minisearch（客户端） + localStorage     | 后期     |

### 2. 文件夹约定（最核心部分）

强烈建议采用**约定优于配置**，参考 Fumadocs root: true + meta 的思路，但更简单：

```
docs-project/                     ← 用户指定的根目录
├── config.json                   ← 全局配置（站点标题、默认语言、主题色、footer 等）
├── assets/                       ← 公共图片、favicon 等（可选）
├── en/                           ← 语言目录（语言代码必须是标准短码）
│   ├── _nav.md                   ← 顶部导航（决定“产品/主题”分组）
│   ├── _sidebar.md               ← 默认/全局侧边栏（可选，如果 nav 里每个主题都有独立侧边栏可不放）
│   ├── introduction.md
│   ├── product-a/
│   │   ├── _sidebar.md           ← 该主题专属侧边栏（优先级最高）
│   │   ├── index.md
│   │   └── getting-started.md
│   └── product-b/
│       ├── _sidebar.md
│       └── ...
└── zh/
    ├── _nav.md
    ├── _sidebar.md
    └── ...（结构与 en/ 类似或部分重叠）
```

**_nav.md** 和 **_sidebar.md** 的格式约定（使用 markdown 标题层级 + 列表）：

```markdown
- [Introduction](README.md)
- [Quickstart](quickstart.md)
- **Features Guide**
- [Mailbox](features/emails.md)
- **API Reference**
- [Introduction](api/README.md)
- AI Stack
  - <post>[Image to Text (OCR)](api/ai-stack-image-to-text.md)
- **LINKS**
- [![Twitter](assets/img/twitter.svg)@litestartup_com](http://x.com/litestartup_com)
- [![Sitemap](assets/img/link.png)Sitemap](/sitemap.xml)
```

支持的增强语法（通过 markdown-it 插件实现）：

- `[icon:rocket]`、`[badge:New]` 等属性（写在链接后面）
- `- [ ] Task list`
- `> [!NOTE]`  admonition 风格（类似 Fumadocs callout）

### 3. 核心数据模型（内存中）

```text
SiteConfig
  ├── title
  ├── default_locale
  ├── available_locales  ["en", "zh"]
  ├── primary_color
  └── ...

LocaleContext
  ├── current_locale     "en" / "zh"
  ├── nav_tree           List[NavNode]           ← 从 _nav.md 解析
  ├── current_product    "product-a" / null      ← 当前选中的顶级分组
  └── sidebar_tree       List[SidebarNode]       ← 根据当前 product 选择对应的 _sidebar.md

PageContext
  ├── slug               "product-a/getting-started"
  ├── locale
  ├── frontmatter        (title, description, icon...)
  ├── toc                List[Heading]
  └── html_content       已渲染的 HTML
```

### 4. 运行时主要流程（用户访问时）

1. 用户启动：`python ctl.py start -m mydocs /path/to/docs-project`
2. 程序扫描整个目录 → 构建语言 → 主题映射表（内存缓存）
3. 用户访问 `/` 或 `/zh/` → 读取对应语言的 `_nav.md` → 解析成顶部导航 tabs / dropdown
4. 用户点击顶部某个 Product（如 Product A）→ 
   - 查找 `en/product-a/_sidebar.md`（优先）
   - 找不到则 fallback 到 `en/_sidebar.md`
   - 渲染左侧菜单
5. 用户点击左侧菜单项 → 查找对应 .md 文件 → 渲染正文 + TOC
6. 切换语言（右上角下拉或链接）→ 
   - 替换 LocaleContext
   - 重新解析该语言的 _nav.md 和对应 _sidebar.md
   - 尽量保持当前 slug（如果存在对应翻译文件）
7. 404 处理 → 显示友好提示 + 语言切换器

### 5. 推荐的技术权衡与取舍（2026视角）

| 需求                   | 推荐方案                              | 为什么不选其他                                      | 实现难度 |
|------------------------|---------------------------------------|-----------------------------------------------------|----------|
| 样式最接近 Fumadocs    | Tailwind + daisyUI / shadcn-tailwind  | 组件丰富、暗黑模式开箱、与 Fumadocs 视觉最接近      | ★★☆      |
| Markdown 渲染          | markdown-it-py + 多插件               | 生态最好，支持 attrs、callout、task list 等         | ★★☆      |
| 热重载开发体验         | FastAPI + watchfiles + HTMX           | 改 md 文件秒刷新，比纯静态生成爽很多                | ★★★      |
| 纯静态导出             | 后期加 `mydocs build` 命令            | 先做 serve 模式，业务跑通后再考虑 SSG               | ★★★★     |
| 全文搜索               | 客户端 minisearch / lunr.js           | 先实现基本功能，索引所有 md 文件标题+内容           | ★★★★     |
| TOC / 滚动高亮         | 客户端 JS（ IntersectionObserver）    | 服务端生成 TOC，客户端处理 active 状态              | ★★☆      |
| 多语言 slug 一致性     | 同名文件优先，fallback 到 default lang | 最常见需求（如 /getting-started 在所有语言都存在）  | ★★★      |

### 6. 分阶段落地建议

阶段 1（MVP，1-2 周）
- 支持单语言
- 解析 _nav.md → 顶部 tabs
- 解析 _sidebar.md → 左侧菜单
- 渲染普通 .md 文件
- 基本 Fumadocs 风格 layout（Tailwind）

阶段 2
- 支持多语言切换
- 语言切换后刷新 nav + sidebar
- 支持 product-specific _sidebar.md

阶段 3
- 搜索
- Callout / Admonition / Mermaid 支持
- 暗黑模式 + 持久化
- 静态导出功能
