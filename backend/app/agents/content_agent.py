"""
Agent 8 – Brand Content Agent
Generates brand copy: elevator pitch, about section, social media bios,
key messaging pillars, and call-to-action phrases.
"""
import json
from app.utils.llm import call_llm
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are an expert brand copywriter and content strategist.
Given the brand strategy, name, and design direction, create compelling brand content.

Return a JSON object with EXACTLY these keys:
{
  "elevator_pitch": "A 2-3 sentence elevator pitch",
  "about_section": "A 4-5 sentence about section for the website",
  "mission_statement_extended": "An extended mission statement (3-4 sentences)",
  "social_media_bios": {
    "twitter": "280 character max bio",
    "instagram": "150 character max bio",
    "linkedin": "Professional bio (2-3 sentences)"
  },
  "key_messaging_pillars": [
    {
      "pillar": "Pillar Name",
      "headline": "Compelling headline",
      "description": "Supporting description"
    }
  ],
  "call_to_action_phrases": ["CTA1", "CTA2", "CTA3", "CTA4"],
  "brand_hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
  "email_signature_tagline": "Tagline for email signatures"
}

Return ONLY valid JSON, no markdown formatting."""


async def run(
    strategy_data: dict,
    naming_data: dict,
    design_data: dict,
    feedback: str | None = None,
) -> AgentResult:
    """Execute the Brand Content Agent."""
    feedback_clause = ""
    if feedback:
        feedback_clause = f"\n\nUSER FEEDBACK: {feedback}\nAdjust the content based on this feedback."

    user_prompt = (
        f"BRAND STRATEGY:\n{json.dumps(strategy_data, indent=2)}\n\n"
        f"BRAND NAME: {naming_data.get('brand_name', 'Brand')}\n"
        f"TAGLINE: {naming_data.get('tagline', '')}\n\n"
        f"DESIGN DIRECTION:\n{json.dumps(design_data, indent=2)}\n\n"
        f"Create compelling brand content for all channels.{feedback_clause}"
    )

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.8,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)

    pillars = data.get("key_messaging_pillars", [])
    explanation = (
        f"Brand content has been crafted for '{naming_data.get('brand_name', 'the brand')}'. "
        f"Elevator pitch: '{data.get('elevator_pitch', 'N/A')[:80]}...' "
        f"Content includes bios for Twitter, Instagram, and LinkedIn. "
        f"{len(pillars)} key messaging pillars have been defined. "
        f"Call-to-action phrases: {', '.join(data.get('call_to_action_phrases', [])[:3])}. "
        f"Brand hashtags: {', '.join(data.get('brand_hashtags', [])[:3])}. "
        f"All content aligns with the brand's tone of voice and strategy."
    )

    return AgentResult(data=data, explanation=explanation)
