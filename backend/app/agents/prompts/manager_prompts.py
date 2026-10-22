"""Prompt templates for the Manager Agent."""

RESEARCH_PLAN_PROMPT = """You are a research project manager.

Target company: {company}
Industry: {industry}
Research depth: {depth}

Define a concise plan with:
1. Primary research questions (3-5)
2. Key competitor categories to investigate
3. Data sources to prioritize

Respond in under 200 words.
"""

PIPELINE_REVIEW_PROMPT = """Review the following research deliverables:

Competitors discovered: {competitor_count}
Articles collected: {article_count}
Events extracted: {event_count}

Is the data sufficient for a report? Answer YES or NO and give a one-line reason.
"""