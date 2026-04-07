"""
Chart Vision Agent — accepts a chart screenshot and returns pattern analysis.
Uses Gemini Pro Vision via OpenRouter.
"""
import logging
from models.schemas import VisionAnalysis
from services.openrouter import call_gemini_vision, parse_json_response

logger = logging.getLogger(__name__)

VISION_PROMPT = """You are an expert XAUUSD chart analyst. Analyze this trading chart screenshot carefully.

Identify:
1. Chart patterns (Head & Shoulders, Double Top/Bottom, Triangle, Wedge, Flag, Channel, etc.)
2. Trend direction and structure (HH/HL for uptrend, LH/LL for downtrend)
3. Key price levels visible (support, resistance, previous highs/lows)
4. Any candlestick patterns at key levels
5. A trade suggestion based on what you see

Return ONLY this JSON (no markdown, no extra text):
{
  "patterns_found": ["pattern 1", "pattern 2"],
  "trend_visible": "string describing the trend structure clearly",
  "key_levels": ["Level 1: $XXXX — description", "Level 2: $XXXX — description"],
  "trade_suggestion": "BUY | SELL | WAIT — with brief reason",
  "confidence": integer 0-100,
  "detailed_analysis": "3-5 sentence detailed analysis of what you see on the chart, referencing specific price structure, patterns, and what the next likely move is"
}

Rules:
- patterns_found: list all visible patterns, or ["No clear pattern"] if none
- key_levels: list 2-4 important levels visible on the chart
- confidence: be honest — blurry or unclear charts get lower confidence
- detailed_analysis: be specific and actionable"""


async def analyze_chart_image(image_bytes: bytes, media_type: str = "image/png") -> VisionAnalysis:
    try:
        raw = await call_gemini_vision(
            prompt=VISION_PROMPT,
            image_bytes=image_bytes,
            media_type=media_type,
            model="google/gemini-2.5-pro",
        )
        data = parse_json_response(raw)
        return VisionAnalysis(**data)

    except Exception as e:
        logger.error("Vision agent failed: %s", e)
        return VisionAnalysis(
            patterns_found=["Analysis failed"],
            trend_visible="Unable to analyze chart.",
            key_levels=[],
            trade_suggestion="WAIT — analysis unavailable",
            confidence=0,
            detailed_analysis=f"Chart vision analysis failed: {str(e)}",
        )
