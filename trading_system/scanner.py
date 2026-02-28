"""Core scanning engine that applies rules and returns ranked setups."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from trading_system import config
from trading_system.data_fetcher import fetch_intraday
from trading_system.indicators import calculate_atr, calculate_vwap, detect_structure, volume_spike
from trading_system.risk import TradeLevels, calculate_levels
from trading_system.scorer import score_setup


def _market_trend(nifty_df: pd.DataFrame) -> Tuple[str, float, float]:
    if nifty_df.empty or len(nifty_df) < 3:
        return "NEUTRAL", 0.0, 0.0

    first_close = float(nifty_df["Close"].iloc[0])
    last_close = float(nifty_df["Close"].iloc[-1])
    pct_change = ((last_close - first_close) / first_close) * 100 if first_close else 0.0

    tmp = calculate_atr(nifty_df, period=config.ATR_PERIOD)
    atr = float(tmp["ATR"].iloc[-1]) if not np.isnan(tmp["ATR"].iloc[-1]) else 0.0

    structure = detect_structure(nifty_df)
    if pct_change > 0.3 and structure == "BULLISH":
        return "BULLISH", round(pct_change, 2), round(atr, 2)
    if pct_change < -0.3 and structure == "BEARISH":
        return "BEARISH", round(pct_change, 2), round(atr, 2)
    return "NEUTRAL", round(pct_change, 2), round(atr, 2)


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = calculate_vwap(df)
    df = calculate_atr(df, period=config.ATR_PERIOD)
    df = volume_spike(df, window=config.VOLUME_WINDOW, threshold=config.VOLUME_SPIKE_THRESHOLD)
    return df


def _build_setup(symbol: str, df: pd.DataFrame, market_trend: str) -> Dict | None:
    if df.empty or len(df) < max(config.ATR_PERIOD, config.VOLUME_WINDOW) + 3:
        return None

    df = _prepare(df)
    last = df.iloc[-1]
    price = float(last["Close"])
    if price < config.MIN_STOCK_PRICE:
        return None

    atr = float(last["ATR"]) if not np.isnan(last["ATR"]) else 0.0
    if atr <= 0:
        return None

    structure = detect_structure(df)
    vol_spike = bool(last["Vol_Spike"])
    vwap = float(last["VWAP"])

    long_ok = (
        price > vwap
        and vol_spike
        and structure == "BULLISH"
        and market_trend != "BEARISH"
    )
    short_ok = (
        price < vwap
        and vol_spike
        and structure == "BEARISH"
        and market_trend != "BULLISH"
    )

    if not long_ok and not short_ok:
        return None

    bias = "LONG" if long_ok else "SHORT"
    levels: TradeLevels = calculate_levels(
        last_close=price,
        bias=bias,
        atr=atr,
        max_risk_rupees=config.MAX_RISK_PER_TRADE_RUPEES,
    )
    if levels.position_size <= 0 or levels.risk_reward < config.MIN_RR:
        return None

    score = score_setup(
        bias=bias,
        price=price,
        vwap=vwap,
        volume_spike=vol_spike,
        structure=structure,
        rr=levels.risk_reward,
        market_trend=market_trend,
    )
    if score < config.MIN_SCORE_TO_DISPLAY:
        return None

    return {
        "stock": symbol.replace(".NS", ""),
        "symbol": symbol,
        "bias": bias,
        "current_price": round(price, 2),
        "vwap": round(vwap, 2),
        "volume_ratio": round(float(last.get("Vol_Ratio", 0.0)), 2),
        "structure": structure,
        "atr": round(atr, 2),
        **asdict(levels),
        "risk_reward": levels.risk_reward,
        "max_risk_rupees": config.MAX_RISK_PER_TRADE_RUPEES,
        "market_trend": market_trend,
        "score": score,
        "data_delay_minutes": config.DATA_DELAY_MINUTES,
        "history": df,
    }


def run_scan() -> Dict[str, object]:
    """Run one click-based market scan and return market + setup data."""
    nifty = fetch_intraday(config.NIFTY_SYMBOL, config.INTRADAY_PERIOD, config.INTRADAY_INTERVAL)
    market_trend, nifty_change_pct, market_atr = _market_trend(nifty)

    setups: List[Dict] = []
    for symbol in config.STOCK_UNIVERSE:
        try:
            df = fetch_intraday(symbol, config.INTRADAY_PERIOD, config.INTRADAY_INTERVAL)
            setup = _build_setup(symbol, df, market_trend)
            if setup:
                setups.append(setup)
        except Exception:
            continue

    ranked = sorted(setups, key=lambda x: x["score"], reverse=True)
    return {
        "market_trend": market_trend,
        "nifty_change_pct": nifty_change_pct,
        "market_atr": market_atr,
        "total_setups": len(ranked),
        "top_setups": ranked[: config.TOP_SETUPS_TO_DISPLAY],
        "all_setups": ranked,
    }
