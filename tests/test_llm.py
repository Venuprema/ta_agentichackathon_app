"""
Tests for src/llm.py: get_api_key, call_llm raises when no key.
"""

import os
from unittest.mock import patch

import pytest

from src.llm import get_api_key, call_llm


def test_get_api_key_returns_value_when_set():
    """get_api_key returns the key when GEMINI_API_KEY is set in env."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-123"}, clear=False):
        assert get_api_key() == "test-key-123"


def test_call_llm_raises_when_no_key():
    """call_llm raises ValueError when GEMINI_API_KEY is not set."""
    with patch("src.llm.get_api_key", return_value=None):
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            call_llm("system", "user")
