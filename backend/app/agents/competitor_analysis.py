"""
Agent 3 – Competitor Analysis Agent
Uses LLM + web search to identify and analyze competitors.
Runs IN PARALLEL with Market Research Agent.
"""
import json
from app.utils.llm import call_llm
from app.utils.search import web_search
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are an expert competitive intelligence analyst.
Given a refined business idea and web search results about competitors, produce a thorough competitor analysis.

Return a JSON object with EXACTLY these keys:
{
  "direct_competitors": [
    {
      "name": "Competitor Name",
      "description": "What they do",
      "strengths": ["strength1", "strength2"],
      "weaknesses": ["weakness1", "weakness2"],
      "estimated_market_share": "e.g. 15%",
      "website": "url or unknown"
    }
  ],
  "indirect_competitors": [
    {
      "name": "Competitor Name",
      "description": "How they overlap"
    }
  ],
  "competitive_advantages": ["advantage1", "advantage2", "advantage3"],
  "market_positioning_gaps": ["gap1", "gap2"],
  "recommended_positioning": "How to position against competitors",
  "threat_level": "low | medium | high"
}

Return ONLY valid JSON, no markdown formatting."""


async def run(idea_data: dict) -> AgentResult:
    """Execute the Competitor Analysis Agent."""
    refined_idea = idea_data.get("refined_idea", "")
    industry = idea_data.get("industry_category", "")

    search_queries = [
        f"{refined_idea[:80]} competitors",
        f"top companies in {industry} 2024 2025",
        f"{industry} startup competition landscape",
    ]

    all_results = []
    for q in search_queries:
        results = await web_search(q, num_results=5)
        all_results.extend(results)

    search_context = "\n".join(
        f"- {r['title']}: {r['snippet']}" for r in all_results
    )

    user_prompt = (
        f"Refined Idea: {refined_idea}\n"
        f"Industry: {industry}\n\n"
        f"Web Search Results:\n{search_context}\n\n"
        f"Based on the idea and search results, produce a comprehensive competitor analysis."
    )

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.5,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)

    direct = data.get("direct_competitors", [])
    explanation = (
        f"Competitor analysis identified {len(direct)} direct competitor(s) "
        f"in the {industry} space. "
        f"Key competitive advantages for this idea include: "
        f"{', '.join(data.get('competitive_advantages', [])[:3])}. "
        f"The overall threat level is assessed as {data.get('threat_level', 'medium')}. "
        f"Recommended positioning: {data.get('recommended_positioning', 'differentiate on innovation')}. "
        f"Market positioning gaps found: {', '.join(data.get('market_positioning_gaps', [])[:2])}. "
        f"Analysis informed by {len(all_results)} search results across multiple queries."
    )

    return AgentResult(data=data, explanation=explanation)
