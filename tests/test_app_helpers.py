"""
Tests for Streamlit app helpers: save_session, load_session, list_sessions.
"""

import json
from unittest.mock import patch

import pytest


@pytest.fixture
def patch_sessions_dir(temp_sessions_dir):
    """Patch streamlit_app.SESSIONS_DIR to temp dir for the duration of the test."""
    with patch("streamlit_app.SESSIONS_DIR", temp_sessions_dir):
        yield temp_sessions_dir


def test_save_and_load_session(patch_sessions_dir):
    """save_session writes JSON; load_session reads it back."""
    from streamlit_app import save_session, load_session, ensure_sessions_dir
    ensure_sessions_dir()
    save_session("abc123", "test query", [{"agent": "Test", "output": "ok"}])
    loaded = load_session("abc123")
    assert loaded is not None
    assert loaded["session_id"] == "abc123"
    assert loaded["query"] == "test query"
    assert len(loaded["steps"]) == 1
    assert loaded["steps"][0]["agent"] == "Test"
    assert loaded["steps"][0]["output"] == "ok"


def test_load_session_returns_none_for_missing(patch_sessions_dir):
    """load_session returns None when session file does not exist."""
    from streamlit_app import load_session
    assert load_session("nonexistent") is None


def test_list_sessions_empty(patch_sessions_dir):
    """list_sessions returns empty list when no sessions."""
    from streamlit_app import list_sessions
    assert list_sessions() == []


def test_list_sessions_returns_ids(patch_sessions_dir):
    """list_sessions returns session ids from JSON files."""
    from streamlit_app import list_sessions, ensure_sessions_dir
    ensure_sessions_dir()
    (patch_sessions_dir / "s1.json").write_text(json.dumps({"session_id": "s1", "query": "q1", "steps": []}))
    (patch_sessions_dir / "s2.json").write_text(json.dumps({"session_id": "s2", "query": "q2", "steps": []}))
    ids = list_sessions()
    assert set(ids) == {"s1", "s2"}
    assert len(ids) == 2
