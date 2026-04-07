"""
Fundamental Analysis Agent — sends news headlines to an LLM
and returns structured macro/sentiment analysis for gold.
"""
import logging
from typing import List

from models.schemas import NewsItem, FundamentalAnalysis
from services.openrouter import call_llm, parse_json_response

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior macro analyst specializing in Gold (XAUUSD) fundamentals.
You understand gold's relationship with: USD strength (DXY), real yields, geopolitical risk,
inflation expectations, Fed policy, and safe-haven flows.
You ALWAYS respond with valid JSON only — no markdown, no explanation outside the JSON."""


async def analyze_fundamental(news_items: List[NewsItem]) -> FundamentalAnalysis:
    if not news_items:
        headlines = "No recent news available."
    else:
        headlines = "\n".join(
            f"[{item.impact or 'LOW'}] [{item.source}] {item.title}"
            for item in news_items[:12]
        )

    prompt = f"""Analyze the following news headlines for their impact on XAUUSD (Gold) price.

RECENT HEADLINES:
{headlines}

Consider:
- USD/DXY strength/weakness (inverse correlation with gold)
- Federal Reserve policy signals (rate hikes = bearish gold)
- Geopolitical tensions (safe-haven demand = bullish gold)
- Inflation data (high inflation = bullish gold)
- Risk-on vs risk-off environment

Return ONLY this JSON structure (no markdown, no extra text):
{{
  "overall_sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
  "sentiment_score": float between -1.0 (max bearish) and 1.0 (max bullish),
  "dxy_outlook": "string — your assessment of USD direction and its gold impact",
  "macro_factors": [
    "factor 1 (bullish or bearish, explain briefly)",
    "factor 2",
    "factor 3"
  ],
  "news_summary": "2-3 sentence summary of the macro picture for gold right now"
}}

Rules:
- sentiment_score must be a float like 0.65 or -0.40
- macro_factors: exactly 3 items, each starting with BULLISH: or BEARISH: or NEUTRAL:
- news_summary: be concise and trader-focused"""

    try:
        raw = await call_llm(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            model="openai/gpt-4.1-nano",
            temperature=0.3,
        )
        data = parse_json_response(raw)
        return FundamentalAnalysis(**data)

    except Exception as e:
        logger.error("Fundamental agent failed: %s", e)
        return FundamentalAnalysis(
            overall_sentiment="NEUTRAL",
            sentiment_score=0.0,
            dxy_outlook="Analysis unavailable.",
            macro_factors=["Fundamental analysis failed — check logs."],
            news_summary="Unable to fetch fundamental analysis.",
        )
