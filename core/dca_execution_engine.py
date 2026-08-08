
"""MBIO DCA Execution Engine

Adaptive DCA engine.

Responsibilities
----------------
• Maintain adaptive DCA ladders
• Expand/reduce ladders
• Cancel stale orders
• Replace orders
• React to fills
• Never talks directly to the exchange
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from core.execution_coordinator import ExecutionCoordinator
from core.market_cache import market_cache

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DCAOrder:

    level: int
    price: float
    size: float
    side: str


class DCAExecutionEngine:

    def __init__(self):

        self.active = {}

    ####################################################################
    # Adaptive spacing
    ####################################################################


    async def close_position(self, asset: str, config: dict, close_side: str) -> dict:
        """Close a DCA position using the legacy verified close semantics."""
        from datetime import datetime, timezone
        import core.state as state
        from execution.hl_executor import execute_hl_order
        from core.executor_utils import run_executor_method

        results = {
            "base_closed": False,
            "dca_cancelled": 0,
            "dca_closed": 0,
            "total_pnl": 0.0,
            "errors": [],
        }

        # Cancel all active DCA ladder orders first.
        for order in config.get("active_orders", []):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    cancel_result = await run_executor_method(
                        self.execution.cancel_order,
                        coin=asset,
                        order_id=int(order["order_id"]),
                    )
                    if cancel_result.get("success"):
                        results["dca_cancelled"] += 1
                        logger.info(
                            "🗑️ Cancelled DCA order %s for %s",
                            order["order_id"],
                            asset,
                        )
                    else:
                        results["errors"].append(
                            f"Cancel {order['order_id']}: "
                            f"{cancel_result.get('error')}"
                        )
                except Exception as e:
                    results["errors"].append(
                        f"Cancel error: {str(e)}"
                    )

        # Close every currently filled position for the asset.
        try:
            positions = (
                await run_executor_method(self.execution.get_open_positions)
            ) or []

            asset_positions = [
                pos for pos in positions
                if isinstance(pos, dict) and pos.get("coin") == asset
            ]

            for pos in asset_positions:
                size = float(pos.get("size", 0))
                if size <= 0:
                    continue

                close_result = execute_hl_order(
                    coin=asset,
                    side=close_side,
                    size=size,
                    reduce_only=True,
                    strategy="AUTO_DCA",
                    regime="AUTO",
                    execution_label="DCA_EXIT",
                )

                if close_result.get("success"):
                    results["base_closed"] = True
                    results["dca_closed"] += 1

                    entry = float(pos.get("entry_price", 0))
                    exit_price = float(
                        close_result.get("avg_price", entry)
                    )

                    pnl = (
                        (exit_price - entry) * size
                        if close_side == "SELL"
                        else (entry - exit_price) * size
                    )

                    results["total_pnl"] += pnl

                    logger.info(
                        "✅ Closed %s: %s @ $%s | PnL: $%+.4f",
                        asset,
                        size,
                        exit_price,
                        pnl,
                    )
                else:
                    results["errors"].append(
                        f"Close failed: {close_result.get('error')}"
                    )

        except Exception as e:
            results["errors"].append(
                f"Position close error: {str(e)}"
            )

        config["enabled"] = False
        config["closed_at"] = datetime.now(timezone.utc).isoformat()

        # Persist removal exactly once the close path has completed.
        async with state.STATE_LOCK:
            removed = state.DCA_POSITIONS.pop(asset, None)
            state.save_state()

            if removed:
                logger.info(
                    "🗑️ DCA position removed from state for %s | Total PnL: $%+.4f",
                    asset,
                    results["total_pnl"],
                )

        return results
    def spacing_pct(
        self,
        volatility: float,
        base: float = 1.20,
    ) -> float:

        if volatility < 0.01:
            return base

        if volatility < 0.02:
            return base * 1.20

        if volatility < 0.04:
            return base * 1.50

        return base * 2.00

    ####################################################################
    # Adaptive sizing
    ####################################################################

    def level_size(
        self,
        base_size: float,
        level: int,
        multiplier: float,
    ) -> float:

        return base_size * (multiplier ** level)

    ####################################################################
    # Build ladder
    ####################################################################

    def build_ladder(
        self,
        entry: float,
        side: str,
        base_size: float,
        levels: int,
        spacing: float,
        multiplier: float,
    ) -> List[DCAOrder]:

        ladder = []

        for level in range(levels):

            distance = spacing * (level + 1) / 100

            if side == "BUY":
                price = entry * (1 - distance)
            else:
                price = entry * (1 + distance)

            ladder.append(
                DCAOrder(
                    level=level + 1,
                    price=round(price, 2),
                    size=self.level_size(
                        base_size,
                        level,
                        multiplier,
                    ),
                    side=side,
                )
            )

        return ladder

    ####################################################################
    # Synchronize ladder
    ####################################################################

    async def synchronize(
        self,
        asset: str,
        position: dict,
    ):

        dca = position.get("dca")

        if not dca:
            return

        market = (
    market_cache.get(asset)
    if hasattr(market_cache, "get")
    else market_cache.snapshot().get(asset)
)

        volatility = market.get("volatility", 0.02)

        spacing = self.spacing_pct(
            volatility,
            dca.get("spacing_pct", 1.2),
        )

        ladder = self.build_ladder(
            entry=position["entry"],
            side=position["side"],
            base_size=dca["base_size"],
            levels=dca["levels"],
            spacing=spacing,
            multiplier=dca["size_multiplier"],
        )

        await self.replace_ladder(
            asset,
            ladder,
            dca,
        )

    ####################################################################
    # Replace ladder
    ####################################################################

    async def replace_ladder(
        self,
        asset: str,
        ladder: List[DCAOrder],
        dca: dict,
    ):

        existing = dca.get("active_orders", [])

        for order in existing:

            oid = order.get("order_id")

            if oid:

                await self.execution.cancel_order(
                    oid
                )

        dca["active_orders"] = []

        for order in ladder:

            result = await self.execution.submit_order(

                asset=asset,

                side=order.side,

                price=order.price,

                size=order.size,

                reduce_only=False,

                strategy="DCA",

            )

            if result.success:

                dca["active_orders"].append(
                    {
                        "order_id": result.payload.get("order_id"),
                        "price": order.price,
                        "size": order.size,
                        "level": order.level,
                        "status": "OPEN",
                    }
                )

        logger.info(
            "Adaptive DCA ladder synchronized %s (%d levels)",
            asset,
            len(dca["active_orders"]),
        )

    ####################################################################
    # Fill event
    ####################################################################

    async def on_fill(
        self,
        asset: str,
        position: dict,
    ):

        logger.info(
            "DCA fill received %s",
            asset,
        )

        await self.synchronize(
            asset,
            position,
        )

    ####################################################################
    # Regime change
    ####################################################################

    async def on_regime_change(
        self,
        asset: str,
        position: dict,
    ):

        logger.info(
            "Market regime changed %s",
            asset,
        )

        await self.synchronize(
            asset,
            position,
        )


dca_execution_engine = DCAExecutionEngine()


# ------------------------------------------------------------------
# Compatibility wrapper for legacy DCA fill monitor
# ------------------------------------------------------------------

async def handle_dca_fill(*args, **kwargs):
    if "dca_execution_engine" in globals() and hasattr(dca_execution_engine, "handle_fill"):
        return await dca_execution_engine.handle_fill(*args, **kwargs)
    return None


def activate_auto_dca(asset: str, direction: str, base_size: float,
                      max_levels: int = 3, spacing_pct: float = 1.2,
                      size_multiplier: float = 1.25, tp_pct: float = 2.0,
                      sl_pct: float = 2.5, leverage: float = None) -> None:
    """Activates Auto-DCA for an asset and persists the configuration."""
    state.auto_dca_active[asset] = True
    state.auto_dca_params[asset] = {
        "direction": direction,
        "base_size": base_size,
        "max_levels": max_levels,
        "spacing_pct": spacing_pct,
        "size_multiplier": size_multiplier,
        "tp_pct": tp_pct,
        "sl_pct": sl_pct,
        "leverage": leverage or _get_leverage(),
    }
    state.auto_dca_consec_losses[asset] = 0
    state.save_state()
    logger.info(
        f"🔄 Auto-DCA ACTIVATED: {asset} {direction} | "
        f"Levels={max_levels} Spacing={spacing_pct}% Mult={size_multiplier}x | "
        f"SL={sl_pct}% TP={tp_pct}%"
    )



def deactivate_auto_dca(asset: str) -> None:
    """Deactivates Auto-DCA for an asset."""
    state.auto_dca_active.pop(asset, None)
    state.auto_dca_params.pop(asset, None)
    state.auto_dca_consec_losses.pop(asset, None)
    state.save_state()
    logger.info(f"🛑 Auto-DCA DEACTIVATED: {asset}")



def get_active_engines() -> dict:
    """Returns currently active Auto-DCA configurations."""
    return {k: v for k, v in state.auto_dca_active.items() if v}



async def handle_position_close_event(asset: str, pnl_usd: float, chat_id: str = "") -> None:
    """Evaluates strategy metrics following a trade closure to coordinate auto-reentries."""
    logger.info(f"🏁 POSITION CLOSE EVENT: {asset} | PnL: ${pnl_usd:.4f}")

    if not state.auto_dca_active.get(asset, False):
        logger.info(f"ℹ️ Auto-DCA not active for {asset}. Skipping re-entry.")
        return

    # Risk Circuit Breaker
    if pnl_usd < 0:
        current_losses = state.auto_dca_consec_losses.get(asset, 0) + 1
        state.auto_dca_consec_losses[asset] = current_losses
        logger.warning(f"⚠️ Loss on {asset}. Consecutive losses: {current_losses}/{MAX_CONSECUTIVE_LOSSES}")
    else:
        state.auto_dca_consec_losses[asset] = 0
        logger.info(f"✅ Profitable exit on {asset}. Resetting loss counter.")

    if state.auto_dca_consec_losses.get(asset, 0) >= MAX_CONSECUTIVE_LOSSES:
        logger.error(f"🚨 RISK BREAK: Disarming Auto-DCA for {asset}")
        state.auto_dca_active[asset] = False
        state.save_state()
        return

    params = state.auto_dca_params.get(asset)
    if not params:
        logger.error(f"❌ Auto-DCA params missing for {asset}")
        return

    logger.info(f"⏳ Scheduling deferred re-entry for {asset} in 60s")
    await asyncio.sleep(60)
    await _execute_reentry(asset, chat_id, params)



async def cmd_stop_auto_dca(update, context) -> None:
    """Telegram command to stop Auto-DCA for an asset."""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /stop_auto_dca <ASSET>")
        return
    asset = args[0].upper()
    if asset in state.auto_dca_active:
        deactivate_auto_dca(asset)
        await update.message.reply_text(f"🛑 Auto-DCA stopped for {asset}")
    else:
        await update.message.reply_text(f"ℹ️ No active Auto-DCA for {asset}")

async def open_dca_position(asset: str, side: str, dca_strategy, exchange: str = None, overrides: dict = None) -> dict:
    """
    Shared DCA-open logic — places base order + limit ladder, builds state,
    and activates Auto-DCA with the computed ATR-based parameters.
    """
    plan = _compute_dca_plan(asset, side, dca_strategy, exchange=exchange, overrides=overrides)
    if not plan.get("can_execute"):
        err = (plan.get("errors") or ["Cannot open DCA position."])[0]
        return {"success": False, "error": err}

    asset = plan["asset"]
    side = plan["side"]
    current_price = plan["price"]
    base_size = plan["base_size"]
    max_levels = plan["max_levels"]
    spacing_pct = plan["spacing_pct"]
    size_multiplier = plan["size_multiplier"]
    sl_price = plan["sl"]
    tp1 = plan["tp1"]
    tp2 = plan["tp2"]
    tp3 = plan["tp3"]
    trailing_stop = plan["trailing_stop"]
    leverage = plan["leverage"]
    sl_pct = plan["sl_pct"]
    tp_pct = plan["tp_pct"]

    try:
        from execution.hl_executor import execute_hl_order

        # Level 0: Market base order
        result = execute_hl_order(
            coin=asset, side="BUY" if side == "LONG" else "SELL",
            size=base_size, strategy="DCA", regime="AUTO", execution_label="DCA_ENTRY"
        )
        if not result.get("success"):
            return {"success": False, "error": result.get("error", "Order failed")}

        entry_price = float(result.get("avg_price", 0)) or current_price

        # Place limit safety orders via shared helper
        active_orders = await _place_dca_ladder(
            asset=asset,
            direction=side,
            entry_price=entry_price,
            base_size=base_size,
            max_levels=max_levels,
            spacing_pct=spacing_pct,
            size_multiplier=size_multiplier,
            strategy_label="DCA",
            regime="AUTO",
        )

        from strategies.institutional_dca import PositionState
        pos = PositionState(
            asset=asset, side=side, size=base_size, entry_price=entry_price,
            active_so_count=0, last_order_price=entry_price,
            trailing_stop=trailing_stop,
        )
        dca_strategy.positions[asset] = pos

        state.OPEN_POSITIONS[asset] = {
            "side": "BUY" if side == "LONG" else "SELL",
            "entry": entry_price,
            "size": base_size,
            "sl": sl_price,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "order_id": result.get("order_id"),
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "strategy": "MANUAL_DCA",
            "dca": {
                "enabled": True,
                "trailing": True,
                "direction": side,
                "levels": max_levels,
                "spacing_pct": spacing_pct,
                "size_multiplier": size_multiplier,
                "base_size": base_size,
                "active_orders": active_orders,  # FIX: now contains real order_ids
                "filled_levels": [1],
                "total_invested": round(base_size * entry_price, 2),
                "avg_entry": entry_price,
            },
        }

        activate_auto_dca(
            asset=asset, direction=side, base_size=base_size,
            max_levels=max_levels, spacing_pct=spacing_pct, size_multiplier=size_multiplier,
            tp_pct=tp_pct, sl_pct=sl_pct, leverage=leverage,
        )

        levels_ok = sum(1 for o in active_orders if o["status"] == "active")
        logger.info(
            f"✅ DCA opened: {asset} {side} @ ${entry_price:.2f} | "
            f"Base={base_size:.6f} | Ladder={levels_ok}/{max_levels} filled | Auto-DCA ON"
        )
        return {
            "success": True,
            "message": (
                f"DCA Position Opened: {asset} {side} @ ${entry_price:.2f} | "
                f"Size: {base_size:.6f} | Ladder: {levels_ok}/{max_levels} | Auto-DCA ACTIVATED"
            ),
            "asset": asset, "side": side, "entry": entry_price, "size": base_size,
            "ladder_placed": levels_ok,
        }
    except Exception as e:
        logger.error(f"❌ Error opening DCA for {asset}: {e}")
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-DCA STATE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
