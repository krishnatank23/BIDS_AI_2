"""
Agent 2 – Market Research Agent
Uses LLM + web search to gather market insights.
"""
import json
from app.utils.llm import call_llm
from app.utils.search import web_search
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are an expert market research analyst.
Given a refined business idea and web search results, produce a comprehensive market analysis.

Return a JSON object with EXACTLY these keys:
{
  "market_size": "Estimated market size and growth rate",
  "market_trends": ["trend1", "trend2", "trend3", "trend4"],
  "target_demographics": {
    "age_range": "e.g. 25-45",
    "income_level": "e.g. middle to high",
    "interests": ["interest1", "interest2"],
    "behavior_patterns": ["pattern1", "pattern2"]
  },
  "market_gaps": ["gap1", "gap2", "gap3"],
  "entry_barriers": ["barrier1", "barrier2"],
  "growth_opportunities": ["opportunity1", "opportunity2", "opportunity3"],
  "key_sources": ["source_title1", "source_title2"]
}

Return ONLY valid JSON, no markdown formatting."""


async def run(idea_data: dict) -> AgentResult:
    """Execute the Market Research Agent."""
    refined_idea = idea_data.get("refined_idea", "")
    industry = idea_data.get("industry_category", "")

    # Perform web searches
    search_queries = [
        f"{industry} market size trends 2024 2025",
        f"{refined_idea[:80]} target audience demographics",
        f"{industry} market opportunities gaps",
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
        f"Based on the idea and the search results above, produce a market research analysis."
    )

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.5,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)

    explanation = (
        f"Market research has been conducted for the {industry} sector. "
        f"The estimated market is {data.get('market_size', 'substantial')}. "
        f"Key trends include {', '.join(data.get('market_trends', [])[:3])}. "
        f"Target demographics span {data.get('target_demographics', {}).get('age_range', 'various')} age groups. "
        f"Notable market gaps were identified: {', '.join(data.get('market_gaps', [])[:2])}. "
        f"Growth opportunities exist in {', '.join(data.get('growth_opportunities', [])[:2])}. "
        f"Analysis was informed by {len(all_results)} web sources."
    )

    return AgentResult(data=data, explanation=explanation)
