
"""MBIO Decision Matrix"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Decision(str, Enum):
    HOLD = "HOLD"
    EXPAND = "EXPAND"
    REDUCE = "REDUCE"
    EXIT = "EXIT"
    ADJUST = "ADJUST"


@dataclass(slots=True)
class DecisionResult:
    action: Decision
    confidence: float
    reason: str


class DecisionMatrix:

    def evaluate(
        self,
        thesis: str,
        risk_action: str,
        verification_ok: bool,
    ) -> DecisionResult:

        if not verification_ok:
            return DecisionResult(
                Decision.HOLD,
                0.0,
                "verification_failed",
            )

        if thesis == "THESIS_INVALID":
            return DecisionResult(
                Decision.EXIT,
                1.0,
                "strategy_invalid",
            )

        if thesis == "THESIS_WEAKENED":

            if risk_action == "EXIT":
                return DecisionResult(
                    Decision.EXIT,
                    0.95,
                    "risk_exit",
                )

            if risk_action == "REDUCE":
                return DecisionResult(
                    Decision.REDUCE,
                    0.90,
                    "risk_reduce",
                )

            return DecisionResult(
                Decision.HOLD,
                0.70,
                "wait_confirmation",
            )

        if thesis == "THESIS_VALID":

            if risk_action == "EXPAND":
                return DecisionResult(
                    Decision.EXPAND,
                    0.95,
                    "add_position",
                )

            if risk_action == "HOLD":
                return DecisionResult(
                    Decision.HOLD,
                    0.90,
                    "healthy_position",
                )

            if risk_action == "REDUCE":
                return DecisionResult(
                    Decision.REDUCE,
                    0.85,
                    "protect_capital",
                )

            if risk_action == "EXIT":
                return DecisionResult(
                    Decision.EXIT,
                    0.95,
                    "risk_override",
                )

        return DecisionResult(
            Decision.HOLD,
            0.5,
            "fallback",
        )


decision_matrix = DecisionMatrix()
