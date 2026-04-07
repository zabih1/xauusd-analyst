import httpx
import json
import base64
from typing import Optional
from config import settings

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8000",
    "X-Title": "XAUUSD Analyst",
}


async def call_llm(
    prompt: str,
    system: str = "",
    model: str = "openai/gpt-4.1-nano",
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> str:
    """Call an LLM via OpenRouter — text only."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENROUTER_BASE, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def call_llm_vision(
    prompt: str,
    image_bytes: bytes,
    media_type: str = "image/png",
    model: str = "google/gemini-2.5-flash-lite",
    temperature: float = 0.3,
) -> str:
    """Call a vision-capable LLM via OpenRouter — image + text."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_b64}"
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 2000,
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(OPENROUTER_BASE, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def parse_json_response(raw: str) -> dict:
    """Safely extract JSON from LLM response (strips markdown fences)."""
    raw = raw.strip()
    
    # Try to find JSON markdown block first
    import re
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if match:
        raw = match.group(1).strip()
    else:
        # Sometimes it might just have prefix/suffix text
        start_idx = raw.find("{")
        end_idx = raw.rfind("}")
        if start_idx != -1 and end_idx != -1:
            raw = raw[start_idx:end_idx+1]
            
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        import logging
        logging.getLogger(__name__).error("Failed to parse JSON: %s. Raw output was: %s", e, raw)
        raise
