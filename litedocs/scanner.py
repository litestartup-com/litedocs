"""Directory scanning and content discovery for LiteDocs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


SPECIAL_FILES = {"_nav.md", "_sidebar.md"}


@dataclass
class PageInfo:
    """Metadata for a single Markdown content page."""

    file_path: Path
    locale: str
    product: str | None
    slug: str
    relative_path: str


@dataclass
class ProductInfo:
    """A product (sub-section) within a locale directory."""

    name: str
    dir_path: Path
    has_sidebar: bool
    pages: list[PageInfo] = field(default_factory=list)


@dataclass
class LocaleInfo:
    """A locale directory and its contents."""

    code: str
    dir_path: Path
    has_nav: bool
    has_sidebar: bool
    products: dict[str, ProductInfo] = field(default_factory=dict)
    pages: list[PageInfo] = field(default_factory=list)


@dataclass
class SiteStructure:
    """Complete scanned structure of the documentation site."""

    docs_path: Path
    locales: dict[str, LocaleInfo] = field(default_factory=dict)
    has_assets: bool = False


def _is_content_file(path: Path) -> bool:
    """Check if a path is a renderable Markdown content file."""
    return (
        path.is_file()
        and path.suffix == ".md"
        and path.name not in SPECIAL_FILES
        and not path.name.startswith("_")
    )


def _make_slug(file_path: Path, base_dir: Path) -> str:
    """Generate a URL slug from a file path relative to a base directory.

    Examples:
        index.md -> ""
        README.md -> ""
        getting-started.md -> "getting-started"
        guide/index.md -> "guide"
        guide/installation.md -> "guide/installation"
    """
    rel = file_path.relative_to(base_dir)
    parts = list(rel.parts)

    # Remove .md extension from last part
    parts[-1] = parts[-1].removesuffix(".md")

    # index and README map to directory root
    if parts[-1].lower() in ("index", "readme"):
        parts = parts[:-1]

    return "/".join(parts)


def _scan_pages(
    directory: Path,
    locale: str,
    locale_dir: Path,
    product: str | None = None,
) -> list[PageInfo]:
    """Scan a directory for Markdown content pages (non-recursive for product level)."""
    pages: list[PageInfo] = []

    for item in sorted(directory.iterdir()):
        if _is_content_file(item):
            slug = _make_slug(item, locale_dir)
            relative_path = str(item.relative_to(locale_dir)).replace("\\", "/")
            pages.append(
                PageInfo(
                    file_path=item,
                    locale=locale,
                    product=product,
                    slug=slug,
                    relative_path=relative_path,
                )
            )
        elif item.is_dir() and not item.name.startswith(".") and product is None:
            # Recurse into subdirectories only from locale level (not nested products)
            sub_pages = _scan_pages(item, locale, locale_dir, product=None)
            pages.extend(sub_pages)

    return pages


def scan_docs(docs_path: Path, available_locales: list[str]) -> SiteStructure:
    """Scan the documentation root directory and build a SiteStructure.

    Args:
        docs_path: Path to the documentation root directory.
        available_locales: List of locale codes to look for (from config.json).

    Returns:
        A SiteStructure containing all discovered locales, products, and pages.
    """
    structure = SiteStructure(docs_path=docs_path)
    structure.has_assets = (docs_path / "assets").is_dir()

    for locale_code in available_locales:
        # Flat mode: use docs_path itself as the locale directory
        if locale_code == "_flat":
            locale_dir = docs_path
        else:
            locale_dir = docs_path / locale_code
        if not locale_dir.is_dir():
            continue

        locale_info = LocaleInfo(
            code=locale_code,
            dir_path=locale_dir,
            has_nav=(locale_dir / "_nav.md").is_file(),
            has_sidebar=(locale_dir / "_sidebar.md").is_file(),
        )

        # Directories to skip when scanning (especially relevant in flat mode
        # where locale_dir == docs_path and non-content dirs are present).
        _skip_dirs = {"assets", "__pycache__", "node_modules", ".git"}

        # Discover products and pages
        for item in sorted(locale_dir.iterdir()):
            if item.is_dir() and not item.name.startswith(".") and not item.name.startswith("_") and item.name not in _skip_dirs:
                product_sidebar = (item / "_sidebar.md").is_file()
                product = ProductInfo(
                    name=item.name,
                    dir_path=item,
                    has_sidebar=product_sidebar,
                )

                # Scan pages within this product directory (recursively)
                product.pages = _scan_product_pages(item, locale_code, locale_dir, item.name)

                locale_info.products[item.name] = product

            elif _is_content_file(item):
                slug = _make_slug(item, locale_dir)
                relative_path = str(item.relative_to(locale_dir)).replace("\\", "/")
                locale_info.pages.append(
                    PageInfo(
                        file_path=item,
                        locale=locale_code,
                        product=None,
                        slug=slug,
                        relative_path=relative_path,
                    )
                )

        structure.locales[locale_code] = locale_info

    return structure


def _scan_product_pages(
    directory: Path,
    locale: str,
    locale_dir: Path,
    product: str,
) -> list[PageInfo]:
    """Recursively scan a product directory for Markdown content pages."""
    pages: list[PageInfo] = []

    for item in sorted(directory.iterdir()):
        if _is_content_file(item):
            slug = _make_slug(item, locale_dir)
            relative_path = str(item.relative_to(locale_dir)).replace("\\", "/")
            pages.append(
                PageInfo(
                    file_path=item,
                    locale=locale,
                    product=product,
                    slug=slug,
                    relative_path=relative_path,
                )
            )
        elif item.is_dir() and not item.name.startswith("."):
            pages.extend(_scan_product_pages(item, locale, locale_dir, product))

    return pages


def resolve_page(
    structure: SiteStructure,
    locale: str,
    path: str,
) -> PageInfo | None:
    """Resolve a URL path to a PageInfo.

    Tries in order:
        1. {locale}/{path}.md
        2. {locale}/{path}/index.md
        3. {locale}/{path}/README.md

    Args:
        structure: The scanned site structure.
        locale: The locale code.
        path: The URL path after the locale prefix (e.g. "getting-started").

    Returns:
        PageInfo if found, None otherwise.
    """
    locale_info = structure.locales.get(locale)
    if locale_info is None:
        return None

    locale_dir = locale_info.dir_path

    # Normalize empty path
    if not path or path == "/":
        path = ""

    path = path.strip("/")

    # Try exact file: {path}.md
    if path:
        candidate = locale_dir / f"{path}.md"
        if candidate.is_file() and _is_content_file(candidate):
            slug = _make_slug(candidate, locale_dir)
            return _page_info_from_file(candidate, locale, locale_dir, slug)

    # Try directory index: {path}/index.md
    index_path = path if path else ""
    candidate = locale_dir / index_path / "index.md" if index_path else locale_dir / "index.md"
    if candidate.is_file() and _is_content_file(candidate):
        slug = _make_slug(candidate, locale_dir)
        return _page_info_from_file(candidate, locale, locale_dir, slug)

    # Try directory README: {path}/README.md
    if index_path:
        candidate = locale_dir / index_path / "README.md"
    else:
        candidate = locale_dir / "README.md"
    if candidate.is_file() and _is_content_file(candidate):
        slug = _make_slug(candidate, locale_dir)
        return _page_info_from_file(candidate, locale, locale_dir, slug)

    return None


def _page_info_from_file(
    file_path: Path,
    locale: str,
    locale_dir: Path,
    slug: str,
) -> PageInfo:
    """Create a PageInfo from a resolved file path."""
    relative_path = str(file_path.relative_to(locale_dir)).replace("\\", "/")

    # Determine product from path
    parts = slug.split("/") if slug else []
    locale_info_dir = locale_dir
    product: str | None = None
    if parts:
        potential_product_dir = locale_info_dir / parts[0]
        if potential_product_dir.is_dir() and (potential_product_dir / "_sidebar.md").is_file():
            product = parts[0]

    return PageInfo(
        file_path=file_path,
        locale=locale,
        product=product,
        slug=slug,
        relative_path=relative_path,
    )
