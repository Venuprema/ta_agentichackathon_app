"""
Tests for src/agents: each agent returns LLM output (with mocked call_llm).
"""

from unittest.mock import patch

import pytest

from src.agents.market_research import run as run_market_research
from src.agents.customer_insights import run as run_customer_insights
from src.agents.competitor_intel import run as run_competitor_intel
from src.agents.offer_design import run as run_offer_design


MOCK_RESPONSE = "Mocked LLM response for testing."


@patch("src.agents.market_research.call_llm", return_value=MOCK_RESPONSE)
def test_market_research_agent_returns_llm_output(mock_call_llm):
    """Market Research agent returns dict with output, system_prompt, user_content."""
    out = run_market_research("sample market data", "user query")
    assert isinstance(out, dict)
    assert out["output"] == MOCK_RESPONSE
    assert "system_prompt" in out and "user_content" in out
    mock_call_llm.assert_called_once()
    args = mock_call_llm.call_args
    assert "sample market data" in args[0][1]
    assert "user query" in args[0][1]


@patch("src.agents.customer_insights.call_llm", return_value=MOCK_RESPONSE)
def test_customer_insights_agent_returns_llm_output(mock_call_llm):
    """Customer Insights agent returns dict with output."""
    out = run_customer_insights("txn data", "feedback data", "user query")
    assert isinstance(out, dict) and out["output"] == MOCK_RESPONSE
    mock_call_llm.assert_called_once()
    args = mock_call_llm.call_args
    assert "txn data" in args[0][1]
    assert "feedback data" in args[0][1]
    assert "user query" in args[0][1]


@patch("src.agents.competitor_intel.call_llm", return_value=MOCK_RESPONSE)
def test_competitor_intel_agent_returns_llm_output(mock_call_llm):
    """Competitor Intelligence agent returns dict with output."""
    out = run_competitor_intel("competitor data", "user query")
    assert isinstance(out, dict) and out["output"] == MOCK_RESPONSE
    mock_call_llm.assert_called_once()
    args = mock_call_llm.call_args
    assert "competitor data" in args[0][1]
    assert "user query" in args[0][1]


@patch("src.agents.offer_design.call_llm", return_value=MOCK_RESPONSE)
def test_offer_design_agent_returns_llm_output(mock_call_llm):
    """Offer Design agent returns dict with output."""
    out = run_offer_design("trends", "insights", "landscape", "whitespace", "user query")
    assert isinstance(out, dict) and out["output"] == MOCK_RESPONSE
    mock_call_llm.assert_called_once()
    args = mock_call_llm.call_args
    assert "trends" in args[0][1]
    assert "insights" in args[0][1]
    assert "user query" in args[0][1]
