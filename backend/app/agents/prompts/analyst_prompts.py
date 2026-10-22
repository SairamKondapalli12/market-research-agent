"""Prompt templates for the Analyst Agent."""

SWOT_ANALYSIS_PROMPT = """Analyze the following competitive intelligence for {company}.

Recent events:
{events}

Produce a SWOT analysis in strict JSON format:
{{
  "strengths": ["..."],
  "weaknesses": ["..."],
  "opportunities": ["..."],
  "threats": ["..."]
}}

Each list should have 3-5 concise, evidence-based items. Return JSON only.
"""

TRENDS_ANALYSIS_PROMPT = """Based on the following market events around {company}, identify 3-5 key market trends.

Events:
{events}

Return strict JSON:
{{
  "trends": [
    {{"name": "...", "description": "...", "direction": "up|down|stable"}}
  ]
}}

Return JSON only.
"""

EVENT_SIGNIFICANCE_PROMPT = """Rate the significance of this competitive intelligence event on a scale of 1-10.

Event type: {event_type}
Company: {company}
Description: {description}

Consider: market impact, strategic importance, competitive threat level.

Return only a single integer 1-10.
"""