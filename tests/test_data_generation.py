"""
Tests for scripts/generate_data.py: CSV output, schemas, row counts.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_generate_data_creates_four_csvs(temp_data_dir):
    """Data generator produces exactly four CSV files."""
    assert (temp_data_dir / "market_trends.csv").exists()
    assert (temp_data_dir / "customer_transactions.csv").exists()
    assert (temp_data_dir / "customer_feedback.csv").exists()
    assert (temp_data_dir / "competitor_intel.csv").exists()
    csvs = list(temp_data_dir.glob("*.csv"))
    assert len(csvs) == 4


def test_market_trends_schema_and_count(temp_data_dir):
    """Market trends CSV has expected columns and 1500 rows."""
    df = pd.read_csv(temp_data_dir / "market_trends.csv")
    expected_cols = {"source_id", "source_type", "text_content", "publication_date", "trend_theme", "velocity_score"}
    assert set(df.columns) == expected_cols
    assert len(df) == 1500


def test_customer_transactions_schema_and_count(temp_data_dir):
    """Customer transactions CSV has expected columns and 2000 rows."""
    df = pd.read_csv(temp_data_dir / "customer_transactions.csv")
    expected_cols = {"transaction_id", "customer_id", "visit_date", "total_spend", "redeemed_offer", "channel"}
    assert set(df.columns) == expected_cols
    assert len(df) == 2000


def test_customer_feedback_schema_and_count(temp_data_dir):
    """Customer feedback CSV has expected columns and 1000 rows."""
    df = pd.read_csv(temp_data_dir / "customer_feedback.csv")
    expected_cols = {"feedback_id", "customer_id", "feedback_date", "rating", "feedback_text"}
    assert set(df.columns) == expected_cols
    assert len(df) == 1000


def test_competitor_intel_schema_and_count(temp_data_dir):
    """Competitor intel CSV has expected columns and 1000 rows."""
    df = pd.read_csv(temp_data_dir / "competitor_intel.csv")
    expected_cols = {"observation_id", "brand", "offer_mechanic", "duration_days", "channel", "observed_date"}
    assert set(df.columns) == expected_cols
    assert len(df) == 1000


def test_generate_data_via_subprocess(tmp_path):
    """Data generator can be run as subprocess with --output-dir."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "generate_data.py"), "--output-dir", str(tmp_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert (tmp_path / "market_trends.csv").exists()
    assert (tmp_path / "customer_transactions.csv").exists()
