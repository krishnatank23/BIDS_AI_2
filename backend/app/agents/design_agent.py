"""
Agent 6 – Design Intelligence Agent
Suggests visual identity: color palettes, typography, styling trends,
and references competitor designs via image search.
"""
import json
from app.utils.llm import call_llm
from app.utils.image_search import image_search
from app.schemas.brand_schema import AgentResult


SYSTEM_PROMPT = """You are an expert brand design strategist and visual identity specialist.
Given the brand strategy, brand name, and visual trend research, suggest a complete design direction.

Return a JSON object with EXACTLY these keys:
{
  "design_style": "e.g. minimalist modern, bold and vibrant, elegant luxury",
  "color_palette": {
    "primary": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Main brand color"},
    "secondary": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Supporting color"},
    "accent": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Call-to-action, highlights"},
    "neutral_dark": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Text, headings"},
    "neutral_light": {"hex": "#XXXXXX", "name": "Color Name", "usage": "Backgrounds"}
  },
  "typography": {
    "heading_font": "Font Name (e.g. Montserrat, Playfair Display)",
    "body_font": "Font Name (e.g. Inter, Open Sans)",
    "accent_font": "Font Name (optional, for special elements)"
  },
  "design_trends": ["trend1", "trend2", "trend3"],
  "mood_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
  "logo_direction": "Description of recommended logo style",
  "imagery_style": "Description of photography / illustration style",
  "competitor_design_references": ["reference1", "reference2"]
}

Return ONLY valid JSON, no markdown formatting."""


async def run(
    strategy_data: dict,
    naming_data: dict,
    feedback: str | None = None,
) -> AgentResult:
    """Execute the Design Intelligence Agent."""
    brand_name = naming_data.get("brand_name", "")
    industry = strategy_data.get("brand_personality", {}).get("archetype", "")

    # Gather visual trends via image search
    search_queries = [
        f"{brand_name} brand design inspiration",
        f"{industry} modern logo design trends 2024",
        f"premium brand identity design {strategy_data.get('brand_values', ['innovative'])[0]}",
    ]

    image_refs = []
    for q in search_queries:
        imgs = await image_search(q, num_results=3)
        image_refs.extend(imgs)

    image_context = "\n".join(
        f"- {img['title']} ({img['imageUrl']})" for img in image_refs[:8]
    )

    feedback_clause = ""
    if feedback:
        feedback_clause = f"\n\nUSER FEEDBACK FOR REDESIGN: {feedback}\nAdjust the design direction based on this feedback."

    user_prompt = (
        f"BRAND STRATEGY:\n{json.dumps(strategy_data, indent=2)}\n\n"
        f"BRAND NAME: {brand_name}\n\n"
        f"VISUAL TREND REFERENCES:\n{image_context}\n\n"
        f"Create a complete design direction for this brand.{feedback_clause}"
    )

    raw = await call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    data = json.loads(raw)
    data["image_references"] = image_refs[:6]

    palette = data.get("color_palette", {})
    primary_hex = palette.get("primary", {}).get("hex", "N/A")
    explanation = (
        f"Design direction established: '{data.get('design_style', 'modern')}' style. "
        f"Primary color is {palette.get('primary', {}).get('name', 'N/A')} ({primary_hex}). "
        f"Typography pairs {data.get('typography', {}).get('heading_font', 'N/A')} headers "
        f"with {data.get('typography', {}).get('body_font', 'N/A')} body text. "
        f"Current design trends applied: {', '.join(data.get('design_trends', [])[:3])}. "
        f"Logo direction: {data.get('logo_direction', 'N/A')[:80]}. "
        f"{len(image_refs)} competitor/trend design references were analyzed."
    )

    return AgentResult(data=data, explanation=explanation)
