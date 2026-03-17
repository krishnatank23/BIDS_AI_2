"""
Agent 7 – Logo Generation Agent
Generates 2-3 logo variations using the HuggingFace Inference API (Stable Diffusion).
Falls back to placeholder SVGs if the API key is not configured.
"""
import os
import io
import base64
import uuid
from pathlib import Path

import httpx
from dotenv import load_dotenv

from app.schemas.brand_schema import AgentResult

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

LOGO_DIR = Path("generated_logos")
LOGO_DIR.mkdir(exist_ok=True)

# Different style variations for logo generation
LOGO_STYLES = [
    {
        "name": "Modern Minimalist",
        "modifier": "minimalist geometric shapes, very simple, clean lines, sans-serif inspired",
    },
    {
        "name": "Premium Bold",
        "modifier": "bold and striking design, luxury aesthetic, elegant curves, sophisticated",
    },
    {
        "name": "Dynamic Creative",
        "modifier": "creative abstract, dynamic movement, playful yet professional, trendy",
    },
]


def _build_prompt(naming_data: dict, design_data: dict, style_variant: dict, feedback: str | None = None) -> str:
    """Build a Stable Diffusion prompt from design intelligence with style variation."""
    brand_name = naming_data.get("brand_name", "Brand")
    style = design_data.get("design_style", "modern minimalist")
    palette = design_data.get("color_palette", {})
    primary_color = palette.get("primary", {}).get("name", "blue")
    logo_dir = design_data.get("logo_direction", "clean symbol")
    mood = ", ".join(design_data.get("mood_keywords", ["professional", "clean"])[:3])

    prompt = (
        f"Professional logo design for '{brand_name}', {style_variant['modifier']}, "
        f"{logo_dir}, {primary_color} color scheme, {mood}, "
        f"vector art, white background, high quality, brand identity, "
        f"professional graphic design, no text, icon only"
    )

    if feedback:
        prompt += f", {feedback}"

    return prompt


async def run(
    naming_data: dict,
    design_data: dict,
    feedback: str | None = None,
) -> AgentResult:
    """Execute the Logo Generation Agent – generates 2-3 variations."""
    logos = []

    for idx, style_variant in enumerate(LOGO_STYLES[:3]):  # Generate up to 3 variations
        prompt = _build_prompt(naming_data, design_data, style_variant, feedback)
        logo_id = str(uuid.uuid4())[:8]
        filename = f"logo_{logo_id}.png"
        filepath = LOGO_DIR / filename

        logo_base64 = None
        generation_method = "placeholder"

        # Try to generate via HuggingFace
        if HF_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {HF_API_KEY}"}
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5,
                        "width": 512,
                        "height": 512,
                    },
                }

                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(HF_API_URL, json=payload, headers=headers)
                    resp.raise_for_status()

                    image_bytes = resp.content
                    filepath.write_bytes(image_bytes)
                    logo_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    generation_method = "huggingface_diffusion"

            except Exception as e:
                generation_method = f"fallback (HF error: {str(e)[:50]})"

        # Fallback to placeholder SVG
        if not logo_base64:
            brand_name = naming_data.get("brand_name", "B")
            primary = design_data.get("color_palette", {}).get("primary", {}).get("hex", "#4A90D9")
            accent = design_data.get("color_palette", {}).get("accent", {}).get("hex", "#E74C3C")

            # Different SVG designs for each variation
            if idx == 0:  # Minimalist
                svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="white"/>
  <circle cx="256" cy="256" r="140" fill="none" stroke="{primary}" stroke-width="20"/>
  <circle cx="256" cy="256" r="70" fill="{primary}" opacity="0.6"/>
</svg>"""
            elif idx == 1:  # Bold
                svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="white"/>
  <rect x="120" y="120" width="272" height="272" fill="{primary}" rx="20"/>
  <circle cx="256" cy="256" r="80" fill="{accent}"/>
</svg>"""
            else:  # Creative
                svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="white"/>
  <path d="M 256 100 L 380 200 L 340 340 L 170 340 L 130 200 Z" fill="{primary}"/>
  <circle cx="256" cy="220" r="50" fill="{accent}"/>
</svg>"""

            svg_bytes = svg.encode("utf-8")
            filepath = filepath.with_suffix(".svg")
            filepath.write_bytes(svg_bytes)
            logo_base64 = base64.b64encode(svg_bytes).decode("utf-8")

        logos.append({
            "variant_name": style_variant["name"],
            "logo_base64": logo_base64,
            "logo_file": str(filepath),
            "generation_prompt": prompt,
            "generation_method": generation_method,
            "format": filepath.suffix.lstrip("."),
        })

    data = {
        "logos": logos,
        "total_variations": len(logos),
        "selected_index": 0,
    }

    explanation = (
        f"Generated {len(logos)} logo variations for '{naming_data.get('brand_name', 'Brand')}': "
        f"{', '.join([l['variant_name'] for l in logos])}. "
        f"Each variation represents a different design direction. "
        f"Users can preview all options and regenerate individual variations with feedback. "
        f"The designs follow the '{design_data.get('design_style', 'modern')}' strategy."
    )

    return AgentResult(data=data, explanation=explanation)
