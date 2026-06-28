from schemas.event import EventInput
from tools.venue_lookup import lookup_venues

def run_venue_research(event: EventInput) -> list[dict]:
    return  lookup_venues(event)


