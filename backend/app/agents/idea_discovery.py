"""
Agent 1 – Idea Discovery Agent
Refines and expands the raw user idea into a structured concept.
"""
import json
from app.utils.llm import call_llm
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are an expert business idea analyst and brand strategist.
Given a raw business idea, you must discover and expand it into a structured concept.

Return a JSON object with EXACTLY these keys:
{
  "refined_idea": "A clear, refined version of the original idea",
  "target_audience": "Primary and secondary target audiences",
  "value_proposition": "Core value proposition",
  "key_differentiators": ["differentiator1", "differentiator2", "differentiator3"],
  "industry_category": "The industry or category this falls under",
  "problem_solved": "The core problem this idea solves",
  "revenue_model": "Potential revenue model suggestions",
  "risk_factors": ["risk1", "risk2"]
}

Return ONLY valid JSON, no markdown formatting."""


async def run(idea: str) -> AgentResult:
    """Execute the Idea Discovery Agent."""
    user_prompt = f"Analyze and expand this business idea:\n\n{idea}"

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)

    explanation = (
        f"The idea '{idea[:60]}...' has been analyzed and refined. "
        f"The concept targets {data.get('target_audience', 'a broad audience')} "
        f"within the {data.get('industry_category', 'general')} industry. "
        f"The core value proposition centers on {data.get('value_proposition', 'delivering unique value')}. "
        f"Key differentiators include {', '.join(data.get('key_differentiators', [])[:3])}. "
        f"The idea primarily solves: {data.get('problem_solved', 'an identified market gap')}. "
        f"Potential revenue can be driven through {data.get('revenue_model', 'various channels')}."
    )

    return AgentResult(data=data, explanation=explanation)
