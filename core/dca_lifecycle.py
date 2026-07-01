"""
Automated DCA Lifecycle Engine for Hyperliquid.
Manages execution, tracking, sizing, and safety circuit breakers.
"""

import asyncio
import logging
import time
import core.state as state
from core.trade_ledger import record_trade

logger = logging.getLogger("DcaLifecycle")

MIN_NOTIONAL_TARGET = 11.50
MAX_CONSECUTIVE_LOSSES = 3


async def handle_position_close_event(asset: str, pnl_usd: float, chat_id: str = "") -> None:
    """Evaluates strategy metrics following a trade closure to coordinate auto-reentries.

    Parameters:
    - asset: The cryptocurrency token symbol (e.g., 'BTC', 'ETH')
    - pnl_usd: USD outcome from the recently terminated position
    - chat_id: Telegram chat ID for notifications (optional)
    """
    logger.info(f"🏁 POSITION CLOSE EVENT: {asset} | PnL: ${pnl_usd:.4f}")

    # Verify if asset has auto-DCA authorization enabled
    if not state.auto_dca_active.get(asset, False):
        logger.info(f"ℹ️ Auto-DCA not active for {asset}. Skipping re-entry.")
        return

    # Risk Circuit Breaker: Track consecutive losses
    if pnl_usd < 0:
        current_losses = state.auto_dca_consec_losses.get(asset, 0) + 1
        state.auto_dca_consec_losses[asset] = current_losses
        logger.warning(f"⚠️ Loss on {asset}. Consecutive losses: {current_losses}/{MAX_CONSECUTIVE_LOSSES}")
    else:
        state.auto_dca_consec_losses[asset] = 0
        logger.info(f"✅ Profitable exit on {asset}. Resetting loss counter.")

    # Kill auto-DCA if safety limits breached
    if state.auto_dca_consec_losses.get(asset, 0) >= MAX_CONSECUTIVE_LOSSES:
        logger.error(f"🚨 RISK BREAK: Disarming Auto-DCA for {asset} ({MAX_CONSECUTIVE_LOSSES} consecutive losses)")
        state.auto_dca_active[asset] = False
        state.save_state()
        return

    # Retrieve parameters
    params = state.auto_dca_params.get(asset)
    if not params:
        logger.error(f"❌ Auto-DCA params missing for {asset}")
        return

    # Cooldown to prevent API spam
    logger.info(f"⏳ Scheduling deferred re-entry for {asset} in 60s")
    await asyncio.sleep(60)

    # Execute re-entry
    await _execute_reentry(asset, chat_id, params)


async def _execute_reentry(asset: str, chat_id: str, params: dict = None) -> None:
    """Executes full multi-level DCA entry: market base + limit safety orders."""
    if params is None:
        params = state.auto_dca_params.get(asset, {})
    
    direction = params.get("direction", "LONG")
    base_size = params.get("base_size", 0.00025)
    max_levels = params.get("max_levels", 3)
    spacing_pct = params.get("spacing_pct", 1.2)
    size_multiplier = params.get("size_multiplier", 1.25)
    sl_pct = params.get("sl_pct", 4.0)
    tp_pct = params.get("tp_pct", 1.0)

    side = "BUY" if direction == "LONG" else "SELL"

    try:
        from execution.hl_executor import execute_hl_order
        from core.data_fetcher import get_current_price

        # Level 0: Market base order
        result = execute_hl_order(coin=asset, side=side, size=base_size, strategy="AUTO_DCA", regime="AUTO")
        
        if not result.get("success"):
            logger.error(f"❌ Auto-DCA base order failed for {asset}: {result.get('error')}")
            return

        entry_price = float(result.get("avg_price", 0))
        if entry_price == 0:
            entry_price = get_current_price(f"{asset}-USD")

        logger.info(f"⚡ AUTO-DCA RE-ENTRY: {asset} {direction} @ ${entry_price:.2f} (base={base_size})")
        record_trade("open", asset, "DCA", side, base_size, entry_price, metadata={"levels": max_levels, "spacing_pct": spacing_pct})

        # Place limit safety orders for levels 1+
        levels_placed = 1
        for lvl in range(1, max_levels + 1):
            lvl_size = base_size * (size_multiplier ** lvl)
            if direction == "LONG":
                lvl_price = entry_price * (1 - (spacing_pct * lvl) / 100)
            else:
                lvl_price = entry_price * (1 + (spacing_pct * lvl) / 100)

            try:
                lvl_result = execute_hl_order(
                    coin=asset, side=side, size=lvl_size,
                    limit_px=lvl_price, order_type="Limit",
                    strategy="AUTO_DCA", regime="AUTO"
                )
                if lvl_result.get("success"):
                    levels_placed += 1
                    logger.info(f"📊 Auto-DCA Level {lvl}: {side} {lvl_size:.4f} @ ${lvl_price:.2f} ✅")
                    # Capture order ID for later cancellation
                    _captured_oid = lvl_result.get("order_id")
                    if _captured_oid:
                        # Update the corresponding metadata entry
                        for _meta in state.OPEN_POSITIONS.get(asset, {}).get("dca", {}).get("active_orders", []):
                            if _meta.get("level") == lvl:
                                _meta["order_id"] = _captured_oid
                                break
                else:
                    logger.warning(f"⚠️ Auto-DCA Level {lvl} failed: {lvl_result.get('error')}")
            except Exception as e:
                logger.warning(f"⚠️ Auto-DCA Level {lvl} error: {e}")

        # Calculate SL/TP
        if direction == "LONG":
            sl_price = entry_price * (1 - sl_pct / 100)
            tp_price = entry_price * (1 + tp_pct / 100)
        else:
            sl_price = entry_price * (1 + sl_pct / 100)
            tp_price = entry_price * (1 - tp_pct / 100)

        # === UNIFIED STATE WITH DCA METADATA + ORDER IDS ===
        # Collect order IDs from placed DCA levels
        _reentry_order_ids = []
        _active_orders_meta = []
        for _lvl_idx in range(1, max_levels + 1):
            _lvl_sz = base_size * (size_multiplier ** _lvl_idx)
            if direction == "LONG":
                _lvl_px = entry_price * (1 - (spacing_pct * _lvl_idx) / 100)
            else:
                _lvl_px = entry_price * (1 + (spacing_pct * _lvl_idx) / 100)
            _active_orders_meta.append({
                "level": _lvl_idx,
                "price": round(_lvl_px, 2),
                "size": round(_lvl_sz, 8),
                "status": "active",
                "order_id": None,  # Populated below from placement results
            })

        state.OPEN_POSITIONS[asset] = {
            "side": side,
            "entry": entry_price,
            "size": base_size,
            "sl": sl_price,
            "tp1": tp_price,
            "strategy": "AUTO_DCA",
            "opened_at": time.time(),
            "dca": {
                "enabled": True,
                "levels": max_levels,
                "spacing_pct": spacing_pct,
                "multiplier": size_multiplier,
                "direction": direction,
                "base_size": base_size,
                "active_orders": _active_orders_meta,
                "filled_levels": [],
                "total_invested": 0.0,
                "avg_entry": entry_price,
            },
        }
        state.save_state()

        logger.info(f"🚀 Auto-DCA re-entry complete: {asset} | {levels_placed} levels | SL=${sl_price:.2f} TP=${tp_price:.2f} | DCA metadata embedded")

    except Exception as e:
        logger.error(f"❌ Auto-DCA re-entry failed for {asset}: {e}")


def activate_auto_dca(asset: str, direction: str, base_size: float,
                      max_levels: int = 3, spacing_pct: float = 1.2,
                      size_multiplier: float = 1.25, tp_pct: float = 1.0,
                      sl_pct: float = 4.0) -> None:
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
    }
    state.auto_dca_consec_losses[asset] = 0
    state.save_state()
    logger.info(f"🔄 Auto-DCA ACTIVATED: {asset} {direction} | Levels={max_levels} Spacing={spacing_pct}% Mult={size_multiplier}x")


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
