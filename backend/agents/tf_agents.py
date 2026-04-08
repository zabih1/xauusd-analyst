"""
Per-Timeframe Technical Analysis Agents — each timeframe gets its own LLM call
with a prompt tuned specifically for that timeframe's role in scalping.

Timeframe roles:
  M1  — entry timing, immediate momentum, micro-structure
  M5  — primary scalp signal, pattern confirmation, entry zone
  M15 — trend context for the scalp, S/R levels that matter
  H1  — higher-timeframe bias, do NOT trade against this
"""
import asyncio
import logging
from typing import List, Optional
from models.schemas import Candle, TimeframeAnalysis
from services.openrouter import call_llm, parse_json_response

logger = logging.getLogger(__name__)

# ── Shared base system prompt ─────────────────────────────────────────────────
_BASE_SYSTEM = """You are an elite XAUUSD scalping specialist with 15+ years experience.
You analyze price action for SHORT-TERM scalping opportunities (targets: 10–50 pips, hold time: 1–15 minutes).
You ALWAYS respond with valid JSON only — no markdown, no explanation outside the JSON.
Be concise, precise, and trader-focused."""


def _fmt(candles: List[Candle], limit: int = 40) -> str:
    recent = candles[-limit:]
    rows = [
        f"{c.time.strftime('%m-%d %H:%M')} O:{c.open:.2f} H:{c.high:.2f} L:{c.low:.2f} C:{c.close:.2f} V:{c.volume:.0f}"
        for c in recent
    ]
    return "\n".join(rows)


def _json_schema() -> str:
    return """{
  "trend": "Bullish" | "Bearish" | "Ranging",
  "strength": "Strong" | "Moderate" | "Weak",
  "support_levels": [float, float, float],
  "resistance_levels": [float, float, float],
  "momentum": "string — one sentence on current momentum",
  "scalp_signal": "BUY" | "SELL" | "WAIT",
  "signal_quality": integer 0-100,
  "key_observations": ["obs1", "obs2", "obs3", "obs4"],
  "entry_note": "string — specific entry trigger to watch for on this timeframe",
  "warning": "string — main risk or reason NOT to trade right now (or 'None')"
}"""


# ── M1 Agent — Entry Timing ───────────────────────────────────────────────────
async def analyze_m1(candles: List[Candle]) -> Optional[TimeframeAnalysis]:
    if not candles:
        return None

    prompt = f"""Analyze these M1 (1-minute) XAUUSD candles for SCALP ENTRY TIMING.

M1 CANDLES (last {min(len(candles), 40)}):
{_fmt(candles, 40)}

Your M1 role: ENTRY TIMING — find the precise micro-structure trigger.
Focus on:
- Last 5–10 candles: is momentum building or fading?
- Immediate support/resistance from recent candle highs/lows
- Candlestick patterns at key levels (pin bars, engulfing, doji rejection)
- Is there a clean breakout or are we in chop?
- Volume spikes suggesting institutional interest

Return ONLY this JSON (no markdown):
{_json_schema()}

Rules:
- support/resistance: the 3 most RECENT and RELEVANT levels from M1 price action
- signal_quality: be strict — M1 noise means most signals are 30–60. Only give 70+ for crystal-clear setups
- entry_note: name the EXACT candle pattern or level break that would trigger entry
- warning: call out any chop, wicks, or mixed signals"""

    return await _call_agent(prompt, "M1", candles)


# ── M5 Agent — Primary Scalp Signal ──────────────────────────────────────────
async def analyze_m5(candles: List[Candle]) -> Optional[TimeframeAnalysis]:
    if not candles:
        return None

    prompt = f"""Analyze these M5 (5-minute) XAUUSD candles for PRIMARY SCALP SIGNALS.

M5 CANDLES (last {min(len(candles), 40)}):
{_fmt(candles, 40)}

Your M5 role: PRIMARY SIGNAL — this is the MAIN scalping timeframe.
Focus on:
- Clear trend structure (HH/HL for bull, LH/LL for bear)
- Breakouts from consolidation ranges
- Key S/R levels that price is reacting to
- EMA crossover signals (assess from price action alone)
- Flag/pennant patterns, bull/bear traps
- Whether current move has continuation potential

Return ONLY this JSON (no markdown):
{_json_schema()}

Rules:
- This is the primary signal TF — be decisive but accurate
- signal_quality: 70+ only for clear trend + pattern + level confluence
- entry_note: describe the M5 pattern/level that confirms the trade
- warning: flag if price is extended from recent range or near major resistance"""

    return await _call_agent(prompt, "M5", candles)


# ── M15 Agent — Trend Context ─────────────────────────────────────────────────
async def analyze_m15(candles: List[Candle]) -> Optional[TimeframeAnalysis]:
    if not candles:
        return None

    prompt = f"""Analyze these M15 (15-minute) XAUUSD candles for SCALP TREND CONTEXT.

M15 CANDLES (last {min(len(candles), 40)}):
{_fmt(candles, 40)}

Your M15 role: TREND CONTEXT — are scalpers aligned with the current flow?
Focus on:
- Overall trend direction for the last 2–4 hours
- Major S/R levels (these are the zones scalpers must respect)
- Recent swing highs and lows — are they being broken or holding?
- Is price in a ranging or trending phase?
- Key levels where price might reverse vs. continue

Return ONLY this JSON (no markdown):
{_json_schema()}

Rules:
- support/resistance: the MOST IMPORTANT levels scalpers must know — missed levels kill scalps
- scalp_signal: direction aligned with M15 trend (scalpers should follow this bias)
- signal_quality: rate clarity of the M15 trend (ranging = low, trending = high)
- entry_note: describe what M15 price action confirms for scalpers
- warning: flag if scalpers are fighting the M15 trend"""

    return await _call_agent(prompt, "M15", candles)


# ── H1 Agent — Higher-Timeframe Bias ─────────────────────────────────────────
async def analyze_h1(candles: List[Candle]) -> Optional[TimeframeAnalysis]:
    if not candles:
        return None

    prompt = f"""Analyze these H1 (1-hour) XAUUSD candles for HIGHER-TIMEFRAME BIAS.

H1 CANDLES (last {min(len(candles), 30)}):
{_fmt(candles, 30)}

Your H1 role: HTF BIAS — scalpers must NOT trade against this direction.
Focus on:
- The dominant trend over the last 1–3 days
- Major H1 support and resistance zones (these are the walls)
- Where are we in the H1 structure? (at support, at resistance, mid-range)
- Is there a pending H1 reversal signal or is trend intact?
- Key daily levels visible on H1 charts

Return ONLY this JSON (no markdown):
{_json_schema()}

Rules:
- support/resistance: the BIG LEVELS — the ones visible even on H4. Fewer but more important.
- scalp_signal: overall HTF directional bias (this overrides lower TF signals if conflicting)
- signal_quality: how clear and strong is the H1 trend? Choppy H1 = dangerous for scalpers
- entry_note: describe the H1 context that scalpers must be aware of
- warning: flag if H1 trend is at a major reversal zone or if trend is exhausted"""

    return await _call_agent(prompt, "H1", candles)


# ── Internal caller ────────────────────────────────────────────────────────────
async def _call_agent(prompt: str, timeframe: str, candles: List[Candle]) -> Optional[TimeframeAnalysis]:
    try:
        raw = await call_llm(
            prompt=prompt,
            system=_BASE_SYSTEM,
            model="openai/gpt-4.1-nano",
            temperature=0.2,
            max_tokens=1000,
        )
        data = parse_json_response(raw)

        # Get actual price range from candles
        closes = [c.close for c in candles[-10:]]
        price_now = closes[-1] if closes else 0.0

        return TimeframeAnalysis(
            timeframe=timeframe,
            trend=data["trend"],
            strength=data["strength"],
            support_levels=data["support_levels"],
            resistance_levels=data["resistance_levels"],
            momentum=data["momentum"],
            scalp_signal=data["scalp_signal"],
            signal_quality=int(data["signal_quality"]),
            key_observations=data["key_observations"],
            entry_note=data.get("entry_note", ""),
            warning=data.get("warning", "None"),
            price_at_analysis=price_now,
        )

    except Exception as e:
        logger.error("TF agent [%s] failed: %s", timeframe, e)
        return None


# ── Run all 4 agents in parallel ──────────────────────────────────────────────
async def analyze_all_timeframes(candles_by_tf: dict) -> dict:
    """
    Run M1, M5, M15, H1 agents concurrently.
    Returns { "M1": TimeframeAnalysis | None, "M5": ..., "M15": ..., "H1": ... }
    """
    m1_coro  = analyze_m1(candles_by_tf.get("M1", []))
    m5_coro  = analyze_m5(candles_by_tf.get("M5", []))
    m15_coro = analyze_m15(candles_by_tf.get("M15", []))
    h1_coro  = analyze_h1(candles_by_tf.get("H1", []))

    results = await asyncio.gather(m1_coro, m5_coro, m15_coro, h1_coro, return_exceptions=True)

    out = {}
    for tf, res in zip(["M1", "M5", "M15", "H1"], results):
        if isinstance(res, Exception):
            logger.error("TF agent [%s] raised: %s", tf, res)
            out[tf] = None
        else:
            out[tf] = res

    logger.info(
        "MTF analysis complete — M1:%s M5:%s M15:%s H1:%s",
        "✓" if out["M1"] else "✗",
        "✓" if out["M5"] else "✗",
        "✓" if out["M15"] else "✗",
        "✓" if out["H1"] else "✗",
    )
    return out