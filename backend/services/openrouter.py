import httpx
import asyncio
import json
import logging
import base64
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8000",
    "X-Title": "XAUUSD Analyst",
}

MAX_RETRIES = 2
RETRY_DELAY = 3  # seconds


async def call_llm(
    prompt: str,
    system: str = "",
    model: str = "openai/gpt-4.1-nano",
    temperature: float = 0.3,
    max_tokens: int = 2000,
    timeout: float = 120.0,
) -> str:
    """Call an LLM via OpenRouter — text only. Retries on timeout."""
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

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(OPENROUTER_BASE, headers=HEADERS, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.ReadTimeout as e:
            last_error = e
            logger.warning("call_llm timeout (attempt %d/%d, model=%s)", attempt, MAX_RETRIES, model)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)

    raise last_error



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
        logger.error("Failed to parse JSON: %s. Raw output was: %s", e, raw)
        raise
