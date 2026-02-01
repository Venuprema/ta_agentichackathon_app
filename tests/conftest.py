"""
Pytest fixtures for Wendy's Hackathon tests.
"""

import os
import sys
from pathlib import Path

import pytest

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temp dir and run data generator to fill it with CSVs."""
    import subprocess
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "generate_data.py"),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"generate_data failed: {result.stderr}"
    return tmp_path


@pytest.fixture
def temp_sessions_dir(tmp_path):
    """Empty temp dir for session JSON files."""
    return tmp_path
