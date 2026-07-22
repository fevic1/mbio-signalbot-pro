"""
Automated DCA Lifecycle Engine for Hyperliquid.
Manages execution, tracking, sizing, and safety circuit breakers.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
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
            # NOTE: stored as BUY/SELL, not LONG/SHORT — check_and_close_positions()
            # in monitoring/position_tracker.py compares against "BUY" literally, and
            # storing "LONG" here silently broke the close logic (it would re-enter
            # same-direction instead of closing, doubling exposure). See tonight's
            # DCA-position-doubling incident.
            "side": "BUY" if side == "LONG" else "SELL",
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


def _compute_dca_plan(asset: str, side: str, dca_strategy, exchange: str = None) -> dict:
    """Pure DCA plan calculator — the SINGLE SOURCE OF TRUTH for the manual DCA
    open path. Read-only: NO state mutation, NO orders, so it is safe to serve
    from the dashboard preview endpoint. Consumed by GET /dca/preview (show the
    plan before OTP) and, after STEP B, by open_dca_position (execute the plan).
    One computation shared by both guarantees the preview can never drift from
    what executes. (CODING_STANDARD: No duplicated business logic, No magic
    numbers.) Exchange-agnostic: every exchange minimum is read from
    core.exchange_limits keyed by the resolved exchange — NO floor literal lives
    here, so adding Vertex/Bybit later cannot inherit Hyperliquid's numbers.
    Every terminal path returns the full stable key-set so the modal can always
    render the numbers it computed — including on rejection."""
    from core.exchange_limits import get_effective_min_notional, get_exchange_limits, can_trade, is_exchange_configured
    import os

    asset = (asset or "").strip().upper()
    side = (side or "").strip().upper()
    # Resolve target exchange once. DEFAULT_EXCHANGE is config plumbing (which
    # exchange to target), NOT a minimum value — the minimums come from limits.
    exchange = (exchange or os.getenv("DEFAULT_EXCHANGE", "hyperliquid")).lower().strip()

    # Stable UI contract: every key always present (None until computed).
    out: dict = {
        "can_execute": False, "errors": [], "warnings": [],
        "asset": asset, "side": side, "exchange": exchange,
        "price": None, "atr": None, "balance": None,
        "risk_pct": None, "risk_amount": None, "sl_distance": None,
        "base_size": None, "base_notional": None,
        "sl": None, "tp1": None, "tp2": None, "tp3": None, "trailing_stop": None,
        "max_levels": None, "spacing_pct": None, "size_multiplier": None,
        "ladder": [], "total_exposure": None, "exchange_min_notional": None,
    }
    errors = out["errors"]
    warnings = out["warnings"]

    if asset not in ("BTC", "ETH"):
        errors.append("DCA Strategy only supports BTC and ETH.")
    if side not in ("LONG", "SHORT"):
        errors.append("Side must be LONG or SHORT.")
    if errors:
        return out
    if asset in state.OPEN_POSITIONS:
        errors.append(f"{asset} already has an active position in global state.")
    if asset in getattr(dca_strategy, "positions", {}):
        errors.append(f"{asset} already has an active DCA position.")
    if errors:
        return out

    try:
        from config_loader import get_config
        m = get_config().get("dca", {}).get("manual", {})
    except Exception as e:
        logger.error(f"DCA config read failed: {e}")
        m = {}
    risk_pct = float(m.get("risk_pct", 0.01))
    min_sl_distance_pct = float(m.get("min_sl_distance_pct", 0.055))
    max_levels = int(m.get("max_levels", 3))
    spacing_pct = float(m.get("spacing_pct", 1.2))
    size_multiplier = float(m.get("size_multiplier", 1.25))
    out["risk_pct"] = risk_pct
    out["max_levels"] = max_levels
    out["spacing_pct"] = spacing_pct
    out["size_multiplier"] = size_multiplier

    try:
        from core.data_fetcher import get_mtf_data, get_account_balance
        data = get_mtf_data(f"{asset}-USD")
        if not data or "1h" not in data:
            errors.append("Failed to fetch market data.")
            return out
        current_price = float(data["1h"]["price"])
        atr = float(data["1h"]["atr"])
        balance = float(get_account_balance())
        out["price"] = round(current_price, 2)
        out["atr"] = round(atr, 2)
        out["balance"] = round(balance, 2)
    except Exception as e:
        logger.error(f"DCA plan market-data fetch failed for {asset}: {e}")
        errors.append(f"Market data unavailable: {e}")
        return out

    sl_distance = atr * dca_strategy.config.SL_ATR_MULT
    out["sl_distance"] = round(sl_distance, 2)
    if side == "LONG" and sl_distance > (current_price * min_sl_distance_pct):
        errors.append("ATR too high for safe SL placement at current leverage. Risk of liquidation.")
        return out

    # SL/TP computed BEFORE the size gate so a blocked plan still shows intended risk levels.
    sign = 1.0 if side == "LONG" else -1.0
    out["sl"] = round(current_price - sign * sl_distance, 2)
    out["tp1"] = round(current_price + sign * atr * dca_strategy.config.TP1_MULT, 2)
    out["tp2"] = round(current_price + sign * atr * dca_strategy.config.TP2_MULT, 2)
    out["tp3"] = round(current_price + sign * atr * dca_strategy.config.TP3_MULT, 2)
    out["trailing_stop"] = round(current_price - sign * atr * dca_strategy.config.TRAILING_ATR_MULT, 2)

    risk_amount = balance * risk_pct
    base_size = risk_amount / sl_distance if sl_distance > 0 else 0.0
    base_notional = round(base_size * current_price, 2)
    out["risk_amount"] = round(risk_amount, 2)
    out["base_size"] = round(base_size, 8)
    out["base_notional"] = base_notional
    if base_size <= 0:
        errors.append("Calculated size is too small.")
        return out

    # Exchange minimums: read from the exchange-keyed authority ONLY. No floor
    # literal here. Missing config for the target exchange is a hard, explicit
    # block — it forces the operator to add the exchange's limits before trading.
    if not is_exchange_configured(exchange):
        errors.append(f"Exchange limits not configured for '{exchange}'. Add a '{exchange}' block to config/exchange_limits.yaml before trading on it.")
        return out
    limits = get_exchange_limits(exchange)
    raw_min = float(limits["min_notional_usd"])
    eff_min = get_effective_min_notional(exchange)
    out["exchange_min_notional"] = eff_min
    if base_notional < raw_min:
        errors.append(f"Base order notional ${base_notional:.2f} below {exchange} minimum ${raw_min:.2f}. Increase dca.manual.risk_pct or account balance.")
        return out
    if base_notional < eff_min:
        warnings.append(f"Base notional ${base_notional:.2f} below safe buffer ${eff_min:.2f}; order may be rejected on slippage.")

    ladder = []
    total_exposure = base_notional
    for lvl in range(1, max_levels + 1):
        lvl_size = base_size * (size_multiplier ** lvl)
        lvl_price = current_price * (1 - sign * (spacing_pct * lvl) / 100.0)
        notional = round(lvl_size * lvl_price, 2)
        total_exposure = round(total_exposure + notional, 2)
        meets = notional >= eff_min
        ladder.append({"level": lvl, "price": round(lvl_price, 2), "size": round(lvl_size, 8), "notional": notional, "meets_exchange_min": meets})
        if not meets:
            warnings.append(f"Ladder level {lvl} notional ${notional:.2f} below {exchange} minimum ${eff_min:.2f}.")
    out["ladder"] = ladder
    out["total_exposure"] = total_exposure

    if not can_trade(balance, exchange):
        warnings.append(f"Balance ${balance:.2f} below safe trading threshold on {exchange}.")

    out["can_execute"] = True
    return out


async def open_dca_position(asset: str, side: str, dca_strategy) -> dict:
    """
    Shared DCA-open logic — the single source of truth for opening a new DCA
    position. Used by both the Telegram /open_dca command and the dashboard's
    /dca/open endpoint, so the two callers cannot drift apart.

    ALL sizing, SL/TP, exchange-minimum and config validation is delegated to
    _compute_dca_plan() — the SAME pure calculator the dashboard preview serves —
    so what the user previews is exactly what executes. (CODING_STANDARD: No
    duplicated business logic, No magic numbers.) This function adds only the
    side effects: place the base order, build state, activate Auto-DCA.

    Returns a result dict: {"success": bool, "message": str, ...details}
    """
    # Delegate all computation/validation to the single source of truth.
    plan = _compute_dca_plan(asset, side, dca_strategy)
    if not plan.get("can_execute"):
        err = (plan.get("errors") or ["Cannot open DCA position."])[0]
        return {"success": False, "error": err}

    # Unpack the validated, config-sourced plan (no literals here).
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

    try:
        from execution.hl_executor import execute_hl_order
        result = execute_hl_order(
            coin=asset, side="BUY" if side == "LONG" else "SELL",
            size=base_size, strategy="DCA", regime="AUTO"
        )
        if not result.get("success"):
            return {"success": False, "error": result.get("error", "Order failed")}

        from strategies.institutional_dca import PositionState
        pos = PositionState(
            asset=asset, side=side, size=base_size, entry_price=current_price,
            active_so_count=0, last_order_price=current_price,
            trailing_stop=trailing_stop,
        )
        dca_strategy.positions[asset] = pos

        state.OPEN_POSITIONS[asset] = {
            # NOTE: stored as BUY/SELL, not LONG/SHORT — check_and_close_positions()
            # compares against "BUY" literally (see _execute_reentry note).
            "side": "BUY" if side == "LONG" else "SELL",
            "entry": current_price,
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
                "trailing": True,  # REQUIRED for background task to manage orders
                "direction": side,
                "levels": max_levels,
                "spacing_pct": spacing_pct,
                "size_multiplier": size_multiplier,
                "base_size": base_size,
                "active_orders": [],  # Populated by dca_manager
                "filled_levels": [1],  # Level 1 (base) is filled
                "total_invested": round(base_size * current_price, 2),
                "avg_entry": current_price,
            },
        }

        activate_auto_dca(
            asset=asset, direction=side, base_size=base_size,
            max_levels=max_levels, spacing_pct=spacing_pct, size_multiplier=size_multiplier,
            tp_pct=1.0, sl_pct=4.0,
        )

        logger.info(f"✅ DCA opened via open_dca_position: {asset} {side} @ ${current_price:.2f}")
        return {
            "success": True,
            "message": f"DCA Position Opened: {asset} {side} @ ${current_price:.2f} | Size: {base_size:.4f} | Auto-DCA ACTIVATED",
            "asset": asset, "side": side, "entry": current_price, "size": base_size,
        }
    except Exception as e:
        logger.error(f"❌ Error opening DCA for {asset}: {e}")
        return {"success": False, "error": str(e)}


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
