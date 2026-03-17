"""
Agent 9 – Brand Guidelines Agent
Synthesizes all outputs into a comprehensive brand guidelines document.
"""
import json
from app.utils.llm import call_llm
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are an expert brand identity consultant.
Given ALL the brand identity elements, create comprehensive brand guidelines.

Return a JSON object with EXACTLY these keys:
{
  "guidelines_version": "1.0",
  "brand_overview": {
    "mission": "Mission statement",
    "vision": "Vision statement",
    "values": ["value1", "value2"]
  },
  "logo_usage": {
    "primary_usage": "How to use the primary logo",
    "minimum_size": "Minimum size requirements",
    "clear_space": "Clear space requirements",
    "dont_rules": ["don't rule 1", "don't rule 2", "don't rule 3"]
  },
  "color_guidelines": {
    "primary_colors": [{"name": "Name", "hex": "#XXXXXX", "rgb": "R, G, B", "usage": "When to use"}],
    "secondary_colors": [{"name": "Name", "hex": "#XXXXXX", "rgb": "R, G, B", "usage": "When to use"}],
    "color_combinations": ["combination1", "combination2"]
  },
  "typography_guidelines": {
    "primary_typeface": "Font name and usage",
    "secondary_typeface": "Font name and usage",
    "hierarchy": {
      "h1": "Size and weight",
      "h2": "Size and weight",
      "body": "Size and weight"
    }
  },
  "voice_and_tone": {
    "personality": "Brand personality description",
    "dos": ["do1", "do2", "do3"],
    "donts": ["don't1", "don't2", "don't3"],
    "example_phrases": ["phrase1", "phrase2"]
  },
  "imagery_guidelines": {
    "photography_style": "Description",
    "illustration_style": "Description",
    "icon_style": "Description"
  },
  "digital_guidelines": {
    "website_style": "Web design guidance",
    "social_media": "Social media guidelines",
    "email": "Email design guidelines"
  }
}

Return ONLY valid JSON, no markdown formatting."""


async def run(
    strategy_data: dict,
    naming_data: dict,
    design_data: dict,
    content_data: dict,
) -> AgentResult:
    """Execute the Brand Guidelines Agent."""
    user_prompt = (
        f"BRAND STRATEGY:\n{json.dumps(strategy_data, indent=2)}\n\n"
        f"BRAND NAME: {naming_data.get('brand_name', 'Brand')}\n"
        f"TAGLINE: {naming_data.get('tagline', '')}\n\n"
        f"DESIGN DIRECTION:\n{json.dumps(design_data, indent=2)}\n\n"
        f"BRAND CONTENT:\n{json.dumps(content_data, indent=2)}\n\n"
        f"Create comprehensive brand guidelines that cover all aspects of this brand identity."
    )

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.6,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)

    logo = data.get("logo_usage", {})
    explanation = (
        f"Comprehensive brand guidelines v{data.get('guidelines_version', '1.0')} have been created. "
        f"The guide covers logo usage ({len(logo.get('dont_rules', []))} don't rules), "
        f"color system ({len(data.get('color_guidelines', {}).get('primary_colors', []))} primary colors), "
        f"typography hierarchy, voice & tone guidelines, "
        f"imagery direction, and digital application standards. "
        f"These guidelines ensure brand consistency across all touchpoints. "
        f"The document is ready for team distribution and client handoff."
    )

    return AgentResult(data=data, explanation=explanation)
