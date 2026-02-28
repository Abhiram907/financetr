"""Streamlit dashboard entry point."""

from __future__ import annotations

from datetime import datetime

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from trading_system import config
from trading_system.claude_explainer import explain_trade
from trading_system.scanner import run_scan

st.set_page_config(page_title="Intraday DSS (India)", layout="wide")

st.title("Intraday Trading Decision Support System (India - Zerodha)")
st.caption(
    "Rule-based decision support only. Data is delayed (~15 min on free tier). "
    "Always verify live price on Kite before placing any trade."
)

if "scan_result" not in st.session_state:
    st.session_state.scan_result = None
if "last_scan_ts" not in st.session_state:
    st.session_state.last_scan_ts = None

if st.button("Scan Market", type="primary"):
    with st.spinner("Fetching delayed 5-min data and evaluating setups..."):
        st.session_state.scan_result = run_scan()
        st.session_state.last_scan_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

result = st.session_state.scan_result

if st.session_state.last_scan_ts:
    st.info(
        f"Last scan: {st.session_state.last_scan_ts} | Data delay: approx {config.DATA_DELAY_MINUTES} minutes"
    )

if not result:
    st.warning("Click 'Scan Market' to start. This is for learning/paper trading with delayed data.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Nifty Trend", result["market_trend"])
col2.metric("Nifty % Change", f"{result['nifty_change_pct']}%")
col3.metric("Market ATR", result["market_atr"])
col4.metric("Total Setups", result["total_setups"])

if not result["top_setups"]:
    st.warning("No high probability setup. Wait.")
    st.stop()

table_df = pd.DataFrame(
    [
        {
            "Stock": setup["stock"],
            "Bias": setup["bias"],
            "Entry": setup["entry"],
            "Stop Loss": setup["stop_loss"],
            "Target": setup["target"],
            "RR": setup["risk_reward"],
            "Position Size": setup["position_size"],
            "Score": setup["score"],
        }
        for setup in result["top_setups"]
    ]
)

st.subheader("Top Opportunities")
st.dataframe(table_df, use_container_width=True, hide_index=True)

selected_stock = st.selectbox("Detailed view", table_df["Stock"].tolist())
selected = next(x for x in result["top_setups"] if x["stock"] == selected_stock)

history = selected["history"]

fig = go.Figure(
    data=[
        go.Candlestick(
            x=history["Timestamp"],
            open=history["Open"],
            high=history["High"],
            low=history["Low"],
            close=history["Close"],
            name="Price",
        ),
        go.Scatter(x=history["Timestamp"], y=history["VWAP"], mode="lines", name="VWAP"),
    ]
)
fig.add_hline(y=selected["entry"], line_dash="solid", line_color="blue", annotation_text="Entry")
fig.add_hline(y=selected["stop_loss"], line_dash="dash", line_color="red", annotation_text="Stop")
fig.add_hline(y=selected["target"], line_dash="dash", line_color="green", annotation_text="Target")
fig.update_layout(height=500, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10))

st.subheader(f"Chart: {selected['stock']}")
st.plotly_chart(fig, use_container_width=True)

vol_fig = go.Figure(
    data=[
        go.Bar(
            x=history["Timestamp"],
            y=history["Volume"],
            name="Volume",
        )
    ]
)
vol_fig.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(vol_fig, use_container_width=True)

st.subheader("Trade Explanation (Claude layer)")
explanation_payload = {
    key: selected[key]
    for key in [
        "stock",
        "bias",
        "current_price",
        "vwap",
        "volume_ratio",
        "structure",
        "atr",
        "entry",
        "stop_loss",
        "target",
        "risk_reward",
        "position_size",
        "max_risk_rupees",
        "market_trend",
        "data_delay_minutes",
    ]
}
st.write(explain_trade(explanation_payload))
st.warning("Workflow: Scan → Read explanation → Verify LIVE chart on Kite → Then execute manually.")
