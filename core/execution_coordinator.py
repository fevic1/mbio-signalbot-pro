
"""MBIO Execution Coordinator

Single gateway for every exchange action.
No strategy, risk engine or DCA engine may talk directly
to the exchange.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from core.event_bus import event_bus
from core.rate_limiter import rate_limiter
from core.verification_engine import verification_engine

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ExecutionResult:
    success: bool
    payload: dict[str, Any]
    error: str | None = None


class ExecutionCoordinator:

    def __init__(self, executor):
        self.executor = executor
        self._lock = asyncio.Lock()

    async def submit_order(self, **kwargs) -> ExecutionResult:

        async with self._lock:

            ok, reason = verification_engine.verify_order(kwargs)
            if not ok:
                return ExecutionResult(False, {}, reason)

            await rate_limiter.acquire("exchange")

            result = self.execution_coordinator.submit_order(**kwargs)

            await event_bus.publish(
                "order_submitted",
                {
                    "request": kwargs,
                    "response": result,
                },
            )

            if not result.get("success"):
                return ExecutionResult(
                    False,
                    result,
                    result.get("error"),
                )

            return ExecutionResult(True, result)

    async def cancel_order(self, order_id):

        async with self._lock:

            await rate_limiter.acquire("exchange")

            result = self.execution_coordinator.cancel_order(order_id)

            await event_bus.publish(
                "order_cancelled",
                result,
            )

            return result

    async def replace_order(
        self,
        cancel_id,
        new_order,
    ):

        await self.cancel_order(cancel_id)
        return await self.submit_order(**new_order)


