import os
import httpx

from schemas.event import EventInput

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = "places.displayName, places.formattedAddress"
DEFAULT_LIMIT = 8

def lookup_venues(event : EventInput, limit : int=DEFAULT_LIMIT) -> list[dict]:
    api_key = os.get_env("GOOGLE_PLACES_API_KEY")
    if not api_key:
        return []
    
    query = f"event venues in {event.city}"
    headers = {
        "Content-Type" : "application/json",
        "X-Goog-Api-Key" : api_key,
        "X-Goog-Field-Mask" : FIELD_MASK

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
        display_name = place.get("displayName", {})
        name = display_name.get("text")
        address = place.get("formattedAddress")
        if not name:
            continue
        venues.append({
            "name" : name,
            "address" : address,
            "source" : "google"
        })

    return venues