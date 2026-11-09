# Architecture

## High-level flow
React/Next.js ⇄ FastAPI ⇄ CrewAI (Manager / Researcher / Analyst / Report)
│
├── PostgreSQL + pgvector
├── Tavily Search API
├── Playwright (Chromium)
└── Google Gemini

text

## Agents

1. **Manager** — orchestrates the pipeline.
2. **Researcher** — discovers competitors and gathers articles.
3. **Analyst** — classifies events, scores significance, produces SWOT and trends.
4. **Report** — writes the final markdown report.

## Data flow

1. User creates a ResearchRequest via `POST /api/v1/research`.
2. The backend creates the row and schedules `ResearchService.run_pipeline` as a background task.
3. ManagerAgent runs the researcher → analyst → report pipeline.
4. Competitors, articles, events, and reports are persisted in PostgreSQL.
5. The frontend polls `/research/{id}` and eventually renders the report.