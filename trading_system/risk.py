"""Risk and position sizing helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradeLevels:
    entry: float
    stop_loss: float
    target: float
    risk_reward: float
    position_size: int
    risk_per_share: float


def calculate_levels(
    last_close: float,
    bias: str,
    atr: float,
    max_risk_rupees: float = 50.0,
) -> TradeLevels:
    """Calculate entry, stop, target, RR and quantity using ATR and fixed rupee risk."""
    entry = float(last_close)

    if atr <= 0:
        return TradeLevels(entry, entry, entry, 0.0, 0, 0.0)

    if bias == "LONG":
        stop_loss = round(entry - (1.5 * atr), 2)
        target = round(entry + (3 * atr), 2)
    elif bias == "SHORT":
        stop_loss = round(entry + (1.5 * atr), 2)
        target = round(entry - (3 * atr), 2)
    else:
        return TradeLevels(entry, entry, entry, 0.0, 0, 0.0)

    risk_per_share = abs(entry - stop_loss)
    if risk_per_share <= 0:
        return TradeLevels(entry, stop_loss, target, 0.0, 0, risk_per_share)

    rr = round(abs(target - entry) / risk_per_share, 2)
    position_size = int(max_risk_rupees / risk_per_share)

    return TradeLevels(entry, stop_loss, target, rr, position_size, risk_per_share)
