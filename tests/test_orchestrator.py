"""
Tests for src/orchestrator: run_workflow returns 4 steps with expected structure.
"""

from unittest.mock import patch, MagicMock

import pytest

from src.orchestrator import run_workflow

MOCK_AGENT_RESPONSE = "Mocked agent output."


@patch("src.orchestrator.run_offer_design", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_competitor_intel", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_customer_insights", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_market_research", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
def test_run_workflow_returns_four_steps(mock_market, mock_customer, mock_competitor, mock_offer, temp_data_dir):
    """run_workflow returns a list of 4 step dicts."""
    steps = run_workflow("test query", data_dir=temp_data_dir)
    assert len(steps) == 4
    mock_market.assert_called_once()
    mock_customer.assert_called_once()
    mock_competitor.assert_called_once()
    mock_offer.assert_called_once()


@patch("src.orchestrator.run_offer_design", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_competitor_intel", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_customer_insights", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_market_research", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
def test_run_workflow_step_structure(mock_market, mock_customer, mock_competitor, mock_offer, temp_data_dir):
    """Each step has agent, input_summary, output, hand_off, system_prompt, user_content, input_data_sample."""
    steps = run_workflow("test query", data_dir=temp_data_dir)
    expected_agents = [
        "Market Trends & Deep Research",
        "Customer Insights",
        "Competitor Intelligence",
        "Offer Design",
    ]
    for i, step in enumerate(steps):
        assert step["agent"] == expected_agents[i]
        assert "input_summary" in step
        assert "output" in step
        assert "hand_off" in step
        assert "system_prompt" in step
        assert "user_content" in step
        assert "input_data_sample" in step
        assert step["output"] == MOCK_AGENT_RESPONSE


@patch("src.orchestrator.run_offer_design", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_competitor_intel", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_customer_insights", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_market_research", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
def test_run_workflow_passes_user_query(mock_market, mock_customer, mock_competitor, mock_offer, temp_data_dir):
    """User query is reflected in the workflow."""
    steps = run_workflow("increase traffic for discount hunters", data_dir=temp_data_dir)
    assert len(steps) == 4
    # First step input should contain the query
    assert "increase traffic" in steps[0]["input_summary"] or "discount hunters" in steps[0]["input_summary"]


def test_run_workflow_raises_when_data_missing(tmp_path):
    """run_workflow raises when data dir has no CSVs."""
    with pytest.raises(FileNotFoundError, match="Data not found"):
        run_workflow("test query", data_dir=tmp_path)


@patch("src.orchestrator.run_offer_design", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_competitor_intel", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_customer_insights", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
@patch("src.orchestrator.run_market_research", return_value={"output": MOCK_AGENT_RESPONSE, "system_prompt": "", "user_content": ""})
def test_run_workflow_injects_scope(mock_market, mock_customer, mock_competitor, mock_offer, temp_data_dir):
    """When scope is provided, agents receive query enhanced with daypart/time_horizon."""
    steps = run_workflow(
        "breakfast offers",
        data_dir=temp_data_dir,
        scope={"daypart": "breakfast", "time_horizon": "Q1"},
    )
    assert len(steps) == 4
    # Market research is called as run_market_research(market_text, effective_query)
    call_args = mock_market.call_args
    assert call_args is not None
    effective_query = call_args[0][1]
    assert "daypart=breakfast" in effective_query
    assert "time_horizon=Q1" in effective_query
