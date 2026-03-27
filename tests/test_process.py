"""Tests for litedocs.process — PID file management and process utilities."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from litedocs.process import (
    InstanceInfo,
    _log_path,
    _meta_path,
    is_alive,
    kill_process,
    list_instances,
    load_instance,
    remove_instance,
    save_instance,
)


@pytest.fixture(autouse=True)
def _isolate_run_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect the .litedocs run directory to a temp location."""
    monkeypatch.setattr("litedocs.process._RUN_DIR", tmp_path / ".litedocs")


def _make_info(port: int = 8000, pid: int = 99999, **kw) -> InstanceInfo:
    defaults = dict(
        pid=pid,
        port=port,
        host="127.0.0.1",
        base_path="",
        docs_dirs=["/tmp/docs"],
        log_file="/tmp/log.txt",
        started_at=time.time(),
    )
    defaults.update(kw)
    return InstanceInfo(**defaults)


# ---------------------------------------------------------------------------
# InstanceInfo persistence
# ---------------------------------------------------------------------------


class TestSaveLoadInstance:
    def test_save_and_load(self) -> None:
        info = _make_info(port=8080, pid=12345)
        save_instance(info)
        loaded = load_instance(8080)
        assert loaded is not None
        assert loaded.pid == 12345
        assert loaded.port == 8080

    def test_load_nonexistent_returns_none(self) -> None:
        assert load_instance(9999) is None

    def test_remove_instance(self) -> None:
        info = _make_info(port=8001)
        save_instance(info)
        assert load_instance(8001) is not None
        remove_instance(8001)
        assert load_instance(8001) is None

    def test_remove_nonexistent_is_noop(self) -> None:
        remove_instance(7777)  # should not raise

    def test_corrupt_json_returns_none(self, tmp_path: Path) -> None:
        save_instance(_make_info(port=8002))
        meta = _meta_path(8002)
        meta.write_text("NOT VALID JSON", encoding="utf-8")
        assert load_instance(8002) is None

    def test_docs_dirs_persisted(self) -> None:
        info = _make_info(docs_dirs=["/a", "/b"])
        save_instance(info)
        loaded = load_instance(info.port)
        assert loaded is not None
        assert loaded.docs_dirs == ["/a", "/b"]


class TestListInstances:
    def test_empty(self) -> None:
        assert list_instances() == []

    def test_multiple(self) -> None:
        save_instance(_make_info(port=8000, pid=100))
        save_instance(_make_info(port=8001, pid=200))
        save_instance(_make_info(port=8002, pid=300))
        instances = list_instances()
        assert len(instances) == 3
        ports = {i.port for i in instances}
        assert ports == {8000, 8001, 8002}

    def test_skips_corrupt_files(self, tmp_path: Path) -> None:
        save_instance(_make_info(port=8000))
        # Write a corrupt file
        bad = _meta_path(8000).parent / "instance-9999.json"
        bad.write_text("{bad", encoding="utf-8")
        instances = list_instances()
        assert len(instances) == 1


# ---------------------------------------------------------------------------
# is_alive / kill_process
# ---------------------------------------------------------------------------


class TestIsAlive:
    def test_current_process_is_alive(self) -> None:
        assert is_alive(os.getpid()) is True

    def test_nonexistent_pid(self) -> None:
        # PID 2^30 is unlikely to exist
        assert is_alive(2**30) is False


class TestKillProcess:
    def test_kill_nonexistent_returns_true(self) -> None:
        # Already dead — should return True
        assert kill_process(2**30) is True

    def test_kill_real_subprocess(self) -> None:
        # Spawn a sleep process and kill it
        if sys.platform == "win32":
            proc = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(60)"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            proc = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(60)"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        pid = proc.pid
        assert is_alive(pid) is True
        ok = kill_process(pid)
        assert ok is True
        assert is_alive(pid) is False


# ---------------------------------------------------------------------------
# Meta/log path helpers
# ---------------------------------------------------------------------------


class TestPaths:
    def test_meta_path_contains_port(self) -> None:
        p = _meta_path(9000)
        assert "9000" in p.name
        assert p.suffix == ".json"

    def test_log_path_contains_port(self) -> None:
        p = _log_path(9000)
        assert "9000" in p.name
        assert p.suffix == ".log"

    def test_different_ports_different_files(self) -> None:
        assert _meta_path(8000) != _meta_path(8001)
        assert _log_path(8000) != _log_path(8001)
