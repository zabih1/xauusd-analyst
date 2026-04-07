"""
Technical Analysis Agent — sends OHLCV candles to an LLM
and returns structured technical analysis.
"""
import json
import logging
from typing import List

from models.schemas import Candle, TechnicalAnalysis
from services.openrouter import call_llm, parse_json_response

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert XAUUSD (Gold) technical analyst with 15+ years of experience.
You analyze multi-timeframe price action and produce precise, structured technical analysis.
You ALWAYS respond with valid JSON only — no markdown, no explanation outside the JSON."""

def _format_candles(candles: List[Candle], limit: int = 30) -> str:
    recent = candles[-limit:]
    rows = []
    for c in recent:
        rows.append(
            f"{c.time.strftime('%m-%d %H:%M')} O:{c.open} H:{c.high} L:{c.low} C:{c.close} V:{c.volume:.0f}"
        )
    return "\n".join(rows)


async def analyze_technical(candles_by_tf: dict) -> TechnicalAnalysis:
    """
    candles_by_tf: {"M15": [...], "H1": [...], "H4": [...], "D1": [...]}
    """
    sections = []
    for tf, candles in candles_by_tf.items():
        if candles:
            sections.append(f"=== {tf} CANDLES (last {min(len(candles),30)}) ===\n{_format_candles(candles)}")

    candle_data = "\n\n".join(sections) if sections else "No candle data available."

    prompt = f"""Analyze the following XAUUSD multi-timeframe OHLCV data and return a JSON object.

{candle_data}

Return ONLY this JSON structure (no markdown, no extra text):
{{
  "trend": "Bullish" | "Bearish" | "Ranging",
  "strength": "Strong" | "Moderate" | "Weak",
  "support_levels": [float, float, float],
  "resistance_levels": [float, float, float],
  "momentum": "string describing momentum (RSI-like assessment, volume analysis)",
  "key_observations": [
    "observation 1",
    "observation 2",
    "observation 3",
    "observation 4"
  ]
}}

Rules:
- support_levels and resistance_levels: provide exactly 3 price levels each, sorted ascending
- key_observations: exactly 4 concise bullet points about price action, patterns, structure
- momentum: one sentence about current momentum
- Be specific with price levels based on the actual candle data"""

    try:
        raw = await call_llm(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            model="openai/gpt-4.1-nano",
            temperature=0.2,
        )
        data = parse_json_response(raw)
        return TechnicalAnalysis(**data)

    except Exception as e:
        logger.error("Technical agent failed: %s", e)
        # return a safe fallback
        return TechnicalAnalysis(
            trend="Ranging",
            strength="Weak",
            support_levels=[0.0, 0.0, 0.0],
            resistance_levels=[0.0, 0.0, 0.0],
            momentum="Analysis unavailable.",
            key_observations=["Technical analysis failed — check logs."],
        )
