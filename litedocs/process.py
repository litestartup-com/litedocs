"""Process management utilities for LiteDocs daemon mode.

Handles PID file management, process spawning, and status queries
across macOS, Linux, and Windows.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

# Directory for PID/meta files — one per instance, keyed by port
_RUN_DIR = Path.cwd() / ".litedocs"


@dataclass
class InstanceInfo:
    """Metadata persisted alongside a running daemon."""

    pid: int
    port: int
    host: str
    base_path: str
    docs_dirs: list[str]
    log_file: str
    started_at: float  # time.time()


def _run_dir() -> Path:
    """Return (and ensure existence of) the run directory."""
    d = _RUN_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _meta_path(port: int) -> Path:
    """Path to the JSON meta file for a given port."""
    return _run_dir() / f"instance-{port}.json"


def _log_path(port: int) -> Path:
    """Path to the log file for a given port."""
    return _run_dir() / f"instance-{port}.log"


def save_instance(info: InstanceInfo) -> None:
    """Write instance metadata to disk."""
    _meta_path(info.port).write_text(
        json.dumps(asdict(info), indent=2), encoding="utf-8"
    )


def load_instance(port: int) -> InstanceInfo | None:
    """Load instance metadata for a port, or None if not found."""
    p = _meta_path(port)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return InstanceInfo(**data)
    except (json.JSONDecodeError, TypeError, KeyError):
        return None


def remove_instance(port: int) -> None:
    """Remove instance metadata file."""
    p = _meta_path(port)
    if p.exists():
        p.unlink()


def list_instances() -> list[InstanceInfo]:
    """Return all known instances (whether alive or not)."""
    d = _run_dir()
    instances: list[InstanceInfo] = []
    for f in sorted(d.glob("instance-*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            instances.append(InstanceInfo(**data))
        except (json.JSONDecodeError, TypeError, KeyError):
            continue
    return instances


def is_alive(pid: int) -> bool:
    """Check if a process with the given PID is still running."""
    if sys.platform == "win32":
        # Use tasklist to check process
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"],
                capture_output=True, text=True, timeout=5,
            )
            return str(pid) in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    else:
        # Unix: send signal 0 to check existence
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False


def kill_process(pid: int, timeout: float = 5.0) -> bool:
    """Terminate a process by PID. Returns True if successfully stopped.

    Sends SIGTERM (Unix) or taskkill (Windows), waits up to *timeout*
    seconds, then sends SIGKILL / force-kill if needed.
    """
    if not is_alive(pid):
        return True

    if sys.platform == "win32":
        # Graceful termination
        subprocess.run(
            ["taskkill", "/PID", str(pid)],
            capture_output=True, timeout=5,
        )
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not is_alive(pid):
                return True
            time.sleep(0.3)
        # Force kill
        subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True, timeout=5,
        )
    else:
        # Unix graceful
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return True
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not is_alive(pid):
                return True
            time.sleep(0.3)
        # Force kill
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            return True

    time.sleep(0.5)
    return not is_alive(pid)


def start_daemon(
    docs_dirs: list[Path],
    host: str = "127.0.0.1",
    port: int = 8000,
    base_path: str = "",
    reload: bool = False,
) -> InstanceInfo:
    """Spawn a LiteDocs server as a background process.

    Returns the :class:`InstanceInfo` for the new instance.
    Raises ``RuntimeError`` if an instance on the same port is already running.
    """
    existing = load_instance(port)
    if existing and is_alive(existing.pid):
        raise RuntimeError(
            f"An instance is already running on port {port} (PID {existing.pid}). "
            f"Stop it first with: litedocs stop --port {port}"
        )

    log_file = _log_path(port)

    # Build the command: run the same Python interpreter with litedocs serve
    cmd = [
        sys.executable, "-m", "litedocs.cli", "serve",
        "--host", host,
        "--port", str(port),
        "--no-reload" if not reload else "--reload",
    ]
    if base_path:
        cmd.extend(["--base-path", base_path])
    for d in docs_dirs:
        cmd.append(str(d))

    # Platform-specific background process creation
    log_fh = open(log_file, "a", encoding="utf-8")  # noqa: SIM115

    kwargs: dict = {
        "stdout": log_fh,
        "stderr": subprocess.STDOUT,
        "stdin": subprocess.DEVNULL,
    }

    if sys.platform == "win32":
        # CREATE_NEW_PROCESS_GROUP + DETACHED_PROCESS
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        kwargs["creationflags"] = CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
    else:
        # Unix: start new session so the child survives terminal close
        kwargs["start_new_session"] = True

    proc = subprocess.Popen(cmd, **kwargs)

    info = InstanceInfo(
        pid=proc.pid,
        port=port,
        host=host,
        base_path=base_path,
        docs_dirs=[str(d) for d in docs_dirs],
        log_file=str(log_file),
        started_at=time.time(),
    )
    save_instance(info)
    return info
