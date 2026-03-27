"""File watcher for hot reload in LiteDocs."""

from __future__ import annotations

import threading
from pathlib import Path

from fastapi import FastAPI


def start_watcher(app: FastAPI, docs_path: Path) -> None:
    """Start a background file watcher that invalidates caches on changes.

    Watches a docs directory for .md, .json, and asset file changes.
    On any change, clears the matching DocsApp caches so the next request
    picks up the updated content.

    Args:
        app: The FastAPI application (with doc_registry on state).
        docs_path: Path to the documentation root directory.
    """
    slug = docs_path.name

    def _watch() -> None:
        from watchfiles import watch, Change

        for changes in watch(str(docs_path)):
            doc_registry = app.state.doc_registry
            docs_app = doc_registry.get(slug)
            if docs_app is None:
                continue

            needs_full_reload = False

            for change_type, change_path in changes:
                p = Path(change_path)
                if p.name == "config.json":
                    needs_full_reload = True
                    break

            if needs_full_reload:
                try:
                    docs_app.reload()
                    print(f"[LiteDocs] Full reload ({slug}): config.json changed")
                except Exception as exc:
                    print(f"[LiteDocs] Reload error ({slug}): {exc}")
            else:
                docs_app.invalidate_caches()
                changed_files = [Path(p).name for _, p in changes]
                print(f"[LiteDocs] Cache invalidated ({slug}): {', '.join(changed_files)}")

    thread = threading.Thread(target=_watch, daemon=True, name=f"watcher-{slug}")
    thread.start()
