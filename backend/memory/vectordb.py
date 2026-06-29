"""
Venue RAG cache — save and search venues in Supabase pgvector.

Flow:
  1. search_cached_venues — look in our database first
  2. save_venues — after Google returns venues, save them for next time
  3. _embed — turn text into numbers Google/Gemini understands for similarity search
"""

import os
import uuid
from typing import Any

from google import genai
from google.genai import types
from supabase import Client, create_client

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 1536
MIN_CACHE_HITS = 5


def _client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in backend/.env")
    return create_client(url, key)


def _embed(text: str) -> list[float]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY must be set in backend/.env (from AI Studio)")

    text = text.strip()
    if not text:
        raise ValueError("Cannot embed empty text")

    client = genai.Client(api_key=api_key)
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )

    embeddings = response.embeddings
    if not embeddings:
        raise ValueError("No embeddings returned from Google API")

    values = embeddings[0].values
    if values is None:
        raise ValueError("No embedding values returned from Google API")

    return list(values)


def _venue_id(city: str, name: str) -> str:
    """Unique id for each row in venue_facts."""
    slug = f"{city}_{name}".lower().replace(" ", "_")[:80]
    return f"venue_{slug}_{uuid.uuid4().hex[:8]}"


def search_cached_venues(
    query_text: str,
    city: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    try:
        embedding = _embed(query_text)
        result = _client().rpc(
            "match_venue_facts",
            {
                "query_embedding": embedding,
                "match_count": limit,
                "filter_city": city,
            },
        ).execute()

        venues: list[dict[str, Any]] = []
        for row in result.data or []: # type: ignore
            venues.append({
                "name": row["name"],
                "address": row.get("address") or "",
                "source": "cache",
            })
        return venues
    except Exception:
        return []


def save_venues(city: str, venues: list[dict[str, Any]]) -> None:
    """Save venues from Google into Supabase with embeddings."""
    if not venues:
        return

    rows: list[dict[str, Any]] = []
    for venue in venues:
        name = venue.get("name")
        if not name:
            continue
        address = venue.get("address") or ""
        body = f"{name} in {city}. {address}. Event venue."
        rows.append({
            "id": _venue_id(city, name),
            "city": city,
            "name": name,
            "address": address,
            "source": venue.get("source") or "google",
            "body": body,
            "embedding": _embed(body),
        })

    if rows:
        _client().table("venue_facts").upsert(rows).execute()
