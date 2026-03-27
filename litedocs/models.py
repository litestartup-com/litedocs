"""Data models for LiteDocs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NavNode(BaseModel):
    """A single item in the top navigation bar."""

    label: str
    href: str | None = None
    is_external: bool = False
    badge: str | None = None
    is_active: bool = False


class SidebarNode(BaseModel):
    """A single item in the sidebar navigation tree."""

    label: str
    href: str | None = None
    is_group: bool = False
    is_external: bool = False
    badge: str | None = None
    method: str | None = None
    is_active: bool = False
    is_expanded: bool = False
    children: list[SidebarNode] = Field(default_factory=list)


class TocHeading(BaseModel):
    """A heading extracted from page content for the table of contents."""

    id: str
    text: str
    level: int


class NavLink(BaseModel):
    """A simple navigation link (used for prev/next page)."""

    label: str
    href: str


class PageContext(BaseModel):
    """Full context for rendering a documentation page."""

    slug: str
    locale: str
    product: str | None = None
    title: str = ""
    description: str = ""
    icon: str | None = None
    frontmatter: dict = Field(default_factory=dict)
    toc: list[TocHeading] = Field(default_factory=list)
    html_content: str = ""
    prev_page: NavLink | None = None
    next_page: NavLink | None = None


class LocaleContext(BaseModel):
    """Context for a specific locale, including nav and sidebar data."""

    locale: str
    nav_items: list[NavNode] = Field(default_factory=list)
    sidebar_tree: list[SidebarNode] = Field(default_factory=list)
    current_product: str | None = None
