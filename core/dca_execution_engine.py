"""MBIO DCA execution engine.

Single DCA lifecycle owner. Exchange access is routed through the application's
execution coordinator; strategy logic remains in InstitutionalDcaStrategy.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, List

import core.state as state
from core.app_context import app_context
from core.market_cache import market_cache
from core.execution_coordinator import ExecutionCoordinator, ExecutionResult

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DCAOrder:
    level: int
    price: float
    size: float
    side: str


class DCAExecutionEngine:
    """Own DCA order lifecycle and use the verified execution gateway."""

    def __init__(self) -> None:
        self.active: dict[str, dict[str, Any]] = {}
        self._coordinator: ExecutionCoordinator | None = None

    @property
    def execution(self) -> ExecutionCoordinator:
        executor = app_context.executor
        if self._coordinator is None or self._coordinator.executor is not executor:
            self._coordinator = ExecutionCoordinator(executor)
        return self._coordinator

    def spacing_pct(self, volatility: float, base: float = 1.20) -> float:
        if volatility < 0.01:
            return base
        if volatility < 0.02:
            return base * 1.20
        if volatility < 0.04:
            return base * 1.50
        return base * 2.00

    def level_size(self, base_size: float, level: int, multiplier: float) -> float:
        return base_size * (multiplier ** level)

    def build_ladder(self, entry: float, side: str, base_size: float, levels: int, spacing: float, multiplier: float) -> List[DCAOrder]:
        ladder: List[DCAOrder] = []
        for level in range(levels):
            distance = spacing * (level + 1) / 100
            is_long = side in ("BUY", "LONG")
            price = entry * (1 - distance) if is_long else entry * (1 + distance)
            order_side = "BUY" if is_long else "SELL"
            ladder.append(DCAOrder(level + 1, round(price, 8), self.level_size(base_size, level, multiplier), order_side))
        return ladder

    async def _submit(self, asset: str, order: DCAOrder) -> ExecutionResult:
        return await self.execution.submit_order(
            asset=asset,
            side=order.side,
            price=order.price,
            size=order.size,
            reduce_only=False,
            strategy="DCA",
        )

    async def _cancel(self, asset: str, order_id: Any) -> dict:
        return await self.execution.cancel_order(coin=asset, order_id=int(order_id))

    async def synchronize(self, asset: str, position: dict) -> None:
        dca = position.get("dca")
        if not dca or not dca.get("enabled", True):
            return
        market = market_cache.get(asset) if hasattr(market_cache, "get") else None
        market = market or market_cache.snapshot().get(asset, {})
        volatility = float(market.get("volatility", 0.02) or 0.02)
        base_spacing = float(dca.get("spacing_pct", dca.get("level_spacing_pct", 1.2)))
        spacing = self.spacing_pct(volatility, base_spacing)
        ladder = self.build_ladder(
            float(position.get("entry", position.get("entry_price", 0))),
            str(position.get("side", "LONG")),
            float(dca.get("base_size", position.get("size", 0))),
            int(dca.get("levels", dca.get("max_levels", 3))),
            spacing,
            float(dca.get("size_multiplier", 1.25)),
        )
        await self.replace_ladder(asset, ladder, dca)

    async def replace_ladder(self, asset: str, ladder: List[DCAOrder], dca: dict) -> None:
        for order in list(dca.get("active_orders", [])):
            oid = order.get("order_id")
            if oid not in (None, "", 0, "0") and str(order.get("status", "OPEN")).upper() in {"OPEN", "ACTIVE"}:
                try:
                    await self._cancel(asset, oid)
                except Exception:
                    logger.exception("Failed cancelling DCA order %s for %s", oid, asset)

        dca["active_orders"] = []
        for order in ladder:
            try:
                result = await self._submit(asset, order)
            except Exception:
                logger.exception("DCA submit failed for %s level %s", asset, order.level)
                continue
            if result.success:
                oid = result.payload.get("order_id", result.payload.get("oid"))
                if oid is not None:
                    dca["active_orders"].append({"order_id": oid, "price": order.price, "size": order.size, "level": order.level, "status": "OPEN"})

        self.active[asset] = dca
        state.save_state()
        logger.info("DCA ladder synchronized %s (%d/%d levels)", asset, len(dca["active_orders"]), len(ladder))

    async def on_fill(self, asset: str, position: dict) -> None:
        await self.synchronize(asset, position)

    async def on_regime_change(self, asset: str, position: dict) -> None:
        await self.synchronize(asset, position)

    async def close_position(self, asset: str, config: dict, close_side: str) -> dict:
        results = {"base_closed": False, "dca_cancelled": 0, "dca_closed": 0, "total_pnl": 0.0, "errors": []}
        for order in list(config.get("active_orders", [])):
            oid = order.get("order_id")
            if oid in (None, "", 0, "0"):
                continue
            try:
                await self._cancel(asset, oid)
                results["dca_cancelled"] += 1
            except Exception as exc:
                results["errors"].append(f"Cancel {oid}: {exc}")

        try:
            positions = await self.execution.get_open_positions()
            if isinstance(positions, dict):
                positions = positions.get("positions", [])
            for pos in positions or []:
                if pos.get("coin") != asset:
                    continue
                size = abs(float(pos.get("size", 0) or 0))
                if size <= 0:
                    continue
                from execution.hl_executor import execute_hl_order
                result = await asyncio.to_thread(execute_hl_order, coin=asset, side=close_side, size=size, reduce_only=True, strategy="AUTO_DCA", regime="AUTO", execution_label="DCA_EXIT")
                if result.get("success"):
                    results["base_closed"] = True
                    results["dca_closed"] += 1
                else:
                    results["errors"].append(f"Close failed: {result.get('error')}")
        except Exception as exc:
            results["errors"].append(f"Position close error: {exc}")

        config["enabled"] = False
        config["closed_at"] = datetime.now(timezone.utc).isoformat()
        self.active.pop(asset, None)
        async with state.STATE_LOCK:
            state.DCA_POSITIONS.pop(asset, None)
            state.save_state()
        return results

    async def update_trailing_orders(self, asset: str, config: dict, current_price: float) -> dict:
        position = state.OPEN_POSITIONS.get(asset)
        if not position or not config.get("enabled"):
            return {"updated": 0, "error": None}
        before = len(config.get("active_orders", []))
        await self.synchronize(asset, position)
        after = len(config.get("active_orders", []))
        return {"updated": max(before, after), "error": None}

    def check_profit_target(self, asset: str, config: dict, current_price: float) -> dict | None:
        position = state.OPEN_POSITIONS.get(asset)
        if not position or not config.get("enabled"):
            return None
        entry = float(position.get("entry", position.get("entry_price", 0)) or 0)
        size = abs(float(position.get("size", 0) or 0))
        if entry <= 0 or size <= 0:
            return None
        direction = str(config.get("direction", position.get("side", "LONG"))).upper()
        pnl_pct = ((current_price - entry) / entry * 100) if direction in {"LONG", "BUY"} else ((entry - current_price) / entry * 100)
        target = float(config.get("profit_target_pct", 0) or 0)
        return {"pnl_pct": pnl_pct, "target_pct": target} if target > 0 and pnl_pct >= target else None

    async def close_dca_position(self, asset: str, config: dict, close_side: str) -> dict:
        return await self.close_position(asset, config, close_side)


dca_execution_engine = DCAExecutionEngine()

async def handle_dca_fill(*args, **kwargs):
    handler = getattr(dca_execution_engine, "handle_fill", None)
    return await handler(*args, **kwargs) if handler else None

def activate_auto_dca(asset: str, direction: str, base_size: float, max_levels: int = 3, spacing_pct: float = 1.2, size_multiplier: float = 1.25, tp_pct: float = 2.0, sl_pct: float = 2.5, leverage: float = None) -> None:
    state.auto_dca_active[asset] = True
    state.auto_dca_params[asset] = {"direction": direction, "base_size": base_size, "max_levels": max_levels, "spacing_pct": spacing_pct, "size_multiplier": size_multiplier, "tp_pct": tp_pct, "sl_pct": sl_pct, "leverage": leverage}
    state.auto_dca_consec_losses[asset] = 0
    state.save_state()

def deactivate_auto_dca(asset: str) -> None:
    state.auto_dca_active.pop(asset, None)
    state.auto_dca_params.pop(asset, None)
    state.auto_dca_consec_losses.pop(asset, None)
    state.save_state()

def get_active_engines() -> dict:
    return {k: v for k, v in state.auto_dca_active.items() if v}

async def handle_position_close_event(asset: str, pnl_usd: float, chat_id: str = "") -> None:
    if not state.auto_dca_active.get(asset, False):
        return
    if pnl_usd < 0:
        losses = state.auto_dca_consec_losses.get(asset, 0) + 1
        state.auto_dca_consec_losses[asset] = losses
    else:
        state.auto_dca_consec_losses[asset] = 0
    if state.auto_dca_consec_losses.get(asset, 0) >= 3:
        state.auto_dca_active[asset] = False
        state.save_state()
        return
    params = state.auto_dca_params.get(asset)
    if not params:
        return
    await asyncio.sleep(60)
    await _execute_reentry(asset, chat_id, params)

async def cmd_stop_auto_dca(update, context) -> None:
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /stop_auto_dca <ASSET>")
        return
    asset = args[0].upper()
    if asset in state.auto_dca_active:
        deactivate_auto_dca(asset)
        await update.message.reply_text(f"Auto-DCA stopped for {asset}")
    else:
        await update.message.reply_text(f"No active Auto-DCA for {asset}")
