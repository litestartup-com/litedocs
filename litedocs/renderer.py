"""Jinja2 template rendering and context assembly for LiteDocs."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from litedocs.config import SiteConfig
from litedocs.models import LocaleContext, NavLink, NavNode, PageContext, SidebarNode

_THEMES_DIR = Path(__file__).parent / "themes"


def get_theme_dir(theme_name: str = "default") -> Path:
    """Return the directory path for a given theme name."""
    theme_dir = _THEMES_DIR / theme_name
    if not theme_dir.is_dir():
        raise FileNotFoundError(f"Theme '{theme_name}' not found at {theme_dir}")
    return theme_dir


def create_jinja_env(theme_name: str = "default") -> Environment:
    """Create and configure the Jinja2 environment for a specific theme."""
    theme_dir = get_theme_dir(theme_name)
    templates_dir = theme_dir / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def _mark_active_nav(nav_items: list[NavNode], current_path: str) -> list[NavNode]:
    """Return a copy of nav items with the active item marked.

    Uses longest-prefix-match so more specific nav items win over broader ones.
    For example, ``/doc/en/guide/install`` matches ``/doc/en/guide/`` over ``/doc/en/``.
    """
    current = current_path.rstrip("/")
    best_idx: int | None = None
    best_len = -1

    for i, item in enumerate(nav_items):
        if not item.href or item.is_external:
            continue
        item_path = item.href.rstrip("/")
        # Exact match is best
        if item_path == current:
            best_idx = i
            best_len = len(item_path) + 9999  # ensure exact wins
        # Prefix match (must be followed by / or be the full path)
        elif item_path and current.startswith(item_path + "/") and len(item_path) > best_len:
            best_idx = i
            best_len = len(item_path)

    result: list[NavNode] = []
    for i, item in enumerate(nav_items):
        result.append(item.model_copy(update={"is_active": i == best_idx}))

    return result


def _mark_active_sidebar(
    nodes: list[SidebarNode], current_path: str
) -> tuple[list[SidebarNode], bool]:
    """Return a copy of sidebar nodes with active item and expanded parents marked.

    Returns:
        Tuple of (updated nodes, whether any child was active).
    """
    result: list[SidebarNode] = []
    any_active = False
    current = current_path.rstrip("/")

    for node in nodes:
        updated_children, child_active = _mark_active_sidebar(node.children, current_path)

        is_active = False
        if node.href and not node.is_external:
            node_path = node.href.rstrip("/")
            is_active = node_path == current

        is_expanded = child_active or is_active

        if is_active or child_active:
            any_active = True

        result.append(
            node.model_copy(
                update={
                    "is_active": is_active,
                    "is_expanded": is_expanded,
                    "children": updated_children,
                }
            )
        )

    return result, any_active


def _get_prev_next(
    sidebar: list[SidebarNode], current_path: str
) -> tuple[NavLink | None, NavLink | None]:
    """Find prev/next pages from the sidebar link order."""
    flat: list[NavLink] = []
    _flatten_sidebar(sidebar, flat)

    current = current_path.rstrip("/")
    current_idx: int | None = None

    for i, link in enumerate(flat):
        if link.href.rstrip("/") == current:
            current_idx = i
            break

    if current_idx is None:
        return None, None

    prev_page = flat[current_idx - 1] if current_idx > 0 else None
    next_page = flat[current_idx + 1] if current_idx < len(flat) - 1 else None
    return prev_page, next_page


def _flatten_sidebar(nodes: list[SidebarNode], out: list[NavLink]) -> None:
    """Flatten sidebar tree into an ordered list of clickable links."""
    for node in nodes:
        if node.href and not node.is_external:
            out.append(NavLink(label=node.label, href=node.href))
        if node.children:
            _flatten_sidebar(node.children, out)


def build_render_context(
    config: SiteConfig,
    locale_ctx: LocaleContext,
    page: PageContext,
    current_path: str,
    available_locales: list[str],
) -> dict:
    """Assemble the full template rendering context.

    Args:
        config: Site configuration.
        locale_ctx: Locale-specific nav/sidebar data.
        page: Parsed page content.
        current_path: The current request URL path.
        available_locales: All available locale codes.

    Returns:
        Dictionary of template variables.
    """
    nav_items = _mark_active_nav(locale_ctx.nav_items, current_path)
    sidebar_tree, _ = _mark_active_sidebar(locale_ctx.sidebar_tree, current_path)
    prev_page, next_page = _get_prev_next(sidebar_tree, current_path)

    page = page.model_copy(update={"prev_page": prev_page, "next_page": next_page})

    return {
        "config": config,
        "locale": locale_ctx.locale,
        "available_locales": available_locales,
        "nav_items": nav_items,
        "sidebar": sidebar_tree,
        "page": page,
        "current_path": current_path,
    }
