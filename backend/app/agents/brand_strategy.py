"""
Agent 4 – Brand Strategy Agent
Synthesizes idea discovery, market research, and competitor analysis
into a coherent brand strategy.
"""
import json
from app.utils.llm import call_llm
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are a world-class brand strategist.
Given the idea analysis, market research, and competitor analysis, create a comprehensive brand strategy.

Return a JSON object with EXACTLY these keys:
{
  "brand_mission": "The brand's mission statement",
  "brand_vision": "The brand's vision for the future",
  "brand_values": ["value1", "value2", "value3", "value4", "value5"],
  "brand_personality": {
    "archetype": "e.g. The Innovator, The Caregiver",
    "tone_of_voice": "e.g. professional yet approachable",
    "traits": ["trait1", "trait2", "trait3"]
  },
  "positioning_statement": "A concise positioning statement",
  "unique_selling_proposition": "The core USP",
  "target_segments": [
    {
      "segment_name": "Name",
      "description": "Description",
      "priority": "primary | secondary"
    }
  ],
  "brand_promise": "What the brand promises to its customers",
  "emotional_benefits": ["benefit1", "benefit2", "benefit3"],
  "functional_benefits": ["benefit1", "benefit2", "benefit3"]
}

Return ONLY valid JSON, no markdown formatting."""


async def run(
    idea_data: dict,
    market_data: dict,
    competitor_data: dict,
) -> AgentResult:
    """Execute the Brand Strategy Agent."""
    user_prompt = (
        f"IDEA ANALYSIS:\n{json.dumps(idea_data, indent=2)}\n\n"
        f"MARKET RESEARCH:\n{json.dumps(market_data, indent=2)}\n\n"
        f"COMPETITOR ANALYSIS:\n{json.dumps(competitor_data, indent=2)}\n\n"
        f"Based on ALL the above inputs, create a comprehensive brand strategy."
    )

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)

    personality = data.get("brand_personality", {})
    explanation = (
        f"A comprehensive brand strategy has been developed. "
        f"The brand archetype is '{personality.get('archetype', 'The Innovator')}' "
        f"with a {personality.get('tone_of_voice', 'professional')} tone. "
        f"Core values: {', '.join(data.get('brand_values', [])[:4])}. "
        f"The positioning statement: {data.get('positioning_statement', 'N/A')[:100]}. "
        f"USP: {data.get('unique_selling_proposition', 'N/A')[:100]}. "
        f"The strategy targets {len(data.get('target_segments', []))} market segments."
    )

    return AgentResult(data=data, explanation=explanation)
