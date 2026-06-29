# Planora AI

Planora AI helps you plan an event. Fill in the event type, city, date, guest count, budget, and preferences and the app returns a starter plan with venue ideas, a budget breakdown, vendor suggestions, a checklist, and a timeline.

The backend uses **LangGraph** to run specialist agents (venue, budget, logistics) with a budget validator. Venues are grounded in **Google Places** results, with a **Supabase pgvector** cache to speed up repeat searches. A **React** frontend presents the plan with copy and PDF export.

## Features

- Event form with example fill, two-column layout, and loading progress
- Multi-agent generation: venue research → venue summary, budget, vendors/checklist/timeline
- Real venue search via Google Places, with pgvector RAG cache (Gemini embeddings)
- Budget validator with automatic retry when totals are off
- Plan results panel: budget bar, interactive checklist, timeline, copy, PDF download
- Groq LLM integration (Llama 3.3 70B)
- Mock fallback when AI is unavailable or when `USE_MOCK_PLAN=true`

## Tech stack

| Layer | Stack |
|-------|-------|
| Frontend | React, TypeScript, Vite, jsPDF |
| Backend | Python, FastAPI, Pydantic |
| AI | LangGraph (StateGraph), Groq |
| Data | Google Places API, Supabase (pgvector), Gemini embeddings |
| Validation | Budget sum check with retry loop in the orchestrator |

## Architecture

```
User fills form (React)
    ↓
POST /plans/generate (FastAPI)
    ↓
plan_service → LangGraph orchestrator
    ↓
venue_research → RAG cache (Supabase) → Google Places fallback
    ↓
venue_agent → event summary + venue ideas (from real results when available)
    ↓
budget_agent → budget breakdown
    ↓
details_agent → vendors, checklist, timeline
    ↓
validator → check budget total, retry budget if needed
    ↓
GeneratedPlan JSON → PlanResults UI (copy / PDF)
```

**Venue RAG flow:** `lookup_venues` searches the pgvector cache first. If enough matches exist for the city, those are returned. Otherwise Google Places is queried and results are embedded and saved for next time.

## Project structure

```
Planora/
  frontend/src/
    App.tsx                    Form, hero, loading state
    components/PlanResults.tsx   Results panel (budget bar, checklist, timeline)
    utils/planExport.ts          Markdown copy + PDF export
    api/plans.ts                 API client
  backend/
    main.py                      FastAPI entry point
    routers/plans.py             POST /plans/generate
    schemas/event.py             Pydantic models
    services/plan_service.py     Orchestrator entry + mock fallback
    tools/venue_lookup.py        Google Places + cache lookup
    memory/vectordb.py           pgvector RAG (save + search venues)
    agents/
      orchestrator.py            LangGraph pipeline
      venue_research.py          Venue lookup node
      venue_agent.py             Summary + venue selection
      budget_agent.py            Budget breakdown
      details_agent.py           Vendors, checklist, timeline
      validator.py                 Budget total check
      llm.py                     Shared Groq helper
```

## Run locally

**Prerequisites:** Python 3.10+, Node.js 18+, [Groq API key](https://console.groq.com)

Optional for real venues and RAG cache: Google Places API key, Supabase project, Gemini API key (see environment variables below).

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Mac and Linux
pip install -r requirements.txt
cp .env.example .env
```

On Windows, activate with `.venv\Scripts\activate` instead of `source`.

Add keys to `backend/.env`, then:

```bash
uvicorn main:app --reload --port 8000
```

API: http://127.0.0.1:8000  
Health: http://127.0.0.1:8000/health

**Frontend** (second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLM calls |
| `GOOGLE_PLACES_API_KEY` | For real venues | Google Places text search |
| `SUPABASE_URL` | For RAG cache | Supabase project URL |
| `SUPABASE_KEY` | For RAG cache | Supabase service role key |
| `GOOGLE_API_KEY` | For RAG cache | Gemini API key for embeddings (AI Studio) |
| `USE_MOCK_PLAN` | No | Set to `true` to skip AI and return a mock plan |

Without Places/Supabase keys, venue research returns empty and the venue agent falls back to LLM-only suggestions.

## API

**POST /plans/generate**

Example request:

```json
{
  "event_type": "Birthday party",
  "city": "Chicago",
  "date": "2026-06-26",
  "guest_count": 50,
  "budget": 10000,
  "vibe": "Elegant",
  "food_preferences": "Both veg and non-veg",
  "indoor_outdoor": "Indoor"
}
```

Returns `event_summary`, `venue_ideas`, `vendor_suggestions`, `budget_breakdown`, `checklist`, and `timeline`.



## Author

- Built by Bhavneet Kaur
- Feel free to fork, clone, or contribute.
