"""MBIO DCA execution engine.

Owns DCA ladder lifecycle, fill reconciliation hooks, trailing maintenance,
profit-target checks, and close handling. Exchange order placement/cancellation
runs through ExecutionCoordinator; the base DCA entry retains the established
verified execute_hl_order path until the executor exposes a market-order method
through the coordinator.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, List

import core.state as state
from config_loader import get_config
from core.app_context import app_context
from core.execution_coordinator import ExecutionCoordinator, ExecutionResult
from core.market_cache import market_cache
from core.exchange_limits import get_exchange_limits

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DCAOrder:
    level: int
    price: float
    size: float
    side: str


class DCAExecutionEngine:
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
        is_long = side.upper() in {"BUY", "LONG"}
        order_side = "BUY" if is_long else "SELL"
        ladder: List[DCAOrder] = []
        for level in range(max(0, levels)):
            distance = spacing * (level + 1) / 100.0
            price = entry * (1 - distance) if is_long else entry * (1 + distance)
            ladder.append(DCAOrder(level + 1, round(price, 8), self.level_size(base_size, level, multiplier), order_side))
        return ladder

    @staticmethod
    def _orders_equivalent(existing: dict, desired: DCAOrder) -> bool:
        """Return True when an existing resting order already implements desired."""
        try:
            existing_side = str(existing.get("side", "")).upper()
            desired_side = str(desired.side).upper()
            existing_price = float(existing.get("price"))
            desired_price = float(desired.price)
            existing_size = float(existing.get("size"))
            desired_size = float(desired.size)
        except (TypeError, ValueError):
            return False

        price_tolerance = max(1e-8, abs(desired_price) * 1e-8)
        size_tolerance = max(1e-10, abs(desired_size) * 1e-8)
        return (
            (not existing_side or existing_side == desired_side)
            and abs(existing_price - desired_price) <= price_tolerance
            and abs(existing_size - desired_size) <= size_tolerance
        )

    async def _submit_limit(self, asset: str, order: DCAOrder) -> ExecutionResult:
        return await self.execution.submit_order(
            asset=asset,
            side=order.side,
            price=order.price,
            size=order.size,
            reduce_only=False,
            strategy="DCA",
            regime="AUTO",
            execution_label="DCA_LADDER",
            order_type="Limit",
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
        entry = float(position.get("entry", position.get("entry_price", 0)) or 0)
        if entry <= 0:
            logger.warning("DCA synchronize skipped for %s: invalid entry", asset)
            return

        ladder = self.build_ladder(
            entry=entry,
            side=str(position.get("side", dca.get("direction", "LONG"))),
            base_size=float(dca.get("base_size", position.get("size", 0)) or 0),
            levels=int(dca.get("levels", dca.get("max_levels", 3))),
            spacing=spacing,
            multiplier=float(dca.get("size_multiplier", 1.25)),
        )
        await self.replace_ladder(asset, ladder, dca)

    async def replace_ladder(self, asset: str, ladder: List[DCAOrder], dca: dict) -> None:
        """Reconcile the desired ladder without churning equivalent orders."""
        old_orders = list(dca.get("active_orders", []))
        used_old: set[int] = set()
        retained_orders = []
        orders_to_place: list[DCAOrder] = []

        for desired in ladder:
            match_index = next(
                (
                    index
                    for index, existing in enumerate(old_orders)
                    if index not in used_old
                    and str(existing.get("status", "OPEN")).upper() in {"OPEN", "ACTIVE"}
                    and self._orders_equivalent(existing, desired)
                ),
                None,
            )
            if match_index is None:
                orders_to_place.append(desired)
                continue

            used_old.add(match_index)
            retained = dict(old_orders[match_index])
            retained.update({
                "price": desired.price,
                "size": desired.size,
                "level": desired.level,
                "side": desired.side,
                "status": "OPEN",
            })
            retained_orders.append(retained)

        for index, old in enumerate(old_orders):
            if index in used_old:
                continue
            oid = old.get("order_id")
            status = str(old.get("status", "OPEN")).upper()
            if oid in (None, "", 0, "0") or status not in {"OPEN", "ACTIVE"}:
                continue
            try:
                result = await self._cancel(asset, oid)
                if not result.get("success"):
                    logger.error("DCA cancel rejected %s/%s: %s", asset, oid, result.get("error"))
            except Exception as exc:
                logger.error("DCA cancel failed %s/%s: %s", asset, oid, exc)

        new_orders = list(retained_orders)
        for order in orders_to_place:
            try:
                result = await self._submit_limit(asset, order)
            except Exception as exc:
                logger.error("DCA ladder submit failed %s level=%s: %s", asset, order.level, exc)
                continue
            if result.success:
                oid = result.payload.get("order_id", result.payload.get("oid"))
                if oid is not None:
                    new_orders.append({
                        "order_id": oid,
                        "price": order.price,
                        "size": order.size,
                        "level": order.level,
                        "side": order.side,
                        "status": "OPEN",
                    })

        dca["active_orders"] = new_orders
        dca.setdefault("filled_levels", [])
        self.active[asset] = dca
        state.save_state()
        logger.info(
            "DCA ladder synchronized %s (%d retained, %d submitted, %d desired)",
            asset,
            len(retained_orders),
            len(new_orders) - len(retained_orders),
            len(ladder),
        )

    async def on_fill(self, asset: str, position: dict) -> None:
        logger.info("DCA fill received %s", asset)
        await self.synchronize(asset, position)

    async def on_regime_change(self, asset: str, position: dict) -> None:
        logger.info("DCA market regime changed %s", asset)
        await self.synchronize(asset, position)

    async def close_position(self, asset: str, config: dict, close_side: str) -> dict:
        results = {"base_closed": False, "dca_cancelled": 0, "dca_closed": 0, "total_pnl": 0.0, "errors": []}

        for order in list(config.get("active_orders", [])):
            oid = order.get("order_id")
            if oid in (None, "", 0, "0"):
                continue
            try:
                result = await self._cancel(asset, oid)
                if result.get("success"):
                    results["dca_cancelled"] += 1
                else:
                    results["errors"].append(f"Cancel {oid}: {result.get('error')}")
            except Exception as exc:
                results["errors"].append(f"Cancel {oid}: {exc}")

        try:
            positions = await self.execution.get_open_positions()
            for pos in positions:
                if not isinstance(pos, dict) or pos.get("coin") != asset:
                    continue
                size = abs(float(pos.get("size", 0) or 0))
                if size <= 0:
                    continue
                from execution.hl_executor import execute_hl_order
                result = await asyncio.to_thread(
                    execute_hl_order,
                    coin=asset,
                    side=close_side,
                    size=size,
                    reduce_only=True,
                    strategy="AUTO_DCA",
                    regime="AUTO",
                    execution_label="DCA_EXIT",
                )
                if result.get("success"):
                    results["base_closed"] = True
                    results["dca_closed"] += 1
                    entry = float(pos.get("entry_price", 0) or 0)
                    exit_price = float(result.get("avg_price", entry) or entry)
                    results["total_pnl"] += ((exit_price - entry) * size if close_side == "SELL" else (entry - exit_price) * size)
                else:
                    results["errors"].append(f"Close failed: {result.get('error')}")
        except Exception as exc:
            results["errors"].append(f"Position close error: {exc}")

        config["enabled"] = False
        config["closed_at"] = datetime.now(timezone.utc).isoformat()
        self.active.pop(asset, None)
        try:
            async with state.STATE_LOCK:
                state.DCA_POSITIONS.pop(asset, None)
                state.save_state()
        except Exception as exc:
            results["errors"].append(f"State cleanup failed: {exc}")
        return results

    async def update_trailing_orders(self, asset: str, config: dict, current_price: float) -> dict:
        """Refresh the current DCA ladder through the active execution gateway."""
        position = state.OPEN_POSITIONS.get(asset)
        if not position or not config.get("enabled"):
            return {"updated": 0, "error": None}
        before = len(config.get("active_orders", []))
        await self.synchronize(asset, position)
        after = len(config.get("active_orders", []))
        return {"updated": after, "previous": before, "error": None}

    def check_profit_target(self, asset: str, config: dict, current_price: float) -> dict | None:
        position = state.OPEN_POSITIONS.get(asset)
        if not position or not config.get("enabled"):
            return None
        entry = float(position.get("entry", 0) or 0)
        size = abs(float(position.get("size", 0) or 0))
        if entry <= 0 or size <= 0:
            return None
        direction = str(config.get("direction", position.get("side", "LONG"))).upper()
        pnl_pct = ((current_price - entry) / entry * 100) if direction in {"LONG", "BUY"} else ((entry - current_price) / entry * 100)
        target = float(config.get("profit_target_pct", 0) or 0)
        if target > 0 and pnl_pct >= target:
            return {"pnl_pct": pnl_pct, "target_pct": target}
        return None

    async def close_dca_position(self, asset: str, config: dict, close_side: str) -> dict:
        return await self.close_position(asset, config, close_side)


dca_execution_engine = DCAExecutionEngine()


async def handle_dca_fill(*args, **kwargs):
    handler = getattr(dca_execution_engine, "handle_fill", None)
    return await handler(*args, **kwargs) if handler else None


def activate_auto_dca(asset: str, direction: str, base_size: float, max_levels: int = 3, spacing_pct: float = 1.2, size_multiplier: float = 1.25, tp_pct: float = 2.0, sl_pct: float = 2.5, leverage: float | None = None) -> None:
    state.auto_dca_active[asset] = True
    state.auto_dca_params[asset] = {
        "direction": direction, "base_size": base_size, "max_levels": max_levels,
        "spacing_pct": spacing_pct, "size_multiplier": size_multiplier,
        "tp_pct": tp_pct, "sl_pct": sl_pct, "leverage": leverage,
    }
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
    cfg = get_config()
    auto_cfg = cfg.get("auto_dca", {}) if isinstance(cfg, dict) else {}
    max_losses = int(auto_cfg.get("max_consecutive_losses", 3))
    cooldown = int(auto_cfg.get("reentry_cooldown_sec", 60))
    if pnl_usd < 0:
        losses = state.auto_dca_consec_losses.get(asset, 0) + 1
        state.auto_dca_consec_losses[asset] = losses
        if losses >= max_losses:
            state.auto_dca_active[asset] = False
            state.save_state()
            logger.error("Auto-DCA risk breaker tripped for %s", asset)
            return
    else:
        state.auto_dca_consec_losses[asset] = 0
    params = state.auto_dca_params.get(asset)
    if not params:
        return
    await asyncio.sleep(cooldown)
    if not state.auto_dca_active.get(asset, False) or asset in state.OPEN_POSITIONS:
        return
    await open_dca_position(asset=asset, side=params["direction"], investment_amount=float(params["base_size"]) * float(params.get("last_price", 0) or 0), overrides=params)


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


async def open_dca_position(asset: str, side: str, dca_strategy=None, exchange: str | None = None, overrides: dict | None = None, investment_amount: float | None = None) -> dict:
    """Open base DCA position and install its verified limit ladder.

    Supports both the dashboard/MCP investment interface and the legacy strategy
    caller. No legacy DCAManager is required.
    """
    asset = asset.upper()
    side = side.upper()
    if side not in {"LONG", "SHORT"}:
        return {"success": False, "error": "side must be LONG or SHORT"}

    cfg = get_config()
    dca_cfg = cfg.get("dca", {}) if isinstance(cfg, dict) else {}
    params = dict(dca_cfg)
    params.update(overrides or {})
    if investment_amount is None:
        investment_amount = float(params.get("investment", params.get("default_notional", cfg.get("execution", {}).get("default_notional", 10.0))))
    investment_amount = float(investment_amount)
    if investment_amount <= 0:
        return {"success": False, "error": "investment must be positive"}

    from core.data_fetcher import get_current_price
    current_price = float(get_current_price(f"{asset}-USD") or 0)
    if current_price <= 0:
        return {"success": False, "error": f"No live price available for {asset}"}

    base_size = investment_amount / current_price
    limits = get_exchange_limits()
    min_notional = float(limits.get("min_notional_usd", params.get("min_notional", 10.0)))
    if investment_amount < min_notional:
        return {"success": False, "error": f"Investment ${investment_amount:.2f} is below minimum ${min_notional:.2f}"}

    max_levels = int(params.get("max_levels", params.get("default_levels", 3)))
    spacing = float(params.get("spacing_pct", params.get("default_spacing_pct", 1.5)))
    multiplier = float(params.get("size_multiplier", params.get("default_multiplier", 1.3)))

    try:
        from execution.hl_executor import execute_hl_order
        result = await asyncio.to_thread(
            execute_hl_order,
            coin=asset,
            side="BUY" if side == "LONG" else "SELL",
            size=base_size,
            strategy="DCA",
            regime="AUTO",
            execution_label="DCA_ENTRY",
        )
        if not result.get("success"):
            return {"success": False, "error": result.get("error", "DCA base order failed")}

        entry_price = float(result.get("avg_price", current_price) or current_price)
        dca_state = {
            "enabled": True,
            "trailing": bool(params.get("trailing_enabled", True)),
            "direction": side,
            "levels": max_levels,
            "spacing_pct": spacing,
            "size_multiplier": multiplier,
            "base_size": base_size,
            "active_orders": [],
            "filled_levels": [],
            "total_invested": round(investment_amount, 2),
            "avg_entry": entry_price,
            "profit_target_pct": float(params.get("profit_target_pct", 0) or 0),
        }
        position = {
            "side": "BUY" if side == "LONG" else "SELL",
            "entry": entry_price,
            "size": base_size,
            "strategy": "MANUAL_DCA",
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "dca": dca_state,
        }
        state.OPEN_POSITIONS[asset] = position
        await dca_execution_engine.synchronize(asset, position)
        activate_auto_dca(asset, side, base_size, max_levels, spacing, multiplier, params.get("tp_pct", 2.0), params.get("sl_pct", 2.5), params.get("leverage"))
        state.auto_dca_params[asset]["last_price"] = entry_price
        state.save_state()

        return {"success": True, "message": f"DCA position opened: {asset} {side}", "asset": asset, "side": side, "entry": entry_price, "size": base_size, "dca_id": result.get("order_id"), "ladder_placed": len(dca_state["active_orders"])}
    except Exception as exc:
        logger.exception("DCA open failed for %s", asset)
        state.OPEN_POSITIONS.pop(asset, None)
        return {"success": False, "error": str(exc)}
