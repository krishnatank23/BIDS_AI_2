"""
Agent 7 – Logo Generation Agent
Generates logo using the HuggingFace Inference API (Stable Diffusion).
Falls back to a placeholder if the API key is not configured.
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


def _build_prompt(naming_data: dict, design_data: dict, feedback: str | None = None) -> str:
    """Build a Stable Diffusion prompt from design intelligence."""
    brand_name = naming_data.get("brand_name", "Brand")
    style = design_data.get("design_style", "modern minimalist")
    palette = design_data.get("color_palette", {})
    primary_color = palette.get("primary", {}).get("name", "blue")
    logo_dir = design_data.get("logo_direction", "clean symbol")
    mood = ", ".join(design_data.get("mood_keywords", ["professional", "clean"])[:4])

    prompt = (
        f"Professional logo design for '{brand_name}', {style} style, "
        f"{logo_dir}, {primary_color} color scheme, {mood}, "
        f"vector art, white background, high quality, minimal, brand identity, "
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
    """Execute the Logo Generation Agent."""
    prompt = _build_prompt(naming_data, design_data, feedback)
    logo_id = str(uuid.uuid4())[:8]
    filename = f"logo_{logo_id}.png"
    filepath = LOGO_DIR / filename

    logo_base64 = None
    generation_method = "placeholder"

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
            generation_method = f"fallback (HF error: {str(e)[:60]})"

    if not logo_base64:
        # Generate a placeholder SVG as fallback
        brand_name = naming_data.get("brand_name", "B")
        primary = design_data.get("color_palette", {}).get("primary", {}).get("hex", "#4A90D9")
        accent = design_data.get("color_palette", {}).get("accent", {}).get("hex", "#E74C3C")

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="white"/>
  <circle cx="256" cy="220" r="120" fill="{primary}" opacity="0.9"/>
  <circle cx="280" cy="240" r="60" fill="{accent}" opacity="0.7"/>
  <text x="256" y="420" font-family="Arial, sans-serif" font-size="48" font-weight="bold"
        fill="{primary}" text-anchor="middle">{brand_name[:12]}</text>
</svg>"""
        svg_bytes = svg.encode("utf-8")
        filepath = filepath.with_suffix(".svg")
        filepath.write_bytes(svg_bytes)
        logo_base64 = base64.b64encode(svg_bytes).decode("utf-8")

    data = {
        "logo_file": str(filepath),
        "logo_base64": logo_base64,
        "generation_prompt": prompt,
        "generation_method": generation_method,
        "dimensions": "512x512",
        "format": filepath.suffix.lstrip("."),
    }

    explanation = (
        f"Logo has been generated using {generation_method}. "
        f"The design follows the '{design_data.get('design_style', 'modern')}' direction. "
        f"Prompt used: '{prompt[:100]}...'. "
        f"Output saved to {filepath}. "
        f"The logo is 512x512 pixels in {filepath.suffix.lstrip('.')} format. "
        f"Use the regenerate feature with feedback like 'make it more minimal' to iterate."
    )

    return AgentResult(data=data, explanation=explanation)
