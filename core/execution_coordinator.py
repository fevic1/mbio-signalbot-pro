"""MBIO Execution Coordinator.

Single gateway for verified exchange actions.
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
            result = await self._call(self.executor.submit_order, **kwargs)
            await event_bus.publish("order_submitted", {"request": kwargs, "response": result})
            if not result.get("success"):
                return ExecutionResult(False, result, result.get("error"))
            return ExecutionResult(True, result)

    async def cancel_order(self, **kwargs):
        async with self._lock:
            await rate_limiter.acquire("exchange")
            result = await self._call(self.executor.cancel_order, **kwargs)
            await event_bus.publish("order_cancelled", result)
            return result

    async def replace_order(self, cancel_id, new_order):
        await self.cancel_order(order_id=cancel_id)
        return await self.submit_order(**new_order)

    async def get_open_positions(self):
        return await self._call(self.executor.get_open_positions)

    async def _call(self, method, *args, **kwargs):
        result = method(*args, **kwargs)
        if hasattr(result, "__await__"):
            result = await result
        return result or {}
