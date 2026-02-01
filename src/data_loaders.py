"""
Load Wendy's Hackathon CSV data from data/ (or custom path).
Loads .env from project root so WENDYS_DATA_DIR is applied when set.
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd

# Default data directory relative to project root
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_env_loaded = False


def _load_dotenv():
    global _env_loaded
    if _env_loaded:
        return
    try:
        from dotenv import load_dotenv
        root = Path(__file__).resolve().parent.parent
        load_dotenv(root / ".env")
        _env_loaded = True
    except ImportError:
        pass


def get_data_dir() -> Path:
    """Data directory for CSVs. Uses WENDYS_DATA_DIR from .env if set."""
    _load_dotenv()
    return Path(os.environ.get("WENDYS_DATA_DIR", str(DEFAULT_DATA_DIR)))


def _path(name: str, data_dir: Optional[Path] = None) -> Path:
    d = data_dir or get_data_dir()
    return d / name


def data_available(data_dir: Optional[Path] = None) -> bool:
    """True if all four CSV files exist."""
    d = data_dir or get_data_dir()
    return all(
        (_path(f, d).exists() for f in [
            "market_trends.csv",
            "customer_transactions.csv",
            "customer_feedback.csv",
            "competitor_intel.csv",
        ])
    )


def load_market_trends(data_dir: Optional[Path] = None) -> pd.DataFrame:
    p = _path("market_trends.csv", data_dir)
    if not p.exists():
        raise FileNotFoundError(f"Data not found: {p}. Run scripts/generate_data.py first.")
    return pd.read_csv(p)


def load_customer_transactions(data_dir: Optional[Path] = None) -> pd.DataFrame:
    p = _path("customer_transactions.csv", data_dir)
    if not p.exists():
        raise FileNotFoundError(f"Data not found: {p}. Run scripts/generate_data.py first.")
    return pd.read_csv(p)


def load_customer_feedback(data_dir: Optional[Path] = None) -> pd.DataFrame:
    p = _path("customer_feedback.csv", data_dir)
    if not p.exists():
        raise FileNotFoundError(f"Data not found: {p}. Run scripts/generate_data.py first.")
    return pd.read_csv(p)


def load_competitor_intel(data_dir: Optional[Path] = None) -> pd.DataFrame:
    p = _path("competitor_intel.csv", data_dir)
    if not p.exists():
        raise FileNotFoundError(f"Data not found: {p}. Run scripts/generate_data.py first.")
    return pd.read_csv(p)


def summarize_for_llm(df: pd.DataFrame, max_rows: int = 80, max_chars: int = 12000) -> str:
    """Sample and truncate a DataFrame to text for LLM context."""
    sample = df.sample(n=min(max_rows, len(df)), random_state=42) if len(df) > max_rows else df
    text = sample.to_string(max_colwidth=200)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n... (truncated)"
    return text


