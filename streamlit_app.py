"""
Wendy's Hackathon – Streamlit app.
Multi-agent workflow: User Query -> Market Research -> Customer Insights -> Competitor Intelligence -> Offer Design (Top 3).
"""

import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

# Default: load .env from project root (GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL)
PROJECT_ROOT = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

import pandas as pd
import streamlit as st

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loaders import data_available, get_data_dir, load_market_trends, load_customer_transactions, load_customer_feedback, load_competitor_intel
from src.llm import get_api_key, call_llm
from src.orchestrator import run_workflow

SESSIONS_DIR = PROJECT_ROOT / "sessions"
DATA_DIR = get_data_dir()

AGENT_ICONS = {
    "Market Trends & Deep Research": "📊",
    "Customer Insights": "👥",
    "Competitor Intelligence": "🔍",
    "Offer Design": "💡",
}

AGENT_STATUS_MSG = {
    "Market Trends & Deep Research": "Detecting trends and themes...",
    "Customer Insights": "Profiling segments and preferences...",
    "Competitor Intelligence": "Mapping landscape and whitespace...",
    "Offer Design": "Synthesizing top 3 offers...",
}

# --- Prompt assistance ---
IDEAL_PROMPT_STRUCTURE = (
    "**Ideal structure:** [Goal] + [Number of offers] + [Customer segment/profile] + optional: [daypart] or [time horizon]. "
    "Example: *Develop 3 innovative offers to increase traffic for discount hunters* or "
    "*Breakfast offers for loyal customers next quarter*."
)

PROMPT_HELP_GOALS = ["Increase traffic", "Increase profit", "Drive engagement", "Launch new mechanic"]
PROMPT_HELP_SEGMENTS = ["Discount hunters", "Loyal repeaters", "Value-conscious customers", "Convenience-driven", "App-first users"]
PROMPT_HELP_DAYPARTS = ["Breakfast", "Lunch", "Late-night", "All day"]
PROMPT_HELP_HORIZONS = ["Next quarter", "Q1", "6 weeks", "2-week campaign"]


def parse_scope(query: str) -> dict:
    """Extract daypart and time_horizon from user query so agents can scope offers (e.g. breakfast only, Q1)."""
    q = (query or "").lower()
    daypart = None
    if any(x in q for x in ("breakfast", "morning")):
        daypart = "breakfast"
    elif any(x in q for x in ("lunch", "midday")):
        daypart = "lunch"
    elif any(x in q for x in ("late-night", "late night", "dinner", "evening")):
        daypart = "late-night"
    time_horizon = None
    if re.search(r"\bq1\b", q):
        time_horizon = "Q1"
    elif re.search(r"\bq2\b", q):
        time_horizon = "Q2"
    elif re.search(r"\bq3\b", q):
        time_horizon = "Q3"
    elif re.search(r"\bq4\b", q):
        time_horizon = "Q4"
    elif any(x in q for x in ("quarter", "next quarter", "this quarter")):
        time_horizon = "quarter"
    elif re.search(r"\d+\s*weeks?", q):
        m = re.search(r"(\d+)\s*weeks?", q)
        if m:
            time_horizon = f"{m.group(1)} weeks"
    return {"daypart": daypart, "time_horizon": time_horizon}


def ensure_sessions_dir():
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def list_sessions():
    ensure_sessions_dir()
    files = sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [f.stem for f in files]


def load_session(session_id: str):
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_session(session_id: str, query: str, steps: list):
    ensure_sessions_dir()
    path = SESSIONS_DIR / f"{session_id}.json"
    data = {"session_id": session_id, "query": query, "steps": steps}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_data_generator():
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "generate_data.py"), "--output-dir", str(DATA_DIR)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode == 0, result.stdout or "", result.stderr or ""
    except Exception as e:
        return False, "", str(e)


def get_data_summary():
    """Return list of {file, rows, cols} for CSVs in DATA_DIR."""
    summary = []
    for name in ["market_trends.csv", "customer_transactions.csv", "customer_feedback.csv", "competitor_intel.csv"]:
        p = DATA_DIR / name
        if p.exists():
            try:
                df = pd.read_csv(p)
                summary.append({"File": name, "Rows": len(df), "Columns": len(df.columns)})
            except Exception:
                summary.append({"File": name, "Rows": "-", "Columns": "-"})
    return summary


def validate_api_key():
    if not get_api_key():
        return False, "GEMINI_API_KEY not set. Add it to .env in the project root."
    try:
        call_llm("You are a test. Reply with exactly: OK", "Say OK")
        return True, None
    except Exception as e:
        return False, str(e)


def _extract_json_list(text: str):
    """Extract a JSON array of objects from text (e.g. ```json [...] ``` or raw [...]). Return list of dicts or None."""
    # Code block
    m = re.search(r"```(?:json)?\s*(\[\s*\{[\s\S]*?\}\s*\])\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Raw array
    m = re.search(r"\[\s*\{[\s\S]*\}\s*\]", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None


def _cell_to_display(val):
    """Convert a cell value for table display: list -> bullet string, dict -> compact string."""
    if isinstance(val, list):
        return " • " + "\n • ".join(str(x) for x in val) if val else ""
    if isinstance(val, dict):
        return " | ".join(f"{k}: {v}" for k, v in val.items())
    return "" if val is None else str(val)


def json_to_table(output: str):
    """Parse JSON list of objects from LLM output; each item = row, keys = columns. Lists/dicts in cells as bullets."""
    data = _extract_json_list(output)
    if not data or not isinstance(data, list):
        return None
    rows = []
    for item in data:
        if not isinstance(item, dict):
            continue
        row = {}
        for k, v in item.items():
            row[k] = _cell_to_display(v)
        rows.append(row)
    if not rows:
        return None
    return pd.DataFrame(rows)


def parse_markdown_table(text: str):
    """Try to extract a markdown table from text; return list of dicts or None."""
    lines = text.strip().split("\n")
    table_lines = []
    in_table = False
    for line in lines:
        if "|" in line and (line.strip().startswith("|") or "---" in line):
            in_table = True
            if "---" not in line:
                table_lines.append(line)
        elif in_table and "|" not in line:
            break
    if not table_lines:
        return None
    try:
        header = [c.strip() for c in table_lines[0].split("|") if c.strip()]
        rows = []
        for line in table_lines[1:]:
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= len(header):
                rows.append(dict(zip(header, cells[:len(header)])))
        return rows if rows else None
    except Exception:
        return None


# Canonical columns for top 3 offers table
TOP3_COLUMN_MAP = {
    "offer name": "Offer",
    "offer": "Offer",
    "name": "Offer",
    "channel": "Channel",
    "target segment": "Target customer segments",
    "target customer segments": "Target customer segments",
    "target": "Target customer segments",
    "duration": "Duration",
    "evidence": "Evidence map",
    "evidence map": "Evidence map",
    "evidence map (bullets)": "Evidence map",
}


def normalize_top3_table(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to Offer, Channel, Target customer segments, Duration, Evidence map."""
    if df is None or df.empty:
        return df
    new_cols = []
    for c in df.columns:
        key = str(c).strip().lower()
        new_cols.append(TOP3_COLUMN_MAP.get(key, c))
    df = df.copy()
    df.columns = new_cols
    return df


def output_to_table(output: str):
    """Represent LLM output as table: try JSON list first (list->rows, keys->columns), then markdown table."""
    tbl = json_to_table(output)
    if tbl is not None and not tbl.empty:
        return tbl
    parsed = parse_markdown_table(output)
    if parsed:
        return pd.DataFrame(parsed)
    return None


def main():
    st.set_page_config(page_title="Wendy's Offer Innovation", layout="wide")
    st.title("Wendy's Hackathon: Agentic AI for Offer Innovation")
    st.caption("Multi-agent workflow: Market Research → Customer Insights → Competitor Intelligence → Offer Design")

    # --- Sidebar ---
    with st.sidebar:
        st.header("API key")
        if "api_key_validated" not in st.session_state:
            with st.spinner("Validating API key..."):
                ok, err = validate_api_key()
                st.session_state["api_key_validated"] = ok
                st.session_state["api_key_error"] = err
        if st.session_state["api_key_validated"]:
            st.success("API key validated. Ready to run workflow.")
        else:
            st.error("API key validation failed.")
            st.caption(st.session_state.get("api_key_error", ""))

        st.divider()
        st.header("Data")
        if st.button("Generate / regenerate data", help="Rerun data script and update CSV files."):
            with st.spinner("Generating data..."):
                ok, out, err = run_data_generator()
            if ok:
                st.success("Data generated. Summary below.")
                summary = get_data_summary()
                if summary:
                    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
                st.rerun()
            else:
                st.error(f"Generation failed:\n{err}\n{out}")
        if data_available():
            summary = get_data_summary()
            if summary:
                st.caption("Data files summary")
                st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

        st.divider()
        st.header("Sessions")
        session_ids = list_sessions()
        if session_ids:
            selected = st.selectbox("Open a past session", ["(New run)"] + session_ids, key="session_select")
            if selected and selected != "(New run)":
                sess = load_session(selected)
                if sess:
                    st.session_state["view_query"] = sess["query"]
                    st.session_state["view_steps"] = sess["steps"]
                    st.session_state["view_only"] = True
                else:
                    st.session_state["view_only"] = False
            else:
                st.session_state["view_only"] = False
        else:
            st.info("No past sessions yet.")

    if not data_available():
        st.warning("Data not found. Click **Generate / regenerate data** in the sidebar, then reload.")
        st.stop()

    require_key = os.environ.get("REQUIRE_GEMINI_KEY", "").strip() in ("1", "true", "True", "yes")
    has_key = bool(get_api_key())
    if require_key and not has_key:
        st.error("**Deployment:** GEMINI_API_KEY is required.")
        st.stop()
    elif not has_key:
        st.info("**Local run:** GEMINI_API_KEY is optional. Set it in .env to run the workflow.")

    # --- Prompt assistance ---
    st.markdown(IDEAL_PROMPT_STRUCTURE)
    # Popover (Streamlit 1.37+) or expander as fallback
    def _render_prompt_help():
        st.markdown("**Goals:** " + ", ".join(PROMPT_HELP_GOALS))
        st.markdown("**Customer segments:** " + ", ".join(PROMPT_HELP_SEGMENTS))
        st.markdown("**Dayparts:** " + ", ".join(PROMPT_HELP_DAYPARTS))
        st.markdown("**Time horizons:** " + ", ".join(PROMPT_HELP_HORIZONS))
        st.caption("Use these in your prompt, e.g. '3 offers for discount hunters, breakfast only, next quarter'.")
    if getattr(st, "popover", None):
        with st.popover("📌 View goals, segments, dayparts & time horizons"):
            _render_prompt_help()
    else:
        with st.expander("📌 View goals, segments, dayparts & time horizons (click to expand)"):
            _render_prompt_help()

    query = st.text_area(
        "Your request",
        value=st.session_state.get("view_query", ""),
        placeholder="e.g. Develop three innovative offers to increase traffic for discount hunters",
        height=100,
        key="query_input",
    )
    col1, col2 = st.columns(2)
    with col1:
        run_clicked = st.button("Run workflow", type="primary")
    with col2:
        if st.session_state.get("view_only"):
            if st.button("New run"):
                st.session_state["view_only"] = False
                st.session_state["view_query"] = ""
                st.session_state["view_steps"] = None
                st.rerun()

    # --- View past session ---
    if st.session_state.get("view_only") and st.session_state.get("view_steps"):
        _render_session_result(st.session_state["view_steps"])
        st.stop()

    # --- Run workflow ---
    if run_clicked and query.strip():
        if not st.session_state.get("api_key_validated", False):
            st.error("API key validation failed. Fix .env and refresh.")
            st.caption(st.session_state.get("api_key_error", ""))
            st.stop()

        session_id = str(uuid.uuid4())[:8]
        progress_bar = st.progress(0.0, text="Starting...")
        status_placeholder = st.empty()
        thinking_steps = []

        def on_agent_start(agent_name: str, status_message: str):
            p = list(AGENT_ICONS.keys()).index(agent_name) / 4.0 if agent_name in AGENT_ICONS else 0
            progress_bar.progress(min(1.0, p + 0.25), text=status_message)
            icon = AGENT_ICONS.get(agent_name, "🤖")
            status_placeholder.markdown(f"**{icon} {agent_name}** — {status_message}")
            thinking_steps.append((agent_name, status_message))

        scope = parse_scope(query)
        try:
            steps = run_workflow(query.strip(), data_dir=DATA_DIR, on_agent_start=on_agent_start, scope=scope)
            progress_bar.progress(1.0, text="Done.")
            progress_bar.empty()
            status_placeholder.empty()

            save_session(session_id, query.strip(), steps)

            # Thinking steps (agent actions during run)
            with st.expander("Thinking steps", expanded=True):
                for i, (agent_name, msg) in enumerate(thinking_steps, 1):
                    icon = AGENT_ICONS.get(agent_name, "🤖")
                    st.markdown(f"{i}. **{icon} {agent_name}** — {msg}")

            # (a) Top 3 offers table
            st.subheader("Recommended top 3 offers")
            offer_step = next((s for s in steps if s["agent"] == "Offer Design"), None)
            if offer_step:
                tbl = output_to_table(offer_step["output"])
                if tbl is not None and not tbl.empty:
                    tbl = normalize_top3_table(tbl)
                    st.dataframe(tbl, use_container_width=True, hide_index=True)
                else:
                    st.markdown(offer_step["output"])

            # (b) Agent-wise details
            st.subheader("Agent-wise details")
            for i, step in enumerate(steps):
                _render_agent_step(step, i == 3)

            st.success("Workflow complete. Session saved.")
            st.balloons()
        except Exception as e:
            st.error(f"Workflow failed: {e}")
            import traceback
            st.code(traceback.format_exc())
    elif run_clicked and not query.strip():
        st.warning("Enter a request to run the workflow.")


def _render_agent_step(step: dict, expanded: bool):
    icon = AGENT_ICONS.get(step["agent"], "🤖")
    with st.expander(f"{icon} {step['agent']}", expanded=expanded):
        st.markdown("**(a) User query**")
        st.text(step.get("user_query", ""))

        st.markdown("**(b) Input data (sample, up to 5 rows)**")
        sample = step.get("input_data_sample") or []
        if sample:
            st.dataframe(pd.DataFrame(sample), use_container_width=True, hide_index=True)
        else:
            st.caption("No raw table (e.g. Offer Design uses prior agent outputs).")

        st.markdown("**(c) LLM call** (system + user content as sent to the model)")
        st.text_area("System prompt", value=step.get("system_prompt", ""), height=120, disabled=True, key=f"sys_{step['agent']}_{id(step)}")
        st.text_area("User content", value=step.get("user_content", ""), height=150, disabled=True, key=f"usr_{step['agent']}_{id(step)}")

        st.markdown("**(d) LLM response**")
        st.markdown(step.get("output", ""))

        st.markdown("**(e) Outputs (tabular when possible)**")
        out = step.get("output", "")
        tbl = json_to_table(out)
        if tbl is None or tbl.empty:
            tbl = output_to_table(out)
        if tbl is not None and not tbl.empty:
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        else:
            st.caption("No table detected; full response shown above.")


def _render_session_result(steps: list):
    st.subheader("Session result")
    with st.expander("Thinking steps", expanded=True):
        for i, step in enumerate(steps, 1):
            icon = AGENT_ICONS.get(step["agent"], "🤖")
            msg = AGENT_STATUS_MSG.get(step["agent"], step.get("hand_off", "—"))
            st.markdown(f"{i}. **{icon} {step['agent']}** — {msg}")
    offer_step = next((s for s in steps if s["agent"] == "Offer Design"), None)
    if offer_step:
        st.subheader("Recommended top 3 offers")
        tbl = output_to_table(offer_step.get("output", ""))
        if tbl is not None and not tbl.empty:
            tbl = normalize_top3_table(tbl)
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        else:
            st.markdown(offer_step.get("output", ""))
    st.subheader("Agent-wise details")
    for step in steps:
        _render_agent_step(step, step.get("agent") == "Offer Design")


if __name__ == "__main__":
    main()
