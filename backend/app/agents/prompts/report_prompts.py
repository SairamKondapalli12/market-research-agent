"""Prompt templates for the Report Agent."""

EXECUTIVE_SUMMARY_PROMPT = """Write a 3-paragraph executive summary of a market research report.

Target company: {company}
Competitors analyzed: {competitor_count}

Key events:
{events}

Tone: professional, concise, strategic. No bullet points. No headings.
"""

RECOMMENDATIONS_PROMPT = """Based on the following analysis, produce 4-6 strategic recommendations for {company}.

SWOT:
{swot}

Recent events:
{events}

Return strict JSON:
{{
  "recommendations": ["...", "..."]
}}

Each recommendation must be actionable and specific. Return JSON only.
"""

FULL_REPORT_PROMPT = """Write a comprehensive market research report in Markdown.

Target company: {company}
Industry: {industry}

Competitors:
{competitors}

Intelligence events:
{events}

SWOT:
{swot}

Trends:
{trends}

Structure the report exactly as:
# Market Research Report: {company}
## Executive Summary
## Competitive Landscape
## SWOT Analysis
## Market Trends
## Recent Intelligence Events
## Recommendations

Be specific, evidence-based, and professional. Use Markdown formatting.
"""