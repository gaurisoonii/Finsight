"""
Module 3 — AI Insights Engine
Uses OpenAI GPT-4o (or Gemini) to summarize complaint batches
and generate natural-language policy insights.
"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ── Client setup ────────────────────────────────────────────────────────────
def _get_client():
    """Return OpenAI client. Falls back gracefully if key not set."""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return OpenAI(api_key=api_key)
    except ImportError:
        return None


# ── Complaint Summarizer ────────────────────────────────────────────────────

SUMMARIZER_SYSTEM = """You are a senior policy analyst at the Reserve Bank of India (RBI) Data Analytics Division.
Your task is to read a batch of consumer complaint narratives and produce a crisp 3–4 sentence analytical summary.

Rules:
- Lead with the most prevalent pattern you observe.
- Mention the top 2 specific pain points (e.g. "failed reversals", "unexpected charges").
- Note any geographic or seasonal pattern if detectable.
- Close with a single sentence on the likely systemic cause.
- Write in formal, professional English suitable for a regulatory report.
- Do NOT include headings, bullet points, or markdown. Plain prose only.
"""


def summarise_complaints(narratives: list[str], category: str) -> str:
    """
    Generate an analytical summary of complaint narratives for a category.
    Falls back to a template summary if no API key is set.
    """
    if not narratives:
        return f"No complaint narratives available for the {category} category."

    client = _get_client()

    if client is None:
        # Graceful fallback — deterministic template
        return (
            f"Analysis of {len(narratives)} {category} complaints reveals persistent service gaps. "
            f"Customers predominantly report transaction failures and delayed resolution timelines. "
            f"High complaint density is observed in urban centres, suggesting systemic issues "
            f"with peak-hour processing capacity. Underlying cause likely relates to inadequate "
            f"reconciliation workflows between banks and payment networks."
        )

    # Truncate narratives to stay within token limits
    sample = narratives[:15]
    combined = "\n---\n".join(
        f"Complaint {i+1}: {text[:400]}" for i, text in enumerate(sample)
    )

    prompt = (
        f"Category: {category}\n"
        f"Number of complaints in batch: {len(narratives)}\n\n"
        f"Complaint excerpts:\n{combined}\n\n"
        "Write the analytical summary now:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",  "content": SUMMARIZER_SYSTEM},
                {"role": "user",    "content": prompt},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[AI summary unavailable: {e}]"


# ── Policy Insight Generator ────────────────────────────────────────────────

POLICY_SYSTEM = """You are a regulatory economist writing for the RBI Governor's monthly brief.
Given a structured JSON of complaint spikes, write a concise policy insight paragraph (4–5 sentences).

Rules:
- Open with the most critical risk signal.
- Quantify growth percentages where provided.
- Recommend 2–3 specific regulatory actions.
- End with the monitoring metric RBI should track.
- Formal, precise English. No bullet points. No markdown.
"""


def generate_policy_insight(recommendations: list[dict]) -> str:
    """
    Convert structured policy recommendations into a narrative paragraph.
    """
    if not recommendations:
        return "No significant complaint spikes detected in the current period. Monitoring continues."

    client = _get_client()

    if client is None:
        # Fallback narrative
        cats = ", ".join(r["category"] for r in recommendations[:3])
        return (
            f"The current period shows elevated complaint activity across {cats}. "
            f"Complaint volumes in these segments have grown by up to "
            f"{max(r['growth_pct'] for r in recommendations):.1f}% month-over-month, "
            f"indicating systemic service delivery failures. Immediate regulatory "
            f"attention is recommended, particularly in refund reconciliation and "
            f"fraud response timelines. RBI should track weekly complaint-to-resolution "
            f"ratios across the top-5 affected institutions."
        )

    payload = json.dumps(recommendations, indent=2)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",  "content": POLICY_SYSTEM},
                {"role": "user",    "content": f"Complaint spike data:\n{payload}\n\nWrite the policy insight:"},
            ],
            temperature=0.2,
            max_tokens=350,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Policy insight unavailable: {e}]"


# ── Trend Narrative ─────────────────────────────────────────────────────────

def trend_narrative(trend_df, kpis: dict) -> str:
    """
    Short natural-language narrative for the Overview page trend section.
    """
    client = _get_client()

    if trend_df is None or trend_df.empty or client is None:
        growth = kpis.get("mom_growth", 0)
        direction = "increased" if growth > 0 else "decreased"
        return (
            f"Overall complaint volume has {direction} by {abs(growth):.1f}% month-over-month. "
            f"The dashboard reflects data from {kpis.get('total', 0):,} complaints. "
            f"Daily average stands at {kpis.get('avg_daily', 0):.0f} complaints per day."
        )

    recent = trend_df.tail(6).to_dict(orient="records")
    prompt = (
        f"KPIs: {json.dumps(kpis)}\n"
        f"Recent 6 months trend: {json.dumps(recent)}\n\n"
        "Write a 2-sentence overview of the complaint trend for a regulatory dashboard header:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.25,
            max_tokens=120,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


# ── Executive Summary Generator ─────────────────────────────────────────────

EXEC_SUMMARY_SYSTEM = """You are the lead policy analyst preparing the one-page executive brief that
opens the RBI Data Analytics & Policy Research monthly pack. Senior leadership reads only this section.

Rules:
- 4-6 sentences, plain prose, no bullet points or markdown.
- Sentence 1: headline state of complaint volumes and the overall risk posture.
- Sentence 2-3: the most significant risk(s) by category, quantified.
- Sentence 4-5: the policy implication / what action is being recommended.
- Close with one sentence naming the single metric leadership should watch next month.
- Formal, precise, confident. No hedging language like "it seems" or "may possibly".
"""


def generate_executive_summary(kpis: dict, risk_index: dict, recommendations: list[dict]) -> str:
    """
    One-page-brief narrative combining headline KPIs, the overall risk index,
    and active policy flags. Used on the Executive Summary page and in the
    PDF Policy Brief.
    """
    client = _get_client()

    if client is None:
        tier = risk_index.get("tier", "LOW")
        idx = risk_index.get("index", 0.0)
        growth = kpis.get("mom_growth", 0)
        direction = "risen" if growth > 0 else "eased"
        if recommendations:
            top = recommendations[0]
            risk_line = (
                f"The most significant exposure is {top['category']}, up "
                f"{top['growth_pct']:+.1f}% month-over-month and flagged {top['severity']}."
            )
            action_line = (
                f"Regulatory attention should prioritise the {len(recommendations)} active policy "
                f"flag(s), beginning with {top['category']}."
            )
        else:
            risk_line = "No category currently shows a statistically significant spike."
            action_line = "Routine monitoring is sufficient at this time; no immediate regulatory action is required."

        return (
            f"Overall complaint volume has {direction} {abs(growth):.1f}% month-over-month across "
            f"{kpis.get('total', 0):,} complaints, placing the system-wide risk index at {idx:.0f}/100 "
            f"({tier}). {risk_line} {action_line} "
            f"RBI should track the weekly complaint-to-resolution ratio in the highest-risk category next period."
        )

    payload = json.dumps({
        "kpis": kpis,
        "risk_index": risk_index,
        "policy_flags": recommendations[:5],
    }, indent=2)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": EXEC_SUMMARY_SYSTEM},
                {"role": "user",   "content": f"Current data:\n{payload}\n\nWrite the executive summary now:"},
            ],
            temperature=0.2,
            max_tokens=260,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Executive summary unavailable: {e}]"
