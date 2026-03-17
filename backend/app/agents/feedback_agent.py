"""
Agent 11 – Feedback Agent
Interprets user feedback and determines which agent(s) to re-run
and how to modify the prompts.
"""
import json
from app.utils.llm import call_llm
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are a brand feedback interpreter.
A user has provided feedback about their brand identity and wants specific elements regenerated.

Analyze the feedback and determine:
1. Which agent(s) should be re-run
2. How to modify the instructions for each agent

The agents that can be regenerated are:
- "design_agent" (Agent 6): color palettes, typography, design style
- "logo_generator" (Agent 7): logo generation
- "content_agent" (Agent 8): brand copy, taglines, messaging

Return a JSON object with EXACTLY these keys:
{
  "agents_to_regenerate": ["agent_name1", "agent_name2"],
  "modifications": {
    "agent_name": "Specific instructions for how to modify the output"
  },
  "feedback_interpretation": "How you interpreted the user's feedback",
  "confidence": "high | medium | low"
}

Return ONLY valid JSON, no markdown formatting."""


REGENERATABLE_AGENTS = {"design_agent", "logo_generator", "content_agent"}


async def run(feedback: str, current_outputs: dict) -> AgentResult:
    """Execute the Feedback Agent to determine regeneration plan."""
    # Build context of current outputs (summaries only, not full data)
    context_summary = {}
    for agent_name in REGENERATABLE_AGENTS:
        output = current_outputs.get(agent_name, {})
        if isinstance(output, dict):
            context_summary[agent_name] = {
                k: str(v)[:200] for k, v in output.items() if k != "logo_base64"
            }

    user_prompt = (
        f"USER FEEDBACK: {feedback}\n\n"
        f"CURRENT OUTPUTS SUMMARY:\n{json.dumps(context_summary, indent=2)}\n\n"
        f"Analyze the feedback and determine what should be regenerated and how."
    )

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)

    # Validate agent names
    requested = data.get("agents_to_regenerate", [])
    data["agents_to_regenerate"] = [a for a in requested if a in REGENERATABLE_AGENTS]

    explanation = (
        f"Feedback analyzed: '{feedback[:80]}...' "
        f"Interpretation: {data.get('feedback_interpretation', 'N/A')[:100]}. "
        f"Confidence level: {data.get('confidence', 'medium')}. "
        f"Agents to regenerate: {', '.join(data.get('agents_to_regenerate', []))}. "
        f"Each agent will receive modified instructions based on the feedback. "
        f"The regeneration will create new versions while preserving previous outputs."
    )

    return AgentResult(data=data, explanation=explanation)
