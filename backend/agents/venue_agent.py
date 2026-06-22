from schemas.event import EventInput
from agents.llm import call_json_llm


def run_venue_agent(event: EventInput) -> dict:
    prompt = f"""
You are a venue specialist for event planning.

Event details:
- Event type: {event.event_type}
- City: {event.city}
- Date: {event.date}
- Guest count: {event.guest_count}
- Budget: ${event.budget:,.0f}
- Vibe: {event.vibe}
- Food preferences: {event.food_preferences}
- Indoor/Outdoor: {event.indoor_outdoor}

Return ONLY valid JSON:
{{
  "event_summary": "string",
  "venue_ideas": ["string", "string", "string"]
}}

Rules:
- Include city, date, guest count, and vibe in event_summary.
- Suggest 3 realistic venues for the city and indoor/outdoor preference.
- Match the vibe (e.g. elegant → upscale options).
- JSON only, no markdown.
"""

    return call_json_llm(
        system="You return JSON only for venue planning.",
        user=prompt,
    )
