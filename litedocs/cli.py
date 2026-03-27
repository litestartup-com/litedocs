"""Command-line interface for LiteDocs."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import typer

from litedocs import __version__

# Project root: parent of the litedocs package directory
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Default demo directories shipped with the project
_DEFAULT_DOCS_DIRS = [
    _PROJECT_ROOT / "litedocs-docs",
    _PROJECT_ROOT / "tests" / "fixtures" / "sample-docs",
]

app = typer.Typer(
    name="litedocs",
    help="A lightweight, Markdown folder-based documentation rendering tool.",
    no_args_is_help=False,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"litedocs {__version__}")
        raise typer.Exit()


def _resolve_docs_dirs(docs_dirs: list[Path] | None) -> list[Path]:
    """Resolve documentation directories. Falls back to built-in demo dirs."""
    if not docs_dirs:
        resolved: list[Path] = [dd for dd in _DEFAULT_DOCS_DIRS if dd.is_dir()]
        if not resolved:
            typer.echo(
                "Error: No default docs directories found. Please specify a directory.",
                err=True,
            )
            raise typer.Exit(code=1)
        typer.echo("No docs directory specified — using built-in demo docs:")
        for dd in resolved:
            typer.echo(f"  • {dd}")
        typer.echo()
        return resolved

    resolved = []
    for docs_dir in docs_dirs:
        p = docs_dir.resolve()
        if not p.is_dir():
            typer.echo(f"Error: {docs_dir} is not a directory.", err=True)
            raise typer.Exit(code=1)
        resolved.append(p)
    return resolved


def _normalize_base_path(base_path: str) -> str:
    """Strip trailing slash, ensure leading slash if non-empty."""
    bp = base_path.strip().rstrip("/")
    if bp and not bp.startswith("/"):
        bp = "/" + bp
    return bp


def _scaffold(docs_paths: list[Path]) -> None:
    """Run auto-scaffolding (config, index, sidebar) for each docs directory."""
    from litedocs.config import load_config
    from litedocs.scaffold import ensure_config, ensure_index, ensure_sidebar

    for docs_path in docs_paths:
        ensure_config(docs_path)
        config = load_config(docs_path)
        ensure_index(docs_path, flat_mode=config.flat_mode)
        ensure_sidebar(docs_path, config.locales.available, flat_mode=config.flat_mode)


def _print_startup_info(docs_paths: list[Path], host: str, port: int, bp: str) -> None:
    """Print startup banner with docs info."""
    from litedocs.config import load_config

    typer.echo("Starting LiteDocs server...")
    for dp in docs_paths:
        cfg = load_config(dp)
        prefix = f"{bp}/{dp.name}/" if bp else f"/{dp.name}/"
        typer.echo(f"  Docs: {dp} -> {prefix}")
        if cfg.flat_mode:
            typer.echo(f"  ⚠  Non-standard directory detected: {dp.name}")
            typer.echo(f"     config.json and _sidebar.md were auto-generated.")
            typer.echo(
                f"     For full features (multi-language, nav tabs), see: "
                f"https://github.com/litestartup-com/litedocs#docs-directory-structure"
            )
    if bp:
        typer.echo(f"  Base: {bp}")
    typer.echo(f"  URL:  http://{host}:{port}{bp}")


def _format_uptime(seconds: float) -> str:
    """Format a duration in seconds to a human-readable string."""
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60}s"
    h = s // 3600
    m = (s % 3600) // 60
    return f"{h}h {m}m"


# ---------------------------------------------------------------------------
# CLI callback
# ---------------------------------------------------------------------------

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show version and exit.",
        callback=version_callback, is_eager=True,
    ),
) -> None:
    """LiteDocs - Lightweight documentation from Markdown folders."""


# ---------------------------------------------------------------------------
# serve (foreground)
# ---------------------------------------------------------------------------

@app.command()
def serve(
    docs_dirs: Optional[List[Path]] = typer.Argument(
        None,
        help="Path(s) to documentation root directories. Defaults to built-in demo docs.",
    ),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to."),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the server to."),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable hot reload on file changes."),
    base_path: str = typer.Option("", "--base-path", "-b", help="URL prefix for reverse proxy (e.g. /docs)."),
) -> None:
    """Start the documentation server in the foreground.

    Supports one or multiple documentation directories.
    If no directories are specified, serves the built-in demo docs
    (litedocs-docs + sample-docs) to showcase all features.

    Missing config.json and _sidebar.md are auto-generated on first run.

    Examples:
        litedocs serve                          # demo mode
        litedocs serve ./docs
        litedocs serve ./docs-a ./docs-b
        litedocs serve ./docs --base-path /docs
    """
    docs_paths = _resolve_docs_dirs(docs_dirs)
    bp = _normalize_base_path(base_path)
    _scaffold(docs_paths)
    _print_startup_info(docs_paths, host, port, bp)

    from litedocs.server import create_app, run_server

    app_instance = create_app(docs_paths, base_path=bp)
    run_server(app_instance, host=host, port=port, reload=reload, docs_paths=docs_paths)


# ---------------------------------------------------------------------------
# start (background daemon)
# ---------------------------------------------------------------------------

@app.command()
def start(
    docs_dirs: Optional[List[Path]] = typer.Argument(
        None,
        help="Path(s) to documentation root directories. Defaults to built-in demo docs.",
    ),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to."),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the server to."),
    reload: bool = typer.Option(False, "--reload/--no-reload", help="Enable hot reload on file changes."),
    base_path: str = typer.Option("", "--base-path", "-b", help="URL prefix for reverse proxy (e.g. /docs)."),
) -> None:
    """Start the documentation server as a background daemon.

    The server runs in the background. Use ``litedocs status`` to check
    running instances, ``litedocs stop`` to shut them down.

    Multiple instances on different ports are supported.

    Examples:
        litedocs start ./docs
        litedocs start ./docs --port 9000
        litedocs start                          # demo mode (background)
    """
    from litedocs.process import is_alive, load_instance, start_daemon

    docs_paths = _resolve_docs_dirs(docs_dirs)
    bp = _normalize_base_path(base_path)
    _scaffold(docs_paths)

    # Check for existing instance on this port
    existing = load_instance(port)
    if existing and is_alive(existing.pid):
        typer.echo(
            f"Error: An instance is already running on port {port} (PID {existing.pid}).\n"
            f"Stop it first:  litedocs stop --port {port}",
            err=True,
        )
        raise typer.Exit(code=1)

    info = start_daemon(
        docs_dirs=docs_paths,
        host=host,
        port=port,
        base_path=bp,
        reload=reload,
    )

    # Wait briefly and verify the process started
    time.sleep(1.0)
    if is_alive(info.pid):
        typer.echo(f"LiteDocs daemon started (PID {info.pid}).")
        typer.echo(f"  URL:  http://{host}:{port}{bp}")
        typer.echo(f"  Log:  {info.log_file}")
        typer.echo(f"  Stop: litedocs stop --port {port}")
    else:
        typer.echo(
            f"Error: Daemon process exited immediately. Check logs:\n  {info.log_file}",
            err=True,
        )
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# stop
# ---------------------------------------------------------------------------

@app.command()
def stop(
    port: int = typer.Option(8000, "--port", "-p", help="Port of the instance to stop."),
    all_instances: bool = typer.Option(False, "--all", "-a", help="Stop all running instances."),
) -> None:
    """Stop a running LiteDocs daemon.

    Examples:
        litedocs stop                   # stop instance on port 8000
        litedocs stop --port 9000
        litedocs stop --all             # stop every instance
    """
    from litedocs.process import (
        is_alive,
        kill_process,
        list_instances,
        load_instance,
        remove_instance,
    )

    if all_instances:
        instances = list_instances()
        if not instances:
            typer.echo("No LiteDocs instances found.")
            return
        for inst in instances:
            if is_alive(inst.pid):
                ok = kill_process(inst.pid)
                status = "stopped" if ok else "failed to stop"
                typer.echo(f"  Port {inst.port} (PID {inst.pid}): {status}")
            else:
                typer.echo(f"  Port {inst.port} (PID {inst.pid}): already dead")
            remove_instance(inst.port)
        return

    inst = load_instance(port)
    if not inst:
        typer.echo(f"No instance found on port {port}.")
        raise typer.Exit(code=1)

    if not is_alive(inst.pid):
        typer.echo(f"Instance on port {port} (PID {inst.pid}) is not running. Cleaning up.")
        remove_instance(port)
        return

    ok = kill_process(inst.pid)
    remove_instance(port)
    if ok:
        typer.echo(f"LiteDocs daemon on port {port} (PID {inst.pid}) stopped.")
    else:
        typer.echo(f"Error: Failed to stop PID {inst.pid}.", err=True)
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# restart
# ---------------------------------------------------------------------------

@app.command()
def restart(
    port: int = typer.Option(8000, "--port", "-p", help="Port of the instance to restart."),
) -> None:
    """Restart a running LiteDocs daemon (stop + start).

    Re-reads config.json and re-scans documents.

    Examples:
        litedocs restart
        litedocs restart --port 9000
    """
    from litedocs.process import is_alive, kill_process, load_instance, remove_instance, start_daemon

    inst = load_instance(port)
    if not inst:
        typer.echo(f"No instance found on port {port}.", err=True)
        raise typer.Exit(code=1)

    # Stop the existing process
    if is_alive(inst.pid):
        ok = kill_process(inst.pid)
        if not ok:
            typer.echo(f"Error: Failed to stop PID {inst.pid}.", err=True)
            raise typer.Exit(code=1)
        typer.echo(f"Stopped PID {inst.pid}.")
    remove_instance(port)

    # Rebuild from saved info
    docs_paths = [Path(d) for d in inst.docs_dirs]
    _scaffold(docs_paths)

    new_info = start_daemon(
        docs_dirs=docs_paths,
        host=inst.host,
        port=inst.port,
        base_path=inst.base_path,
        reload=False,
    )

    time.sleep(1.0)
    if is_alive(new_info.pid):
        typer.echo(f"LiteDocs daemon restarted (PID {new_info.pid}).")
        typer.echo(f"  URL:  http://{inst.host}:{inst.port}{inst.base_path}")
    else:
        typer.echo(
            f"Error: Daemon exited immediately after restart. Check logs:\n  {new_info.log_file}",
            err=True,
        )
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@app.command()
def status() -> None:
    """Show the status of all LiteDocs daemon instances.

    Examples:
        litedocs status
    """
    from litedocs.process import is_alive, list_instances, remove_instance

    instances = list_instances()
    if not instances:
        typer.echo("No LiteDocs instances found.")
        return

    now = time.time()
    typer.echo(f"{'PORT':<8} {'PID':<10} {'STATUS':<12} {'UPTIME':<12} {'URL'}")
    typer.echo("-" * 72)
    for inst in instances:
        alive = is_alive(inst.pid)
        state = typer.style("running", fg=typer.colors.GREEN) if alive else typer.style("dead", fg=typer.colors.RED)
        uptime = _format_uptime(now - inst.started_at) if alive else "-"
        bp = inst.base_path or ""
        url = f"http://{inst.host}:{inst.port}{bp}"
        typer.echo(f"{inst.port:<8} {inst.pid:<10} {state:<21} {uptime:<12} {url}")
        if not alive:
            remove_instance(inst.port)

    typer.echo()
    running = [i for i in instances if is_alive(i.pid)]
    typer.echo(f"{len(running)} running, {len(instances) - len(running)} dead (cleaned up).")


# ---------------------------------------------------------------------------
# logs
# ---------------------------------------------------------------------------

@app.command()
def logs(
    port: int = typer.Option(8000, "--port", "-p", help="Port of the instance to view logs for."),
    follow: bool = typer.Option(True, "--follow/--no-follow", "-f", help="Follow log output (tail -f)."),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show initially."),
) -> None:
    """View logs for a LiteDocs daemon instance.

    Examples:
        litedocs logs
        litedocs logs --port 9000
        litedocs logs --no-follow --lines 100
    """
    from litedocs.process import load_instance

    inst = load_instance(port)
    if not inst:
        typer.echo(f"No instance found on port {port}.", err=True)
        raise typer.Exit(code=1)

    log_path = Path(inst.log_file)
    if not log_path.exists():
        typer.echo(f"Log file not found: {log_path}", err=True)
        raise typer.Exit(code=1)

    # Show last N lines
    try:
        all_lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        typer.echo(f"Error reading log: {e}", err=True)
        raise typer.Exit(code=1)

    tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
    for line in tail:
        typer.echo(line)

    if not follow:
        return

    # Follow mode: poll for new content
    typer.echo(f"\n--- Following {log_path} (Ctrl+C to stop) ---\n")
    try:
        last_pos = log_path.stat().st_size
        while True:
            time.sleep(0.5)
            current_size = log_path.stat().st_size
            if current_size > last_pos:
                with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(last_pos)
                    new_data = f.read()
                    if new_data:
                        typer.echo(new_data, nl=False)
                    last_pos = f.tell()
            elif current_size < last_pos:
                # File was truncated (e.g. log rotation)
                last_pos = 0
    except KeyboardInterrupt:
        typer.echo("\nStopped following logs.")


if __name__ == "__main__":
    app()
