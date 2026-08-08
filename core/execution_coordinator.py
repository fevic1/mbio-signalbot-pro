"""MBIO Execution Coordinator.

Single gateway for verified exchange actions. Strategies and lifecycle engines
must use this gateway instead of calling the exchange executor directly.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from core.event_bus import event_bus
from core.rate_limiter import rate_limiter
from core.verification_engine import verification_engine


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
            verification = await verification_engine.verify(**kwargs)
            if not verification.passed:
                return ExecutionResult(False, {}, verification.reason)

            await rate_limiter.acquire("exchange")
            result = await self._place_order(**kwargs)
            await event_bus.publish("order_submitted", {"request": kwargs, "response": result})
            if not result.get("success"):
                return ExecutionResult(False, result, result.get("error"))
            return ExecutionResult(True, result)

    async def _place_order(self, **kwargs) -> dict:
        coin = kwargs.pop("coin", kwargs.pop("asset", None))
        side = kwargs.pop("side")
        size = kwargs.pop("size")
        price = kwargs.pop("price", kwargs.pop("limit_price", None))
        reduce_only = kwargs.pop("reduce_only", False)
        strategy = kwargs.pop("strategy", "UNKNOWN")
        regime = kwargs.pop("regime", "UNKNOWN")
        execution_label = kwargs.pop("execution_label", "COORDINATED")
        order_type = kwargs.pop("order_type", "Limit")
        if not coin:
            return {"success": False, "error": "Missing asset/coin"}

        from execution.execution_context import ExecutionContext
        context = ExecutionContext(
            execution_label=execution_label,
            strategy=strategy,
            regime=regime,
            order_type=order_type,
        )
        result = self.executor.place_order(
            coin=coin,
            side=side,
            size=size,
            limit_price=price,
            order_type=order_type,
            reduce_only=reduce_only,
            execution_context=context,
        )
        if hasattr(result, "__await__"):
            result = await result
        return result or {}

    async def cancel_order(self, **kwargs):
        async with self._lock:
            await rate_limiter.acquire("exchange")
            result = self.executor.cancel_order(**kwargs)
            if hasattr(result, "__await__"):
                result = await result
            result = result or {}
            await event_bus.publish("order_cancelled", result)
            return result

    async def replace_order(self, cancel_id, new_order):
        coin = new_order.get("asset", new_order.get("coin"))
        await self.cancel_order(order_id=cancel_id, coin=coin)
        return await self.submit_order(**new_order)

    async def get_open_positions(self):
        result = self.executor.get_open_positions()
        if hasattr(result, "__await__"):
            result = await result
        return result or []
