# Autonomous AI-Powered Market Research Agent

A multi-agent AI system that autonomously performs competitive market
research and generates structured intelligence reports.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL + pgvector, CrewAI, Google Gemini
- **Frontend:** Next.js 14, React 18, Tailwind CSS, Recharts
- **Search:** Tavily API
- **Scraping:** Playwright (Chromium headless)
- **Background:** Celery + Redis
- **Auth:** JWT

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
cp .env.example .env    # fill in your API keys
uvicorn app.main:app --reload