"""
MT5 Bridge — fetches live ticks, OHLCV candles, and account info.
Now supports M1 and M5 for scalping multi-timeframe analysis.
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional

from models.schemas import Candle, PriceTick, MT5Status

logger = logging.getLogger(__name__)

# ── attempt MT5 import (Windows only) ────────────────────────
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.warning("MetaTrader5 package not available — running in disconnected mode.")

from config import settings
SYMBOL = getattr(settings, "MT5_SYMBOL", "XAUUSDm")

TIMEFRAME_MAP = {
    "M1":  mt5.TIMEFRAME_M1  if MT5_AVAILABLE else 1,
    "M5":  mt5.TIMEFRAME_M5  if MT5_AVAILABLE else 5,
    "M15": mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 15,
    "M30": mt5.TIMEFRAME_M30 if MT5_AVAILABLE else 30,
    "H1":  mt5.TIMEFRAME_H1  if MT5_AVAILABLE else 60,
    "H4":  mt5.TIMEFRAME_H4  if MT5_AVAILABLE else 240,
    "D1":  mt5.TIMEFRAME_D1  if MT5_AVAILABLE else 1440,
}

# ── Candle counts per timeframe for scalping ──────────────────
# M1:  50 candles = last 50 minutes  (entry timing)
# M5:  50 candles = last ~4 hours    (primary signal)
# M15: 40 candles = last 10 hours    (trend context)
# H1:  30 candles = last 30 hours    (HTF bias)
SCALPER_CANDLE_COUNTS = {
    "M1":  50,
    "M5":  50,
    "M15": 40,
    "H1":  30,
}

# ── internal state ────────────────────────────────────────────
_connected: bool = False



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

    if not mt5.symbol_select(SYMBOL, True):
        logger.warning(
            "Failed to select symbol %s in MT5 Market Watch. "
            "Check if it exists for your account type.", SYMBOL
        )

    _connected = True
    logger.info("MT5 connected successfully.")
    return True


def shutdown():
    global _connected
    if MT5_AVAILABLE and _connected:
        mt5.shutdown()
    _connected = False





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
    """Return latest tick from MT5."""
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


def get_scalper_candles() -> dict:
    """
    Fetch candles optimised for scalping multi-timeframe analysis.
    
    Returns:
        {
          "M1":  [...50 candles — entry timing],
          "M5":  [...50 candles — primary scalp signal],
          "M15": [...40 candles — trend context],
          "H1":  [...30 candles — HTF bias],
        }
    """
    result = {}
    for tf, count in SCALPER_CANDLE_COUNTS.items():
        candles = get_candles(tf, count)
        result[tf] = candles
        logger.debug("Fetched %d candles for %s", len(candles), tf)

    total = sum(len(v) for v in result.values())
    logger.info(
        "Scalper candles fetched — M1:%d M5:%d M15:%d H1:%d (total:%d)",
        len(result.get("M1", [])),
        len(result.get("M5", [])),
        len(result.get("M15", [])),
        len(result.get("H1", [])),
        total,
    )
    return result


# ── Legacy function (kept for backwards compat) ───────────────
def get_multi_timeframe_candles() -> dict:
    """Legacy wrapper — returns same as get_scalper_candles()."""
    return get_scalper_candles()