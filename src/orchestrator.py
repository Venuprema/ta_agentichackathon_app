"""
Orchestrator: runs Market Research -> Customer Insights -> Competitor Intelligence -> Offer Design
in sequence and returns full trace + top 3 offers.
"""

import pandas as pd
from pathlib import Path
from typing import Any, Optional

from src.agents.market_research import run as run_market_research
from src.agents.customer_insights import run as run_customer_insights
from src.agents.competitor_intel import run as run_competitor_intel
from src.agents.offer_design import run as run_offer_design
from src.data_loaders import (
    load_market_trends,
    load_customer_transactions,
    load_customer_feedback,
    load_competitor_intel,
    summarize_for_llm,
    get_data_dir,
)


def _sample_df(df: pd.DataFrame, n: int = 5) -> list[dict[str, Any]]:
    """First n rows as list of dicts for table display."""
    return df.head(n).fillna("").astype(str).to_dict(orient="records")


def _enhance_query_with_scope(user_query: str, scope: Optional[dict[str, Optional[str]]]) -> str:
    """Prepend parsed scope (daypart, time_horizon) so agents explicitly see it."""
    if not scope or not any(scope.get(k) for k in ("daypart", "time_horizon")):
        return user_query
    parts = [f"daypart={scope['daypart']}" if scope.get("daypart") else None, f"time_horizon={scope['time_horizon']}" if scope.get("time_horizon") else None]
    parts = [p for p in parts if p]
    if not parts:
        return user_query
    return user_query + "\n\n[Parsed scope from your request: " + ", ".join(parts) + "]"


def run_workflow(
    user_query: str,
    data_dir: Optional[Path] = None,
    on_agent_start: Optional[Any] = None,
    scope: Optional[dict[str, Optional[str]]] = None,
) -> list[dict[str, Any]]:
    """
    Run full agent flow. Returns list of step results.
    If on_agent_start(agent_name, status_message) is provided, it is called before each agent runs.
    scope: optional dict with daypart, time_horizon (parsed from user query) to inject into agent context.
    """
    data_dir = data_dir or get_data_dir()
    steps = []
    effective_query = _enhance_query_with_scope(user_query, scope)

    def _notify(name: str, msg: str):
        if on_agent_start:
            try:
                on_agent_start(name, msg)
            except Exception:
                pass

    df_market = load_market_trends(data_dir)
    df_txn = load_customer_transactions(data_dir)
    df_feedback = load_customer_feedback(data_dir)
    df_comp = load_competitor_intel(data_dir)

    market_text = summarize_for_llm(df_market)
    txn_text = summarize_for_llm(df_txn)
    feedback_text = summarize_for_llm(df_feedback)
    comp_text = summarize_for_llm(df_comp)

    # 1. Market Research
    _notify("Market Trends & Deep Research", "Detecting trends and themes...")
    step1_input = f"User query: {effective_query}\n\nMarket trends data (sample): {market_text[:4000]}..."
    res1 = run_market_research(market_text, effective_query)
    steps.append({
        "agent": "Market Trends & Deep Research",
        "user_query": user_query,
        "input_data_sample": _sample_df(df_market),
        "input_summary": step1_input[:1500] + "..." if len(step1_input) > 1500 else step1_input,
        "system_prompt": res1["system_prompt"],
        "user_content": res1["user_content"],
        "output": res1["output"],
        "hand_off": "Trend briefs passed to Customer Insights and Offer Design.",
    })
    out1 = res1["output"]

    # 2. Customer Insights
    _notify("Customer Insights", "Profiling segments and preferences...")
    step2_input = f"User query: {effective_query}\n\nTransactions + feedback (sample): {txn_text[:2000]}... {feedback_text[:2000]}..."
    res2 = run_customer_insights(txn_text, feedback_text, effective_query)
    # Combine two dfs for display: show txn head + feedback head
    combined_sample = _sample_df(df_txn) + _sample_df(df_feedback)
    steps.append({
        "agent": "Customer Insights",
        "user_query": user_query,
        "input_data_sample": combined_sample[:5],
        "input_summary": step2_input[:1500] + "..." if len(step2_input) > 1500 else step2_input,
        "system_prompt": res2["system_prompt"],
        "user_content": res2["user_content"],
        "output": res2["output"],
        "hand_off": "Customer segment insights passed to Offer Design.",
    })
    out2 = res2["output"]

    # 3. Competitor Intelligence
    _notify("Competitor Intelligence", "Mapping landscape and whitespace...")
    step3_input = f"User query: {effective_query}\n\nCompetitor data (sample): {comp_text[:4000]}..."
    res3 = run_competitor_intel(comp_text, effective_query)
    steps.append({
        "agent": "Competitor Intelligence",
        "user_query": user_query,
        "input_data_sample": _sample_df(df_comp),
        "input_summary": step3_input[:1500] + "..." if len(step3_input) > 1500 else step3_input,
        "system_prompt": res3["system_prompt"],
        "user_content": res3["user_content"],
        "output": res3["output"],
        "hand_off": "Competitive landscape and whitespace opportunities passed to Offer Design.",
    })
    out3 = res3["output"]

    # 4. Offer Design
    _notify("Offer Design", "Synthesizing top 3 offers...")
    step4_input = f"User query: {effective_query}\n\nInputs from agents:\n- Trend briefs: {out1[:2000]}...\n- Customer insights: {out2[:2000]}...\n- Competitor intel: {out3[:2000]}..."
    res4 = run_offer_design(out1, out2, out3, out3, effective_query)
    steps.append({
        "agent": "Offer Design",
        "user_query": user_query,
        "input_data_sample": [],  # No raw table; inputs are prior agent outputs
        "input_summary": step4_input[:1500] + "..." if len(step4_input) > 1500 else step4_input,
        "system_prompt": res4["system_prompt"],
        "user_content": res4["user_content"],
        "output": res4["output"],
        "hand_off": "Top 3 offer concepts delivered.",
    })

    return steps
