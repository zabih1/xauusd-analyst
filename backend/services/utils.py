"""Utility helpers — session detection, risk calculator."""
from datetime import datetime, timezone
from models.schemas import RiskInput, RiskOutput


def get_current_session() -> str:
    """Determine the current forex trading session based on UTC time."""
    now = datetime.now(timezone.utc)
    hour = now.hour

    # Session times in UTC
    asian_open   = 0;  asian_close   = 8
    london_open  = 7;  london_close  = 16
    ny_open      = 12; ny_close      = 21

    in_asian  = asian_open  <= hour < asian_close
    in_london = london_open <= hour < london_close
    in_ny     = ny_open     <= hour < ny_close

    if in_london and in_ny:
        return "London / New York Overlap 🔥"
    if in_london:
        return "London Session"
    if in_ny:
        return "New York Session"
    if in_asian:
        return "Asian Session"
    return "Off-Hours"


def calculate_risk(inp: RiskInput) -> RiskOutput:
    """
    Calculate position sizing for XAUUSD.
    Gold: 1 standard lot = 100 oz, pip value ≈ $1 per 0.01 price move per 0.01 lot.
    """
    risk_usd = inp.account_balance * (inp.risk_percent / 100)

    sl_distance = abs(inp.entry_price - inp.stop_loss_price)
    tp_distance = abs(inp.take_profit_price - inp.entry_price)

    if sl_distance == 0:
        return RiskOutput(
            risk_amount_usd=0, lot_size=0, sl_pips=0,
            tp_pips=0, risk_reward=0, potential_profit_usd=0,
            margin_required=0,
        )

    # For XAUUSD: 1 lot = 100 oz, pip = $0.01
    # Value per pip per lot = $1 (100 oz * $0.01)
    # sl_pips = sl_distance / 0.01
    sl_pips = sl_distance / 0.01
    tp_pips = tp_distance / 0.01

    # lot_size = risk_usd / (sl_pips * pip_value_per_lot)
    pip_value_per_lot = 1.0  # USD per pip for 1 lot XAUUSD
    lot_size = risk_usd / (sl_pips * pip_value_per_lot)
    lot_size = round(lot_size, 2)

    potential_profit = lot_size * tp_pips * pip_value_per_lot
    rr = round(tp_distance / sl_distance, 2)

    # Approximate margin (varies by broker, ~$1000/lot for gold typical)
    margin_required = round(lot_size * 1000, 2)

    return RiskOutput(
        risk_amount_usd=round(risk_usd, 2),
        lot_size=lot_size,
        sl_pips=round(sl_pips, 1),
        tp_pips=round(tp_pips, 1),
        risk_reward=rr,
        potential_profit_usd=round(potential_profit, 2),
        margin_required=margin_required,
    )
