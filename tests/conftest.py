"""Shared test fixtures for LiteDocs."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_DOCS_DIR = FIXTURES_DIR / "sample-docs"


@pytest.fixture
def sample_docs_path() -> Path:
    """Return the path to the sample documentation site fixture."""
    return SAMPLE_DOCS_DIR


@pytest.fixture
def sample_config_path(sample_docs_path: Path) -> Path:
    """Return the path to the sample config.json."""
    return sample_docs_path / "config.json"
