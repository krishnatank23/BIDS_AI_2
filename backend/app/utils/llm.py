"""
LLM utility – uses Groq API with Llama 3.3 70B model.
Provides a single `call_llm` coroutine used by every agent.
"""
import os
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    response_format: dict | None = None,
) -> str:
    """Send a chat completion request to Groq and return the assistant message text."""
    kwargs: dict = {
        "model": _MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format:
        kwargs["response_format"] = response_format

    response = await _client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""
