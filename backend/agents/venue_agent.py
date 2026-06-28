from schemas.event import EventInput
from agents.llm import call_json_llm

def _format_researched_venues(venues : list[dict]) -> str:
    if not venues:
        return "No live venue data available. Suggest plausible options for the city."
    
    lines = []
    for v in venues : 
        address = v.get("address","")
        if address:
            lines.append(f"- {v['name']} ({address})")
        else:
            lines.append(f"- {v['name']}")

    return "\n".join(lines)


def run_venue_agent(
        event: EventInput,
        researched_venues: list[dict] | None=None,
    ) -> dict:
         venue_context = _format_researched_venues(researched_venues or [])
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

Real venues found for this city (use these when possible):
{venue_context}

Return ONLY valid JSON:
{{
  "event_summary": "string",
  "venue_ideas": ["string", "string", "string"]
}}

Rules:
- Include city, date, guest count, and vibe in event_summary.
- Pick 3 venues from the list above when possible; use real names and addresses.
- Match indoor/outdoor preference and vibe.
- If no live data, suggest 3 realistic options for the city.
- JSON only, no markdown.
"""
         return call_json_llm(system="You return JSON only for venue planning.", user=prompt)