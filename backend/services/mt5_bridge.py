"""
MT5 Bridge — fetches live ticks, OHLCV candles, and account info.
Falls back to manual price if MT5 is not connected.
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from models.schemas import Candle, PriceTick, MT5Status

logger = logging.getLogger(__name__)

# ── attempt MT5 import (Windows only) ────────────────────────
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.warning("MetaTrader5 package not available — running in manual mode.")

SYMBOL = "XAUUSD"

TIMEFRAME_MAP = {
    "M1":  mt5.TIMEFRAME_M1  if MT5_AVAILABLE else 1,
    "M5":  mt5.TIMEFRAME_M5  if MT5_AVAILABLE else 5,
    "M15": mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 15,
    "M30": mt5.TIMEFRAME_M30 if MT5_AVAILABLE else 30,
    "H1":  mt5.TIMEFRAME_H1  if MT5_AVAILABLE else 60,
    "H4":  mt5.TIMEFRAME_H4  if MT5_AVAILABLE else 240,
    "D1":  mt5.TIMEFRAME_D1  if MT5_AVAILABLE else 1440,
}


# ── internal state ────────────────────────────────────────────
_connected: bool = False
_manual_bid: Optional[float] = None
_manual_ask: Optional[float] = None


def initialize(login: int, password: str, server: str) -> bool:
    global _connected
    if not MT5_AVAILABLE:
        logger.warning("MT5 not available, skipping init.")
        return False
    if not mt5.initialize():
        logger.error("MT5 initialize() failed: %s", mt5.last_error())
        return False
    authorized = mt5.login(login, password=password, server=server)
    if not authorized:
        logger.error("MT5 login failed: %s", mt5.last_error())
        mt5.shutdown()
        return False
    _connected = True
    logger.info("MT5 connected successfully.")
    return True


def shutdown():
    global _connected
    if MT5_AVAILABLE and _connected:
        mt5.shutdown()
    _connected = False


def set_manual_price(bid: float, ask: float):
    global _manual_bid, _manual_ask
    _manual_bid = bid
    _manual_ask = ask


def get_status() -> MT5Status:
    if not MT5_AVAILABLE:
        return MT5Status(connected=False, message="MetaTrader5 package not installed (Windows only).")
    if not _connected:
        return MT5Status(connected=False, message="MT5 not connected. Set credentials in .env.")
    info = mt5.account_info()
    if info is None:
        return MT5Status(connected=False, message="Could not fetch account info.")
    return MT5Status(
        connected=True,
        account_number=info.login,
        broker=info.company,
        balance=info.balance,
        equity=info.equity,
        message="Connected",
    )


def get_tick() -> Optional[PriceTick]:
    """Return latest tick — from MT5 or manual fallback."""
    if _connected and MT5_AVAILABLE:
        tick = mt5.symbol_info_tick(SYMBOL)
        if tick:
            return PriceTick(
                bid=round(tick.bid, 2),
                ask=round(tick.ask, 2),
                spread=round((tick.ask - tick.bid) * 10, 1),
                time=datetime.fromtimestamp(tick.time, tz=timezone.utc),
                source="MT5",
            )

    # manual fallback
    if _manual_bid and _manual_ask:
        return PriceTick(
            bid=_manual_bid,
            ask=_manual_ask,
            spread=round((_manual_ask - _manual_bid) * 10, 1),
            time=datetime.now(tz=timezone.utc),
            source="manual",
        )

    return None


def get_candles(timeframe: str = "H1", count: int = 100) -> List[Candle]:
    """Fetch OHLCV candles from MT5."""
    if not _connected or not MT5_AVAILABLE:
        return []

    tf = TIMEFRAME_MAP.get(timeframe.upper())
    if tf is None:
        return []

    rates = mt5.copy_rates_from_pos(SYMBOL, tf, 0, count)
    if rates is None:
        return []

    candles = []
    for r in rates:
        candles.append(Candle(
            time=datetime.fromtimestamp(r["time"], tz=timezone.utc),
            open=round(r["open"], 2),
            high=round(r["high"], 2),
            low=round(r["low"], 2),
            close=round(r["close"], 2),
            volume=float(r["tick_volume"]),
            timeframe=timeframe,
        ))
    return candles


def get_multi_timeframe_candles() -> dict:
    """Fetch candles across multiple timeframes for richer analysis."""
    return {
        "M15": get_candles("M15", 50),
        "H1":  get_candles("H1", 50),
        "H4":  get_candles("H4", 30),
        "D1":  get_candles("D1", 20),
    }
