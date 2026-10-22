"""Prompt template for the Executive One-Pager."""

ONEPAGER_PROMPT = """You are an executive analyst.

Produce a 60-second executive one-pager for {company} from the following report.

Report title: {title}
Executive summary:
{executive_summary}

Top 3 events:
{events}

Top 3 recommendations:
{recommendations}

Output strict JSON:
{{
  "headline": "<one-line takeaway, under 15 words>",
  "key_points": ["<3 to 5 short bullet points, each under 20 words>"],
  "action": "<one imperative next step, under 20 words>"
}}

Return JSON only."""