from schemas.event import EventInput
from agents.llm import call_json_llm

def run_details_agent(event: EventInput) -> dict:
    prompt = f"""
You are a vendor and logistics specialist for event planning.
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
  "vendor_suggestions": ["string", "string", "string", "string"],
  "checklist": ["string", "string", "string", "string", "string"],
  "timeline": [
    {{ "when": "string", "task": "string" }}
  ]
}}
Rules:
- 4 vendor suggestions (catering, photo, music, decor — match food + vibe).
- 5 checklist items.
- 5 timeline items from "8 weeks before" to "Event day".
- Mention event date ({event.date}) in at least one timeline item.
- JSON only, no markdown.
"""
    
    return call_json_llm(
        system="You return JSON only for vendors, checklist, and timeline.",
        user=prompt,
    )