"""Auto-scaffold missing config.json and _sidebar.md for documentation directories."""

from __future__ import annotations

import json
import re
from pathlib import Path

SPECIAL_FILES = {"_nav.md", "_sidebar.md"}

# Pattern for locale directory names: ISO 639-1 (en, zh) or BCP 47 (pt-BR, zh-CN)
_LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")


def ensure_config(docs_path: Path) -> bool:
    """Create a default config.json if it does not exist.

    When the directory has no locale subdirectories (non-standard directory),
    the generated config sets ``flat_mode: true`` and ``locales.available: ["_flat"]``.
    The title is derived from the directory name.

    Returns:
        True if the config was auto-generated (flat or standard),
        False if it already existed.
    """
    config_file = docs_path / "config.json"
    if config_file.exists():
        return False

    title = docs_path.name.replace("-", " ").replace("_", " ").title()
    locales = _detect_locales(docs_path)
    is_flat = locales == ["_flat"]

    config: dict = {
        "site": {
            "title": title,
            "description": "",
        },
        "locales": {
            "default": locales[0],
            "available": locales,
        },
    }
    if is_flat:
        config["flat_mode"] = True

    config_file.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return True


def _detect_locales(docs_path: Path) -> list[str]:
    """Detect locale directories or return flat-mode locale.

    A subdirectory is considered a locale directory if its name matches
    an ISO 639-1 code (``en``, ``zh``) or BCP 47 tag (``pt-BR``, ``zh-CN``)
    and it contains at least one ``.md`` file.

    If no locale directories are found, the docs root itself is treated
    as a flat (single-locale) directory with locale code ``"_flat"``.
    """
    candidates: list[str] = []
    for item in sorted(docs_path.iterdir()):
        if (
            item.is_dir()
            and _LOCALE_RE.match(item.name)
            and _dir_has_md(item)
        ):
            candidates.append(item.name)

    if candidates:
        return candidates

    # No locale dirs found — flat mode
    return ["_flat"]


def _dir_has_md(directory: Path) -> bool:
    """Check if a directory contains any .md files (recursively)."""
    for item in directory.rglob("*.md"):
        if item.is_file() and item.name not in SPECIAL_FILES and not item.name.startswith("_"):
            return True
    return False


def ensure_index(docs_path: Path, flat_mode: bool = False) -> None:
    """Create a minimal index.md if no index/README exists.

    In flat mode the index lives at the docs root; in standard mode each
    locale directory is checked (but this function currently only handles
    flat mode – standard dirs are expected to have their own index).
    """
    if not flat_mode:
        return

    for name in ("index.md", "README.md", "readme.md", "INDEX.md"):
        if (docs_path / name).exists():
            return

    title = docs_path.name.replace("-", " ").replace("_", " ").title()
    (docs_path / "index.md").write_text(
        f"# {title}\n\nWelcome to {title}.\n",
        encoding="utf-8",
    )


def ensure_sidebar(docs_path: Path, available_locales: list[str], flat_mode: bool = False) -> None:
    """Create a default _sidebar.md if missing.

    In flat mode, the sidebar is generated at the docs root (``docs_path/_sidebar.md``).
    In standard mode, a sidebar is generated in each locale subdirectory.
    """
    if flat_mode:
        sidebar_file = docs_path / "_sidebar.md"
        if sidebar_file.exists():
            return
        entries = _scan_for_sidebar(docs_path)
        if entries:
            sidebar_file.write_text(
                "\n".join(entries) + "\n", encoding="utf-8"
            )
        return

    # Standard mode: one sidebar per locale dir
    for locale_code in available_locales:
        locale_dir = docs_path / locale_code
        if not locale_dir.is_dir():
            continue

        sidebar_file = locale_dir / "_sidebar.md"
        if sidebar_file.exists():
            continue

        entries = _scan_for_sidebar(locale_dir)
        if not entries:
            continue

        sidebar_file.write_text(
            "\n".join(entries) + "\n", encoding="utf-8"
        )


def _scan_for_sidebar(directory: Path, prefix: str = "") -> list[str]:
    """Recursively scan a directory and generate sidebar markdown entries.

    Returns a list of markdown lines like:
        - [Getting Started](getting-started.md)
        - **Guide**
          - [Installation](guide/installation.md)
    """
    entries: list[str] = []

    # Collect files and dirs separately, sorted
    files: list[Path] = []
    dirs: list[Path] = []

    for item in sorted(directory.iterdir()):
        if item.name.startswith(".") or item.name.startswith("_"):
            continue
        if item.is_file() and item.suffix == ".md":
            files.append(item)
        elif item.is_dir() and item.name != "assets":
            dirs.append(item)

    # Add files first (index.md and README.md at top)
    index_files = [f for f in files if f.stem.lower() in ("index", "readme")]
    other_files = [f for f in files if f.stem.lower() not in ("index", "readme")]

    for f in index_files:
        label = _file_to_label(f, is_index=True, dir_name=directory.name if prefix else "")
        rel_path = f"{prefix}{f.name}" if prefix else f.name
        entries.append(f"- [{label}]({rel_path})")

    for f in other_files:
        label = _file_to_label(f)
        rel_path = f"{prefix}{f.name}" if prefix else f.name
        entries.append(f"- [{label}]({rel_path})")

    # Add directories as groups
    for d in dirs:
        group_label = d.name.replace("-", " ").replace("_", " ").title()
        sub_prefix = f"{prefix}{d.name}/"
        sub_entries = _scan_for_sidebar(d, sub_prefix)
        if sub_entries:
            entries.append(f"- **{group_label}**")
            for sub in sub_entries:
                entries.append(f"  {sub}")

    return entries


def _file_to_label(path: Path, is_index: bool = False, dir_name: str = "") -> str:
    """Convert a filename to a human-readable label."""
    if is_index and dir_name:
        return dir_name.replace("-", " ").replace("_", " ").title()
    if is_index:
        return "Home"
    return path.stem.replace("-", " ").replace("_", " ").title()
