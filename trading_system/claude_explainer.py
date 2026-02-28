"""Claude explanation layer (optional, safe fallback when no API key)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict


def _fallback_explanation(payload: Dict[str, Any]) -> str:
    return (
        f"{payload['stock']} shows a {payload['bias']} setup with RR {payload['risk_reward']} and "
        f"position size {payload['position_size']}. VWAP tells you whether price is trading with "
        "intraday value, and volume spike suggests participation. Setup is invalid if price breaks the "
        f"stop-loss ({payload['stop_loss']}). Confidence: 65/100. Data is delayed by about "
        f"{payload['data_delay_minutes']} minutes. Verify live price on Kite before placing this trade."
    )


def explain_trade(payload: Dict[str, Any]) -> str:
    """Generate beginner-friendly explanation. Uses Anthropic when configured; else fallback."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_explanation(payload)

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        prompt = (
            "You are a conservative intraday trading coach. Explain this JSON in simple language for "
            "a beginner. Follow strict rules: never guarantee profit, remind to verify live price on "
            "Kite, mention 15-minute delay, validate RR, explain VWAP and volume, state invalidation, "
            "capital preservation priority, confidence in 60-75% range. If RR<2, explicitly avoid.\n\n"
            f"TRADE_JSON:\n{json.dumps(payload, indent=2)}"
        )
        message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=400,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception:
        return _fallback_explanation(payload)
