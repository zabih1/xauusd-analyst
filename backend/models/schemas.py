from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Bias(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"


class Trend(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    RANGING = "Ranging"


class Strength(str, Enum):
    STRONG = "Strong"
    MODERATE = "Moderate"
    WEAK = "Weak"


class SentimentLevel(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


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
    source: str = "MT5"  # MT5 | manual


class ManualPriceInput(BaseModel):
    bid: float
    ask: float


# ── News ──────────────────────────────────────────────────────
class NewsItem(BaseModel):
    title: str
    source: str
    published_at: datetime
    url: Optional[str] = None
    impact: Optional[str] = None      # HIGH | MEDIUM | LOW
    sentiment: Optional[str] = None   # BULLISH | BEARISH | NEUTRAL


# ── Analysis ─────────────────────────────────────────────────
class TechnicalAnalysis(BaseModel):
    trend: Trend
    strength: Strength
    support_levels: List[float]
    resistance_levels: List[float]
    key_observations: List[str]
    momentum: str


class FundamentalAnalysis(BaseModel):
    overall_sentiment: SentimentLevel
    sentiment_score: float          # -1.0 to +1.0
    dxy_outlook: str
    macro_factors: List[str]
    news_summary: str


class TradeSetup(BaseModel):
    bias: Bias
    entry_low: float
    entry_high: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward: float
    confidence: int                 # 0-100
    reasoning: str
    invalidation: str               # when the setup is wrong


class FullAnalysis(BaseModel):
    id: str
    timestamp: datetime
    current_price: float
    session: str                    # Asian | London | New York | Overlap
    technical: TechnicalAnalysis
    fundamental: FundamentalAnalysis
    setup: TradeSetup
    news_items: List[NewsItem]
    candles_used: int
    source: str = "MT5"


# ── Chart Vision ──────────────────────────────────────────────
class VisionAnalysis(BaseModel):
    patterns_found: List[str]
    trend_visible: str
    key_levels: List[str]
    trade_suggestion: str
    confidence: int
    detailed_analysis: str


# ── Risk Calculator ───────────────────────────────────────────
class RiskInput(BaseModel):
    account_balance: float
    risk_percent: float             # e.g. 1.0 for 1%
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
