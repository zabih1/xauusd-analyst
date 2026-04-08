"""
Scalper Synthesizer — combines M1/M5/M15/H1 timeframe analyses into a
single, actionable scalp trade plan.

Timeframe weighting for scalping decisions:
  H1  (20%) — bias filter only; counter-trend scalps are high risk
  M15 (30%) — trend context; must be aligned or at least neutral
  M5  (35%) — PRIMARY signal; this is where the scalp lives
  M1  (15%) — entry precision; fine-tune the exact entry candle
"""
import logging
from typing import Dict, Optional

from models.schemas import TimeframeAnalysis, ScalperTradeSetup
from services.openrouter import call_llm, parse_json_response

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the head scalp trader at a professional prop firm, specializing in XAUUSD.
You receive analysis from 4 dedicated timeframe agents and must produce ONE precise scalp trade plan.
You are decisive, capital-protective, and understand that in scalping, NOT trading is often the best trade.
You ALWAYS respond with valid JSON only — no markdown, no preamble."""


def _build_tf_summary(tf_results: Dict[str, Optional[TimeframeAnalysis]]) -> str:
    lines = []
    for tf in ["H1", "M15", "M5", "M1"]:
        res = tf_results.get(tf)
        if res is None:
            lines.append(f"[{tf}] — DATA UNAVAILABLE")
            continue
        lines.append(
            f"[{tf}] Trend:{res.trend} ({res.strength}) | "
            f"Signal:{res.scalp_signal} | Quality:{res.signal_quality}/100\n"
            f"      Momentum: {res.momentum}\n"
            f"      Entry Note: {res.entry_note}\n"
            f"      ⚠ Warning: {res.warning}\n"
            f"      Support: {res.support_levels} | Resistance: {res.resistance_levels}"
        )
    return "\n\n".join(lines)


def _signal_alignment(tf_results: Dict[str, Optional[TimeframeAnalysis]]) -> str:
    """Quick alignment check string for the LLM."""
    signals = {}
    for tf in ["H1", "M15", "M5", "M1"]:
        res = tf_results.get(tf)
        signals[tf] = res.scalp_signal if res else "N/A"

    buy_count  = sum(1 for s in signals.values() if s == "BUY")
    sell_count = sum(1 for s in signals.values() if s == "SELL")
    wait_count = sum(1 for s in signals.values() if s == "WAIT")

    if buy_count >= 3:
        alignment = "STRONG BUY ALIGNMENT"
    elif sell_count >= 3:
        alignment = "STRONG SELL ALIGNMENT"
    elif buy_count >= 2 and sell_count == 0:
        alignment = "MODERATE BUY"
    elif sell_count >= 2 and buy_count == 0:
        alignment = "MODERATE SELL"
    elif wait_count >= 2:
        alignment = "WAIT — multiple TFs say stand aside"
    else:
        alignment = "MIXED — conflicting signals"

    return f"H1:{signals['H1']} M15:{signals['M15']} M5:{signals['M5']} M1:{signals['M1']} → {alignment}"


async def synthesize_scalp(
    current_price: float,
    tf_results: Dict[str, Optional[TimeframeAnalysis]],
    session: str,
) -> ScalperTradeSetup:

    tf_summary = _build_tf_summary(tf_results)
    alignment  = _signal_alignment(tf_results)

    # Best timeframe for this scalp (M5 is default, but M1 if M5 unavailable)
    primary_tf = "M5"
    primary = tf_results.get("M5")
    if primary is None:
        primary_tf = "M1"
        primary = tf_results.get("M1")

    prompt = f"""Synthesize the following multi-timeframe analysis into ONE precise XAUUSD scalp trade plan.

CURRENT PRICE: ${current_price:.2f}
TRADING SESSION: {session}
SIGNAL ALIGNMENT: {alignment}

━━━ TIMEFRAME AGENT REPORTS ━━━
{tf_summary}

━━━ SCALPING RULES TO FOLLOW ━━━
1. H1 is the BIAS FILTER — never take a scalp strongly against H1 trend
2. M15 provides the TREND CONTEXT — scalp in M15 direction when possible
3. M5 is the PRIMARY SIGNAL — the entry setup must be visible on M5
4. M1 is for ENTRY PRECISION — fine-tune entry to the specific candle
5. If signals conflict across ≥2 timeframes, reduce confidence and widen SL
6. Scalp targets: TP1 = 10–25 pips, TP2 = 30–60 pips MAX
7. Stop loss: 8–20 pips for scalps (tight but not unrealistic)
8. If session is Asian, reduce position size and expect range-bound action

Return ONLY this JSON (no markdown):
{{
  "bias": "BUY" | "SELL" | "NEUTRAL",
  "primary_timeframe": "M5" | "M1" | "M15",
  "entry_low": float,
  "entry_high": float,
  "stop_loss": float,
  "take_profit_1": float,
  "take_profit_2": float,
  "risk_reward": float,
  "confidence": integer 0-100,
  "timeframe_alignment": "string — describe agreement/conflict across TFs in 1 sentence",
  "reasoning": "string — 3-4 sentences: what the MTF analysis shows and why this scalp makes sense",
  "invalidation": "string — specific price level or candle pattern that kills the setup",
  "scalp_notes": "string — practical execution tips: when to enter, what confirmation to wait for, session considerations",
  "do_not_trade_if": "string — list 2-3 conditions that would make you skip this trade entirely"
}}

Rules:
- entry_low/entry_high: the ideal zone to place a limit or watch for entry (small range, 3–8 pips)
- SL must be BELOW entry for BUY (above recent swing low), ABOVE for SELL (below recent swing high)
- TP1 must give at minimum 1:1 R:R, TP2 should be 1:2 or better
- confidence: be HONEST — conflicting TFs = 30–50, aligned TFs = 65–85, perfect setup = 85+
- If NEUTRAL: do NOT invent a trade — set confidence below 40 and explain why to wait"""

    try:
        raw = await call_llm(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            model="openai/gpt-4.1-nano",
            temperature=0.15,
            max_tokens=1500,
        )
        data = parse_json_response(raw)
        return ScalperTradeSetup(**data)

    except Exception as e:
        logger.error("Scalper synthesizer failed: %s", repr(e), exc_info=True)
        sl = current_price - 15.0
        tp1 = current_price + 15.0
        tp2 = current_price + 30.0
        return ScalperTradeSetup(
            bias="NEUTRAL",
            primary_timeframe="M5",
            entry_low=current_price - 2,
            entry_high=current_price + 2,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            risk_reward=1.0,
            confidence=0,
            timeframe_alignment="Analysis failed",
            reasoning="Synthesis failed — please retry manually.",
            invalidation="Analysis unavailable.",
            scalp_notes="Retry the analysis.",
            do_not_trade_if="Analysis is unavailable.",
        )