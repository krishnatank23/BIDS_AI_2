"""
Agent 5 – Brand Naming Agent
Generates brand name candidates with rationale, taglines, and optional domain availability.
"""
import json
from app.utils.llm import call_llm
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are an expert brand naming specialist.
Given the brand strategy, generate creative and memorable brand name options.

Return a JSON object with EXACTLY these keys:
{
  "brand_name": "The top recommended brand name",
  "tagline": "A catchy tagline for the brand",
  "name_candidates": [
    {
      "name": "Name Option",
      "rationale": "Why this name works",
      "style": "e.g. abstract, descriptive, compound",
      "domain_suggestion": "possible-domain.com"
    }
  ],
  "naming_strategy": "The approach used for naming",
  "brand_story_hook": "A one-sentence origin story or hook"
}

Provide at least 5 name candidates. Return ONLY valid JSON, no markdown formatting."""


async def run(strategy_data: dict) -> AgentResult:
    """Execute the Brand Naming Agent."""
    user_prompt = (
        f"BRAND STRATEGY:\n{json.dumps(strategy_data, indent=2)}\n\n"
        f"Based on this brand strategy, generate creative brand name options."
    )

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.9,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)

    candidates = data.get("name_candidates", [])
    explanation = (
        f"Brand naming analysis is complete. The top recommended name is "
        f"'{data.get('brand_name', 'N/A')}' with tagline '{data.get('tagline', 'N/A')}'. "
        f"A total of {len(candidates)} name candidates were generated using a "
        f"{data.get('naming_strategy', 'creative')} approach. "
        f"Name styles range from abstract to descriptive compound words. "
        f"Each candidate includes a domain suggestion for web presence. "
        f"Brand story hook: {data.get('brand_story_hook', 'N/A')[:120]}."
    )

    return AgentResult(data=data, explanation=explanation)
