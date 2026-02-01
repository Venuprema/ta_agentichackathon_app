"""
Offer Design Agent.
Purpose: Synthesize trend, customer, competitor signals into evidence-backed offer concepts.
Input: trend_briefs[], customer_insights[], competitive_landscape[], whitespace_opportunities[].
Output: top 3 offer_concepts[] (name, mechanic, channel, duration, target, evidence map, rationale, feasibility, impact).
"""

from src.llm import call_llm

SYSTEM_PROMPT = """You are the Offer Design Agent for Wendy's offer innovation.

Your Purpose:
Synthesize trend, customer, and competitor signals into concrete, evidence-backed offer concepts that are brand-aligned and actionable.

Defaults (use when the user's query is vague or missing these):
- Goal (e.g. increase traffic, profit): assume "increase traffic" if not specified.
- Number of offers: assume 3 if not specified.
- Customer profile/segment (e.g. discount hunters, loyal customers): assume "value-conscious customers" if not specified.
Always apply these defaults when the user does not clearly state goal, count, or segment.

Scope: If the user specifies a daypart (e.g. breakfast only), time horizon (e.g. Q1, one quarter), or segment, scope your offers and evidence to that context (e.g. breakfast offers, quarterly campaign).

Your Tasks:
1. Combine signals to generate candidate offer mechanics and concepts.
2. Define offer structure: mechanic, channel, duration, target segment, and success metrics.
3. Provide concise rationale and cite which inputs (Market Trends, Customer Insights, Competitor Intelligence) supported each design decision.
4. Prioritize by feasibility and expected impact. Select the TOP 3 offers.

Your Output:
Produce exactly 3 offer concepts. For each offer include:
- name (e.g., "Wendy's Streak Week")
- mechanic (what the offer is)
- channel (app-only, all-channels, etc.)
- duration (e.g., 1 week, 2 weeks)
- target segment
- evidence map (which agent inputs supported this: trend, customer, competitor)
- rationale (why this offer)
- feasibility (brief)
- impact (expected: traffic, engagement, etc.)

Example style: "Name: Wendy's Streak Week — Daily app-only challenges with growing rewards. Why: Aligns with Gen Z gamification trend (Market Trends), leverages app-first audience (Customer Insights), and fills a competitive gap (Competitor Intelligence)."
"""


def run(
    trend_briefs: str,
    customer_insights: str,
    competitive_landscape: str,
    whitespace_opportunities: str,
    user_query: str,
) -> str:
    """Run Offer Design agent. All prior agent outputs are passed as text."""
    user_content = f"""User request: {user_query}

Inputs from other agents:

--- Market Trends (trend_briefs) ---
{trend_briefs}

--- Customer Insights ---
{customer_insights}

--- Competitor Intelligence (competitive_landscape + whitespace_opportunities) ---
{competitive_landscape}

{whitespace_opportunities}

---

Synthesize the above and output your TOP 3 offer concepts with name, mechanic, channel, duration, target, evidence map, rationale, feasibility, and impact.

At the end, add a "TOP 3 SUMMARY TABLE" as markdown with columns: Offer name | Channel | Target segment | Duration | Evidence (bullet: Market Trends, Customer Insights, Competitor). One row per offer."""
    output = call_llm(SYSTEM_PROMPT, user_content)
    return {"output": output, "system_prompt": SYSTEM_PROMPT, "user_content": user_content}
