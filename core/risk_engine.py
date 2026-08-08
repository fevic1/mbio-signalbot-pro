
"""MBIO Risk Engine"""

from __future__ import annotations

from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RiskAssessment:
    score: float
    action: str
    reason: str


class RiskEngine:

    def evaluate(self, position: dict, market: dict) -> RiskAssessment:

        score = 1.0
        reason = []

        if market.get("volatility", 0) > position.get("max_volatility", 999):
            score -= 0.25
            reason.append("high_volatility")

        if market.get("drawdown", 0) > position.get("max_drawdown", 999):
            score -= 0.25
            reason.append("drawdown")

        if market.get("liquidity", 1) < position.get("min_liquidity", 0):
            score -= 0.25
            reason.append("low_liquidity")

        if market.get("spread", 0) > position.get("max_spread", 999):
            score -= 0.25
            reason.append("wide_spread")

        if score >= 0.75:
            action = "EXPAND"
        elif score >= 0.50:
            action = "HOLD"
        elif score >= 0.25:
            action = "REDUCE"
        else:
            action = "EXIT"

        return RiskAssessment(
            score=score,
            action=action,
            reason=",".join(reason),
        )


risk_engine = RiskEngine()
