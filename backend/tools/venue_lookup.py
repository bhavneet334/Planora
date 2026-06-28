import os
import httpx

from schemas.event import EventInput

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = "places.displayName,places.formattedAddress"
DEFAULT_LIMIT = 10

def _budget_phrase(budget: float, guest_count:int) ->str:
    per_guest = budget/max(guest_count,1)
    if per_guest >= 400 or budget >= 10000:
        return "luxury upscale"
    if per_guest >= 200 or budget >= 5000:
        return "upscale"
    return "affordable" 

def _build_places_query(event : EventInput) -> str:
    setting = event.indoor_outdoor.lower()
    if "out" in setting:
        setting_phrase = "garden patio rooftop outdoor"
    elif "in" in setting:
        setting_phrase = "indoor banquet hall loft"
    else:
        setting_phrase = setting

    budget_phrase = _budget_phrase(event.budget, event.guest_count)

    return (
        f"{event.vibe.lower()} {budget_phrase} {setting_phrase} "
        f"{event.event_type.lower()} venues for {event.guest_count} guests in {event.city}"
    )

def lookup_venues(event : EventInput, limit : int=DEFAULT_LIMIT) -> list[dict]:
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        return []
    
    query = _build_places_query(event)
    headers = {
        "Content-Type" : "application/json",
        "X-Goog-Api-Key" : api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    body = {"textQuery":query, "maxResultCount":limit}

    try:
        response = httpx.post(PLACES_URL, headers=headers, json=body, timeout=10.0)
        response.raise_for_status()
    except(httpx.HTTPError, ValueError):
        return []
    
    places = response.json().get("places", [])
    venues : list[dict] = []

    for place in places:
        display_name = place.get("displayName") or {}
        if not isinstance(display_name, dict):
            continue
        name = display_name.get("text")
        if not name:
            continue
        venues.append({
            "name" : name,
            "address": place.get("formattedAddress") or "",
            "source" : "google"
        })

    return venues