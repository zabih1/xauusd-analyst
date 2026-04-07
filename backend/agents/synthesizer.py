"""
Synthesizer Agent — the "head analyst" that takes technical + fundamental
analysis and produces a final, actionable trade plan.
"""
import logging

from models.schemas import TechnicalAnalysis, FundamentalAnalysis, TradeSetup
from services.openrouter import call_llm, parse_json_response

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a master XAUUSD trader and head analyst.
You receive technical and fundamental analysis from your team and synthesize them
into one precise, actionable trade plan.
You are decisive, risk-aware, and always protect capital first.
You ALWAYS respond with valid JSON only — no markdown, no preamble."""


async def synthesize(
    current_price: float,
    technical: TechnicalAnalysis,
    fundamental: FundamentalAnalysis,
    session: str,
) -> TradeSetup:

    prompt = f"""Synthesize the following analysis into a final XAUUSD trade plan.

CURRENT PRICE: ${current_price:.2f}
TRADING SESSION: {session}

TECHNICAL ANALYSIS:
- Trend: {technical.trend} ({technical.strength})
- Momentum: {technical.momentum}
- Support Levels: {technical.support_levels}
- Resistance Levels: {technical.resistance_levels}
- Key Observations:
{chr(10).join(f"  • {obs}" for obs in technical.key_observations)}

FUNDAMENTAL ANALYSIS:
- Sentiment: {fundamental.overall_sentiment} (score: {fundamental.sentiment_score:+.2f})
- DXY Outlook: {fundamental.dxy_outlook}
- Macro Factors:
{chr(10).join(f"  • {f}" for f in fundamental.macro_factors)}
- Summary: {fundamental.news_summary}

SESSION CONTEXT:
- Asian session: Low volatility, range-bound typical
- London session: High volatility, trend initiation likely
- New York session: High volume, major moves, news-driven
- Overlap (London/NY): Highest volatility window

Return ONLY this JSON (no markdown, no extra text):
{{
  "bias": "BUY" | "SELL" | "NEUTRAL",
  "entry_low": float,
  "entry_high": float,
  "stop_loss": float,
  "take_profit_1": float,
  "take_profit_2": float,
  "risk_reward": float,
  "confidence": integer 0-100,
  "reasoning": "3-4 sentence explanation of why this setup makes sense, referencing specific levels and confluence factors",
  "invalidation": "One clear sentence: what price action would invalidate this setup"
}}

Rules:
- entry_low/entry_high define the ideal entry ZONE (not a single price)
- stop_loss must be BELOW entry for BUY, ABOVE for SELL
- take_profit_1 is conservative (1:1 or better), take_profit_2 is extended target
- risk_reward calculated from midpoint of entry zone to TP1
- confidence: be honest — if signals conflict, confidence should be lower (40-60)
- If NEUTRAL bias: set entry zone around current price, SL/TP equidistant"""

    try:
        raw = await call_llm(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            model="openai/gpt-4.1-nano",
            temperature=0.2,
            max_tokens=1500,
        )
        data = parse_json_response(raw)
        return TradeSetup(**data)

    except Exception as e:
        logger.error("Synthesizer agent failed: %s", repr(e), exc_info=True)
        sl = current_price - 10.0
        tp1 = current_price + 10.0
        tp2 = current_price + 20.0
        return TradeSetup(
            bias="NEUTRAL",
            entry_low=current_price - 1,
            entry_high=current_price + 1,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            risk_reward=1.0,
            confidence=0,
            reasoning="Synthesis failed — please retry manually.",
            invalidation="Analysis unavailable.",
        )
