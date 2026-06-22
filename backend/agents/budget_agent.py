from schemas.event import EventInput
from agents.llm import call_json_llm

def run_budget_agent(event:EventInput)->dict:
    prompt =  f"""
You are a budget specialist for event planning.

Event details:
- Event type: {event.event_type}
- City: {event.city}
- Date: {event.date}
- Guest count: {event.guest_count}
- Total budget: ${event.budget:,.0f}
- Vibe: {event.vibe}
- Food preferences: {event.food_preferences}
- Indoor/Outdoor: {event.indoor_outdoor}

Return ONLY valid JSON:
{{
"budget_breakdown":[
  {{"category":"string","amount":number, "notes":"string"}}
]
}}

Rules
- Use 4-5 categories (venue, catering, decor, entertainment, misc).
- Amounts must add up to roughly ${event.budget:,.0f}.
- JSON only, no markdown.
"""
    
    return call_json_llm(system="You only return JSON for budget breakdown",
                         user=prompt)




