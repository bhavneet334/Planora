# Planora

Planora helps you plan an event. You fill in a form with the event type, city, date, guest count, budget, and preferences. The app returns a starter plan with venue ideas, a budget breakdown, vendor suggestions, a checklist, and a timeline.

The backend uses LangGraph to run multiple AI agents (venue, budget, details) and validate the budget before sending the result to a React frontend.

## Features

- Event form: type, city, date, guests, budget, vibe, food, indoor or outdoor
- Multi agent generation with specialist agents for venues, budget, and logistics
- Budget validator with automatic retry if totals are off
- Groq LLM integration (Llama 3.3 70B)
- Mock fallback when AI is unavailable or when `USE_MOCK_PLAN=true`

## Tech stack

**Frontend:** React, TypeScript, Vite

**Backend:** Python, FastAPI, Pydantic

**AI:** LangGraph (StateGraph), Groq

**Validation:** Budget sum check in `validator.py`, with retry loop in the LangGraph orchestrator

## Architecture

Planora works like this:

```
User fills form (React)
    ↓
POST /plans/generate (FastAPI)
    ↓
plan_service → LangGraph orchestrator
    ↓
Venue agent → summary and venue ideas
    ↓
Budget agent → budget breakdown
    ↓
Details agent → vendors, checklist, timeline
    ↓
Validator → check budget total, retry budget if needed
    ↓
GeneratedPlan JSON → shown in the UI
```

## Project structure

```
Planora/
  frontend/src/          React app (form, results, API client)
  backend/
    main.py              FastAPI entry point
    routers/plans.py     POST /plans/generate
    schemas/event.py     Pydantic models (input and output)
    services/plan_service.py
    agents/
      orchestrator.py    LangGraph pipeline
      venue_agent.py
      budget_agent.py
      details_agent.py
      validator.py
      llm.py             Shared Groq helper
```

## Run locally

**Prerequisites:** Python 3.10+, Node.js 18+, [Groq API key](https://console.groq.com)

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Mac and Linux
pip install -r requirements.txt
cp .env.example .env
```

On Windows, activate with `.venv\Scripts\activate` instead of `source`.

Add your `GROQ_API_KEY` to `backend/.env`, then:

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

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM calls |
| `USE_MOCK_PLAN` | Set to `true` to skip AI and return a mock plan |

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

## Roadmap

- RAG with pgvector to retrieve event planning knowledge before generation
- Save and load plans in PostgreSQL (Supabase)
- Plan refinement via chat

## Author

- Built by Bhavneet Kaur
- Feel free to fork, clone, or contribute.
