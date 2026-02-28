"""Market data access layer (free yfinance source)."""

from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_intraday(symbol: str, period: str = "1d", interval: str = "5m") -> pd.DataFrame:
    """Fetch 5-minute intraday bars for one symbol."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval, auto_adjust=False)
    if df.empty:
        return df

    # Normalize timezone/index for stable UI display.
    df = df.reset_index()
    time_col = "Datetime" if "Datetime" in df.columns else "Date"
    df = df.rename(columns={time_col: "Timestamp"})
    df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.tz_localize(None)
    return df
