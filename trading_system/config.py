"""Configuration constants for the intraday trading decision support system."""

from __future__ import annotations

STOCK_UNIVERSE = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "AXISBANK.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "WIPRO.NS",
    "HINDUNILVR.NS",
    "BAJFINANCE.NS",
    "MARUTI.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "ADANIENT.NS",
    "NTPC.NS",
    "POWERGRID.NS",
    "ONGC.NS",
    "COALINDIA.NS",
    "TECHM.NS",
    "HCLTECH.NS",
    "SUNPHARMA.NS",
    "DRREDDY.NS",
    "CIPLA.NS",
    "DIVISLAB.NS",
    "TITAN.NS",
    "ULTRACEMCO.NS",
    "GRASIM.NS",
    "NESTLEIND.NS",
    "BRITANNIA.NS",
    "HEROMOTOCO.NS",
    "BAJAJFINSV.NS",
    "INDUSINDBK.NS",
    "M&M.NS",
    "TATACONSUM.NS",
    "ASIANPAINT.NS",
    "EICHERMOT.NS",
    "SHREECEM.NS",
    "BPCL.NS",
    "IOC.NS",
    "JSWSTEEL.NS",
    "HINDALCO.NS",
    "VEDL.NS",
    "SAIL.NS",
    "NMDC.NS",
    "BANKBARODA.NS",
    "PNB.NS",
    "CANBK.NS",
    "IDEA.NS",
]

NIFTY_SYMBOL = "^NSEI"

MIN_STOCK_PRICE = 20.0
INTRADAY_PERIOD = "1d"
INTRADAY_INTERVAL = "5m"
DATA_DELAY_MINUTES = 15

MAX_RISK_PER_TRADE_RUPEES = 50.0
MIN_RR = 2.0
MIN_SCORE_TO_DISPLAY = 70
TOP_SETUPS_TO_DISPLAY = 3

VOLUME_WINDOW = 10
VOLUME_SPIKE_THRESHOLD = 1.5
ATR_PERIOD = 14
