
"""MBIO Strategy Engine"""

from __future__ import annotations

from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


THESIS_VALID = "THESIS_VALID"
THESIS_WEAKENED = "THESIS_WEAKENED"
THESIS_INVALID = "THESIS_INVALID"


@dataclass(slots=True)
class StrategyResult:
    thesis: str
    confidence: float
    score: float
    reason: str


class StrategyEngine:

    def evaluate(self, market: dict, position: dict) -> StrategyResult:

        score = 0.0
        reasons = []

        if market.get("trend") == position.get("direction"):
            score += 1.0
            reasons.append("trend")

        if market.get("regime") == position.get("regime"):
            score += 1.0
            reasons.append("regime")

        if market.get("volume_confirmed", False):
            score += 1.0
            reasons.append("volume")

        if market.get("volatility", 0) <= position.get("max_volatility", 999):
            score += 1.0
            reasons.append("volatility")

        confidence = score / 4.0

        if confidence >= 0.75:
            thesis = THESIS_VALID
        elif confidence >= 0.50:
            thesis = THESIS_WEAKENED
        else:
            thesis = THESIS_INVALID

        return StrategyResult(
            thesis=thesis,
            confidence=confidence,
            score=score,
            reason=",".join(reasons),
        )


strategy_engine = StrategyEngine()
