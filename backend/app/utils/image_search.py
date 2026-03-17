"""
Image search utility using DuckDuckGo (no API key required).
Uses the duckduckgo-search library for image results.
"""
import asyncio
from duckduckgo_search import DDGS


async def image_search(query: str, num_results: int = 6) -> list[dict]:
    """Return list of image results with keys: title, imageUrl, link."""
    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: DDGS().images(query, max_results=num_results),
        )

        return [
            {
                "title": r.get("title", ""),
                "imageUrl": r.get("image", ""),
                "link": r.get("url", ""),
            }
            for r in (results or [])[:num_results]
        ]
    except Exception as e:
        return [
            {
                "title": f"[Image search unavailable] for '{query}'",
                "imageUrl": f"https://via.placeholder.com/400x300?text={query.replace(' ', '+')}",
                "link": "",
            }
        ]
