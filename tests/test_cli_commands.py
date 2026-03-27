"""Tests for CLI commands: start, stop, restart, status, logs."""

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from litedocs.cli import app
from litedocs.process import InstanceInfo, save_instance

runner = CliRunner()


@pytest.fixture(autouse=True)
def _isolate_run_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect .litedocs run directory to temp location for all tests."""
    monkeypatch.setattr("litedocs.process._RUN_DIR", tmp_path / ".litedocs")
    monkeypatch.setattr("litedocs.cli._DEFAULT_DOCS_DIRS", [])


@pytest.fixture
def sample_docs(tmp_path: Path) -> Path:
    """Create a minimal docs directory for testing."""
    docs = tmp_path / "test-docs"
    docs.mkdir()
    en = docs / "en"
    en.mkdir()
    (en / "index.md").write_text("# Test\n\nHello.", encoding="utf-8")
    (en / "_sidebar.md").write_text("- [Home](index.md)\n", encoding="utf-8")
    config = {
        "site": {"title": "Test"},
        "locales": {"default": "en", "available": ["en"]},
    }
    (docs / "config.json").write_text(json.dumps(config), encoding="utf-8")
    return docs


def _make_saved_instance(port: int = 8000, pid: int = 99999, **kw) -> InstanceInfo:
    defaults = dict(
        pid=pid,
        port=port,
        host="127.0.0.1",
        base_path="",
        docs_dirs=["/tmp/docs"],
        log_file="/tmp/litedocs.log",
        started_at=time.time(),
    )
    defaults.update(kw)
    info = InstanceInfo(**defaults)
    save_instance(info)
    return info


# ---------------------------------------------------------------------------
# litedocs status
# ---------------------------------------------------------------------------


class TestStatusCommand:
    def test_no_instances(self) -> None:
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "No LiteDocs instances" in result.output

    def test_with_instances(self) -> None:
        _make_saved_instance(port=8000, pid=99999)
        _make_saved_instance(port=9000, pid=99998)
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "8000" in result.output
        assert "9000" in result.output


# ---------------------------------------------------------------------------
# litedocs stop
# ---------------------------------------------------------------------------


class TestStopCommand:
    def test_stop_no_instance(self) -> None:
        result = runner.invoke(app, ["stop"])
        assert result.exit_code == 1
        assert "No instance found" in result.output

    def test_stop_dead_instance_cleans_up(self) -> None:
        _make_saved_instance(port=8000, pid=99999)
        result = runner.invoke(app, ["stop"])
        assert result.exit_code == 0
        assert "not running" in result.output or "Cleaning up" in result.output

    def test_stop_all_no_instances(self) -> None:
        result = runner.invoke(app, ["stop", "--all"])
        assert result.exit_code == 0
        assert "No LiteDocs instances" in result.output

    def test_stop_all_cleans_dead(self) -> None:
        _make_saved_instance(port=8000, pid=99999)
        _make_saved_instance(port=9000, pid=99998)
        result = runner.invoke(app, ["stop", "--all"])
        assert result.exit_code == 0
        assert "8000" in result.output
        assert "9000" in result.output


# ---------------------------------------------------------------------------
# litedocs restart
# ---------------------------------------------------------------------------


class TestRestartCommand:
    def test_restart_no_instance(self) -> None:
        result = runner.invoke(app, ["restart"])
        assert result.exit_code == 1
        assert "No instance found" in result.output


# ---------------------------------------------------------------------------
# litedocs logs
# ---------------------------------------------------------------------------


class TestLogsCommand:
    def test_logs_no_instance(self) -> None:
        result = runner.invoke(app, ["logs"])
        assert result.exit_code == 1
        assert "No instance found" in result.output

    def test_logs_missing_file(self) -> None:
        _make_saved_instance(port=8000, log_file="/nonexistent/file.log")
        result = runner.invoke(app, ["logs", "--no-follow"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_logs_shows_content(self, tmp_path: Path) -> None:
        log_file = tmp_path / "test.log"
        log_file.write_text("line1\nline2\nline3\n", encoding="utf-8")
        _make_saved_instance(port=8000, log_file=str(log_file))
        result = runner.invoke(app, ["logs", "--no-follow", "--lines", "2"])
        assert result.exit_code == 0
        assert "line2" in result.output
        assert "line3" in result.output


# ---------------------------------------------------------------------------
# litedocs serve (help only — actual serve blocks)
# ---------------------------------------------------------------------------


class TestServeCommand:
    def test_serve_help(self) -> None:
        result = runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "foreground" in result.output.lower() or "documentation server" in result.output.lower()


# ---------------------------------------------------------------------------
# litedocs start
# ---------------------------------------------------------------------------


class TestStartCommand:
    def test_start_help(self) -> None:
        result = runner.invoke(app, ["start", "--help"])
        assert result.exit_code == 0
        assert "background" in result.output.lower() or "daemon" in result.output.lower()

    def test_start_duplicate_port(self, sample_docs: Path) -> None:
        """Starting on a port that already has a running instance should fail."""
        import os

        _make_saved_instance(port=8000, pid=os.getpid())  # current process = alive
        result = runner.invoke(app, ["start", str(sample_docs), "--port", "8000"])
        assert result.exit_code == 1
        assert "already running" in result.output


# ---------------------------------------------------------------------------
# Help output for all commands
# ---------------------------------------------------------------------------


class TestHelpOutput:
    @pytest.mark.parametrize("cmd", ["serve", "start", "stop", "restart", "status", "logs"])
    def test_help_exits_cleanly(self, cmd: str) -> None:
        result = runner.invoke(app, [cmd, "--help"])
        assert result.exit_code == 0
