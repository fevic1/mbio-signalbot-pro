
"""MBIO Position Manager

Institutional position management layer.

Strategy -> Verification -> Risk -> Decision -> Execution
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from core.strategy_engine import strategy_engine
from core.verification_engine import verification_engine
from core.risk_engine import risk_engine
from core.decision_matrix import decision_matrix
from core.dca_execution_engine import dca_execution_engine

logger = logging.getLogger(__name__)


HOLD = "HOLD"
EXPAND = "EXPAND"
REDUCE = "REDUCE"
EXIT = "EXIT"


@dataclass(slots=True)
class PositionDecision:

    action: str
    confidence: float
    reason: str


class PositionManager:

    async def evaluate(
        self,
        asset: str,
        market: dict,
        position: dict,
    ) -> PositionDecision:

        thesis = strategy_engine.evaluate(
            market,
            position,
        )

        verify = verification_engine.verify_position(
            market,
            position,
        )

        risk = risk_engine.evaluate_position(
            market,
            position,
        )

        decision = decision_matrix.evaluate(
            thesis,
            verify,
            risk,
        )

        action = decision.action

        if action == "EXPAND":

            logger.info(
                "Expanding %s",
                asset,
            )

            await dca_execution_engine.synchronize(
                asset,
                position,
            )

        elif action == "REDUCE":

            logger.info(
                "Reducing %s",
                asset,
            )

        elif action == "EXIT":

            logger.info(
                "Closing %s",
                asset,
            )

        else:

            logger.debug(
                "Holding %s",
                asset,
            )

        return PositionDecision(
            action=action,
            confidence=getattr(decision, "confidence", 1.0),
            reason=getattr(decision, "reason", ""),
        )

    async def tick(
        self,
        open_positions: dict,
        market_cache: dict,
    ):

        for asset, position in list(open_positions.items()):

            market = market_cache.get(asset)

            if not market:
                continue

            try:

                await self.evaluate(
                    asset,
                    market,
                    position,
                )

            except Exception:

                logger.exception(
                    "Position manager failed %s",
                    asset,
                )


position_manager = PositionManager()
