"""
Tests for src/data_loaders.py: data_available, load_*, summarize_for_llm.
"""

from pathlib import Path

import pandas as pd
import pytest

from src.data_loaders import (
    data_available,
    load_market_trends,
    load_customer_transactions,
    load_customer_feedback,
    load_competitor_intel,
    summarize_for_llm,
    get_data_dir,
)


def test_data_available_false_when_empty(tmp_path):
    """data_available returns False when no CSVs exist."""
    assert data_available(tmp_path) is False


def test_data_available_false_when_partial(tmp_path):
    """data_available returns False when only some CSVs exist."""
    (tmp_path / "market_trends.csv").write_text("a,b\n1,2")
    assert data_available(tmp_path) is False


def test_data_available_true_when_all_present(temp_data_dir):
    """data_available returns True when all four CSVs exist."""
    assert data_available(temp_data_dir) is True


def test_load_market_trends(temp_data_dir):
    """load_market_trends returns DataFrame with expected columns."""
    df = load_market_trends(temp_data_dir)
    assert isinstance(df, pd.DataFrame)
    assert "trend_theme" in df.columns
    assert "velocity_score" in df.columns
    assert len(df) == 1500


def test_load_customer_transactions(temp_data_dir):
    """load_customer_transactions returns DataFrame with expected columns."""
    df = load_customer_transactions(temp_data_dir)
    assert isinstance(df, pd.DataFrame)
    assert "redeemed_offer" in df.columns
    assert "channel" in df.columns
    assert len(df) == 2000


def test_load_customer_feedback(temp_data_dir):
    """load_customer_feedback returns DataFrame with expected columns."""
    df = load_customer_feedback(temp_data_dir)
    assert isinstance(df, pd.DataFrame)
    assert "rating" in df.columns
    assert "feedback_text" in df.columns
    assert len(df) == 1000


def test_load_competitor_intel(temp_data_dir):
    """load_competitor_intel returns DataFrame with expected columns."""
    df = load_competitor_intel(temp_data_dir)
    assert isinstance(df, pd.DataFrame)
    assert "brand" in df.columns
    assert "offer_mechanic" in df.columns
    assert len(df) == 1000


def test_load_raises_when_file_missing(tmp_path):
    """load_* raises FileNotFoundError when CSV is missing."""
    with pytest.raises(FileNotFoundError, match="Data not found"):
        load_market_trends(tmp_path)


def test_summarize_for_llm_returns_string(temp_data_dir):
    """summarize_for_llm returns a non-empty string."""
    df = load_market_trends(temp_data_dir)
    out = summarize_for_llm(df, max_rows=10, max_chars=5000)
    assert isinstance(out, str)
    assert len(out) > 0


def test_summarize_for_llm_truncates_large_df(temp_data_dir):
    """summarize_for_llm truncates when over max_chars."""
    df = load_market_trends(temp_data_dir)
    out = summarize_for_llm(df, max_rows=100, max_chars=500)
    assert "... (truncated)" in out or len(out) <= 600


def test_get_data_dir_returns_path():
    """get_data_dir returns a Path."""
    d = get_data_dir()
    assert isinstance(d, Path)
    assert "data" in str(d).lower() or d.name == "data"
