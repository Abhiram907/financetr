"""Scoring model for ranking setup quality."""

from __future__ import annotations


def score_setup(
    *,
    bias: str,
    price: float,
    vwap: float,
    volume_spike: bool,
    structure: str,
    rr: float,
    market_trend: str,
) -> int:
    score = 0

    if bias == "LONG" and price > vwap:
        score += 25
    elif bias == "SHORT" and price < vwap:
        score += 25

    if volume_spike:
        score += 25

    if (bias == "LONG" and structure == "BULLISH") or (bias == "SHORT" and structure == "BEARISH"):
        score += 25

    if rr >= 2.5:
        score += 15

    if (bias == "LONG" and market_trend != "BEARISH") or (bias == "SHORT" and market_trend != "BULLISH"):
        score += 10

    return score
