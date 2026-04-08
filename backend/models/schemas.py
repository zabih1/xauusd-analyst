from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Bias(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"


class ScalpSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"


class Trend(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    RANGING = "Ranging"


class Strength(str, Enum):
    STRONG = "Strong"
    MODERATE = "Moderate"
    WEAK = "Weak"


# ── Price Data ────────────────────────────────────────────────
class Candle(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str


class PriceTick(BaseModel):
    symbol: str = "XAUUSD"
    bid: float
    ask: float
    spread: float
    time: datetime
    source: str = "MT5"





# ── Per-Timeframe Analysis (new) ──────────────────────────────
class TimeframeAnalysis(BaseModel):
    timeframe: str                   # M1 | M5 | M15 | H1
    trend: Trend
    strength: Strength
    support_levels: List[float]
    resistance_levels: List[float]
    momentum: str
    scalp_signal: ScalpSignal        # BUY | SELL | WAIT
    signal_quality: int              # 0-100
    key_observations: List[str]
    entry_note: str                  # what to watch for on this TF
    warning: str                     # risk or reason to skip
    price_at_analysis: float = 0.0


# ── Scalper Trade Setup (new, replaces TradeSetup for scalp mode) ──
class ScalperTradeSetup(BaseModel):
    bias: Bias
    primary_timeframe: str           # which TF drove the signal
    entry_low: float
    entry_high: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward: float
    confidence: int                  # 0-100
    timeframe_alignment: str         # one-line alignment summary
    reasoning: str
    invalidation: str
    scalp_notes: str                 # execution tips
    do_not_trade_if: str             # skip conditions


# ── Legacy TechnicalAnalysis (kept for backwards compatibility) ──
class TechnicalAnalysis(BaseModel):
    trend: Trend
    strength: Strength
    support_levels: List[float]
    resistance_levels: List[float]
    key_observations: List[str]
    momentum: str


# ── Legacy TradeSetup (kept for backwards compat) ─────────────
class TradeSetup(BaseModel):
    bias: Bias
    entry_low: float
    entry_high: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward: float
    confidence: int
    reasoning: str
    invalidation: str


# ── Full Analysis Response ────────────────────────────────────
class FullAnalysis(BaseModel):
    id: str
    timestamp: datetime
    current_price: float
    session: str
    # MTF results (new)
    timeframe_analyses: Optional[dict] = None    # {"M1": TFAnalysis, ...}
    setup: ScalperTradeSetup
    # Legacy fields kept for compatibility
    technical: Optional[TechnicalAnalysis] = None
    candles_used: int
    source: str = "MT5"




# ── Risk Calculator ───────────────────────────────────────────
class RiskInput(BaseModel):
    account_balance: float
    risk_percent: float
    entry_price: float
    stop_loss_price: float
    take_profit_price: float


class RiskOutput(BaseModel):
    risk_amount_usd: float
    lot_size: float
    sl_pips: float
    tp_pips: float
    risk_reward: float
    potential_profit_usd: float
    margin_required: float


# ── MT5 Status ────────────────────────────────────────────────
class MT5Status(BaseModel):
    connected: bool
    account_number: Optional[int] = None
    broker: Optional[str] = None
    balance: Optional[float] = None
    equity: Optional[float] = None
    message: str = ""