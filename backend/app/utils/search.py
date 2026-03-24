"""
Web search utility using DuckDuckGo (no API key required).
Uses the duckduckgo-search library.
"""
import asyncio
from duckduckgo_search import DDGS


# Keep DDGS and primp impersonation versions aligned to avoid noisy fallback warnings.
DDGS._impersonates = ("chrome_145",)


def _make_ddgs() -> DDGS:
    return DDGS()


async def web_search(query: str, num_results: int = 8) -> list[dict]:
    """
    Return a list of search result dicts with keys: title, link, snippet.
    Uses DuckDuckGo – no API key needed.
    """
    try:
        # duckduckgo-search is synchronous, so run in executor
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: _make_ddgs().text(query, max_results=num_results),
        )

        return [
            {
                "title": r.get("title", ""),
                "link": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in (results or [])[:num_results]
        ]
    except Exception as e:
        # Fallback if DuckDuckGo is temporarily unavailable
        return [
            {
                "title": f"[Search unavailable] for '{query}'",
                "link": "",
                "snippet": f"DuckDuckGo search temporarily unavailable: {str(e)[:80]}",
            }
        ]
