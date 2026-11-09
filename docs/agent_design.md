# Agent Design

The system coordinates seven specialised agents under the direction of a Manager Agent. Each agent is implemented as a Python class in `backend/app/agents/`.

## Manager Agent

- **File:** `manager_agent.py`
- **Role:** Research Project Manager
- **Responsibilities:** Orchestrates the pipeline, delegates to specialist agents, persists results, triggers change detection, sends notifications.
- **Downstream agents:** Researcher, Analyst, Sentiment, Financial, Report.
- **Emits:** Progress events via Redis pub/sub channel `research:{request_id}:events`.

## Researcher Agent

- **File:** `researcher_agent.py`
- **Role:** Senior Web Researcher
- **Tools:** `TavilySearchTool`, `PlaywrightScraperTool`, `DataExtractorTool`
- **Output:** List of competitor dicts, list of article dicts.
- **Persistence:** Writes to `competitors` and `articles` tables.

## Analyst Agent

- **File:** `analyst_agent.py`
- **Role:** Competitive Intelligence Analyst
- **Tools:** `EventClassifierTool`, `SignificanceScorerTool`
- **Output:** Structured intelligence events, SWOT analysis per company, market trends.
- **Persistence:** Writes to `intelligence_events` table and embeds SWOT/trends in the Report.

## Sentiment Agent

- **File:** `sentiment_agent.py`
- **Role:** Market Sentiment Analyst
- **Tools:** `SentimentScorerTool` (rule-based fallback)
- **Output:** Per-company sentiment score (−1.0 to +1.0), distribution, drivers, and a narrative summary.
- **Persistence:** Writes to `sentiment_records` table.
- **Enabled by:** `SENTIMENT_ENABLED=true`.

## Financial Intelligence Agent

- **File:** `financial_agent.py`
- **Role:** Financial Intelligence Analyst
- **Tools:** `FinancialDataExtractorTool`, `CrunchbaseTool` (optional paid tier)
- **Output:** Funding rounds, total raised, latest valuation, estimated revenue, investor list.
- **Persistence:** Writes to `financial_profiles`, `funding_rounds`, and `investors` tables.

## Report Agent

- **File:** `report_agent.py`
- **Role:** Business Report Writer
- **Output:** Executive summary, full Markdown report, strategic recommendations, one-pager payload.
- **Persistence:** Writes to `reports` table.

## Tool Reference

| Tool | Purpose |
|------|---------|
| `TavilySearchTool` | AI-native web search returning structured results |
| `PlaywrightScraperTool` | Headless Chromium scraping for JS-rendered pages |
| `DataExtractorTool` | Parses HTML and infers competitor names |
| `EventClassifierTool` | Maps text to event types (funding, launch, etc.) |
| `SignificanceScorerTool` | Scores events 1–10 based on impact signals |
| `SentimentScorerTool` | Rule-based sentiment fallback |
| `FinancialDataExtractorTool` | Rule-based financial signal extraction |
| `CrunchbaseTool` | Optional Crunchbase lookup for funding data |

## Pipeline Flow

```
User submits company name
    → Manager initialises pipeline
    → Researcher discovers competitors + scrapes articles
    → Analyst extracts events + builds SWOT
    → Sentiment scores perception per competitor
    → Financial extracts funding + valuation data
    → Report composes the final Markdown report
    → Change Detection compares against previous report
    → Notification sent to user
```