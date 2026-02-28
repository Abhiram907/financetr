"""Technical indicator calculations and market structure logic."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """Add VWAP-related columns to OHLCV data frame."""
    out = df.copy()
    out["TP"] = (out["High"] + out["Low"] + out["Close"]) / 3
    out["TPV"] = out["TP"] * out["Volume"]
    cumulative_volume = out["Volume"].cumsum().replace(0, np.nan)
    out["VWAP"] = out["TPV"].cumsum() / cumulative_volume
    return out


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Add True Range and ATR columns."""
    out = df.copy()
    prev_close = out["Close"].shift(1)
    out["TR"] = np.maximum(
        out["High"] - out["Low"],
        np.maximum(
            (out["High"] - prev_close).abs(),
            (out["Low"] - prev_close).abs(),
        ),
    )
    out["ATR"] = out["TR"].rolling(window=period).mean()
    return out


def volume_spike(
    df: pd.DataFrame,
    window: int = 10,
    threshold: float = 1.5,
) -> pd.DataFrame:
    """Add rolling volume average and boolean spike indicator."""
    out = df.copy()
    out["Vol_Avg"] = out["Volume"].rolling(window=window).mean()
    out["Vol_Ratio"] = np.where(out["Vol_Avg"] > 0, out["Volume"] / out["Vol_Avg"], np.nan)
    out["Vol_Spike"] = out["Volume"] > (threshold * out["Vol_Avg"])
    return out


def detect_structure(df: pd.DataFrame) -> str:
    """Detect simple HH/HL (bullish) or LH/LL (bearish) structure."""
    highs = df["High"].values
    lows = df["Low"].values
    n = len(highs)
    if n < 3:
        return "NEUTRAL"

    hh = highs[-1] > highs[-2] > highs[-3]
    hl = lows[-1] > lows[-2] > lows[-3]
    lh = highs[-1] < highs[-2] < highs[-3]
    ll = lows[-1] < lows[-2] < lows[-3]

    if hh and hl:
        return "BULLISH"
    if lh and ll:
        return "BEARISH"
    return "NEUTRAL"
