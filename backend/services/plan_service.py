import json
import os

from openai import OpenAI

from schemas.event import BudgetItem, EventInput, GeneratedPlan, TimelineItem

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _build_prompt(event: EventInput) -> str:
    return f"""
You are an expert event planner. Create a practical starter plan for this event.

Event details:
- Event type: {event.event_type}
- City: {event.city}
- Date: {event.date}
- Guest count: {event.guest_count}
- Budget: ${event.budget:,.0f}
- Vibe: {event.vibe}
- Food preferences: {event.food_preferences}
- Indoor/Outdoor: {event.indoor_outdoor}

Return ONLY valid JSON with this exact structure:
{{
  "event_summary": "string",
  "venue_ideas": ["string", "string", "string"],
  "vendor_suggestions": ["string", "string", "string", "string"],
  "budget_breakdown": [
    {{ "category": "string", "amount": number, "notes": "string" }}
  ],
  "checklist": ["string", "string", "string", "string", "string"],
  "timeline": [
    {{ "when": "string", "task": "string" }}
  ]
}}

Rules:
- Budget breakdown amounts should add up to roughly the total budget.
- Give realistic, city-specific suggestions (general types, not fake business names).
- Keep checklist to 5 items and timeline to 5 items.
- No markdown, no extra text — JSON only.
"""


def _generate_mock_plan(event: EventInput) -> GeneratedPlan:
    """Fallback plan when AI is unavailable."""
    venue_budget = round(event.budget * 0.4, 2)
    catering_budget = round(event.budget * 0.35, 2)
    decor_budget = round(event.budget * 0.15, 2)
    misc_budget = round(event.budget * 0.1, 2)

    setting = event.indoor_outdoor.lower()
    venue_suffix = "garden venues" if "out" in setting else "event halls"

    return GeneratedPlan(
        event_summary=(
            f"A {event.vibe.lower()} {event.event_type.lower()} for "
            f"{event.guest_count} guests in {event.city} on {event.date}. "
            f"Budget: ${event.budget:,.0f}. Food preference: {event.food_preferences}."
        ),
        venue_ideas=[
            f"{event.city} {venue_suffix} with space for {event.guest_count} guests",
            f"Boutique {setting} venue matching a {event.vibe.lower()} vibe",
            f"Community space in {event.city} with flexible layout options",
        ],
        vendor_suggestions=[
            f"Caterer specializing in {event.food_preferences.lower()}",
            "Local photographer for event coverage",
            "DJ or live band based on guest count and vibe",
            "Decorator aligned with your theme and budget",
        ],
        budget_breakdown=[
            BudgetItem(
                category="Venue",
                amount=venue_budget,
                notes=f"Estimated for {setting} options in {event.city}",
            ),
            BudgetItem(
                category="Catering",
                amount=catering_budget,
                notes=f"Covers {event.guest_count} guests with {event.food_preferences.lower()}",
            ),
            BudgetItem(
                category="Decor",
                amount=decor_budget,
                notes=f"Supports a {event.vibe.lower()} atmosphere",
            ),
            BudgetItem(
                category="Miscellaneous",
                amount=misc_budget,
                notes="Invitations, tips, and small last-minute items",
            ),
        ],
        checklist=[
            "Confirm guest count and send save-the-dates",
            "Shortlist and visit top venue options",
            "Book caterer and finalize menu tasting",
            "Confirm vendors and payment schedules",
            "Create day-of run sheet and assign helpers",
        ],
        timeline=[
            TimelineItem(when="8 weeks before", task="Finalize guest list and budget"),
            TimelineItem(when="6 weeks before", task="Book venue and key vendors"),
            TimelineItem(when="3 weeks before", task="Confirm menu, decor, and timeline"),
            TimelineItem(when="1 week before", task="Final headcount and vendor check-ins"),
            TimelineItem(when="Event day", task="Setup, welcome guests, and enjoy"),
        ],
    )


def _generate_ai_plan(event: EventInput) -> GeneratedPlan:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Add it to backend/.env")

    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You return structured event plans as JSON only.",
            },
            {"role": "user", "content": _build_prompt(event)},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("AI returned an empty response")

    data = json.loads(content)
    return GeneratedPlan.model_validate(data)


def generate_plan(event: EventInput) -> GeneratedPlan:
    use_mock = os.getenv("USE_MOCK_PLAN", "").lower() in {"1", "true", "yes"}

    if use_mock:
        return _generate_mock_plan(event)

    try:
        return _generate_ai_plan(event)
    except Exception:
        return _generate_mock_plan(event)
