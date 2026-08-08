from core.market_cache import market_cache
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

MAX_CONSECUTIVE_LOSSES = 3
MIN_RR_RATIO = 1.5  # Minimum risk:reward ratio (TP vs SL) — prevents bad configs


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _get_dca_config():
    """Safe config reader with sensible, profitable defaults."""
    try:
        from config_loader import get_config
        return get_config().get("dca", {})
    except Exception as e:
        dca["_processing"] = False
        logger.warning(f"Config read failed, using defaults: {e}")
        return {}


def _get_manual_config():
    """Manual DCA config subsection."""
    return _get_dca_config().get("manual", {})


def _get_leverage() -> float:
    """Read account leverage from config. Hyperliquid default is 10x."""
    return float(_get_manual_config().get("leverage", 10.0))


def _get_safe_sl_buffer(leverage: float = None) -> float:
    """
    Return the MAXIMUM allowable SL distance (as decimal) before liquidation
    danger.  Formula: (1 / leverage) * 0.75 safety margin.
    """
    lev = leverage or _get_leverage()
    return (1.0 / lev) * 0.75


# ─────────────────────────────────────────────────────────────────────────────
# SHARED DCA LADDER PLACEMENT
# ─────────────────────────────────────────────────────────────────────────────

async def _place_dca_ladder(
    asset: str,
    direction: str,
    entry_price: float,
    base_size: float,
    max_levels: int,
    spacing_pct: float,
    size_multiplier: float,
    strategy_label: str = "AUTO_DCA",
    regime: str = "AUTO",
) -> list:
    """
    Places limit safety orders for DCA levels 1+.
    Returns a list of active order metadata dicts with real order_ids.
    """
    side = "BUY" if direction == "LONG" else "SELL"
    sign = -1.0 if direction == "LONG" else 1.0  # LONG: lower prices; SHORT: higher prices
    active_orders = []

    for lvl in range(1, max_levels + 1):
        lvl_size = base_size * (size_multiplier ** lvl)
        lvl_price = entry_price * (1 + sign * (spacing_pct * lvl) / 100.0)

        meta = {
            "level": lvl,
            "price": round(lvl_price, 2),
            "size": round(lvl_size, 8),
            "status": "pending",
            "order_id": None,
        }

        try:
            from execution.hl_executor import execute_hl_order
            result = execute_hl_order(
                coin=asset,
                side=side,
                size=lvl_size,
                limit_px=lvl_price,
                order_type="Limit",
                strategy=strategy_label,
                regime=regime,
                execution_label="DCA_ADD",
            )
            if result.get("success"):
                meta["status"] = "active"
                meta["order_id"] = result.get("order_id")
                logger.info(
                    f"📊 DCA Level {lvl}: {side} {lvl_size:.6f} @ ${lvl_price:.2f} "
                    f"(oid={meta['order_id']}) ✅"
                )
            else:
                meta["status"] = "failed"
                logger.warning(
                    f"⚠️ DCA Level {lvl} failed: {result.get('error')}"
                )
        except Exception as e:
            meta["status"] = "error"
            logger.warning(f"⚠️ DCA Level {lvl} error: {e}")

        active_orders.append(meta)

    return active_orders


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-DCA LIFECYCLE (Post-close re-entry)
# ─────────────────────────────────────────────────────────────────────────────


async def handle_dca_fill(asset: str, position: dict):


    processed = set(position.setdefault("_processed_dca_fills", []))

    level = None
    dca = position.get("dca", {})
    if dca.get("filled_levels"):
        level = dca["filled_levels"][-1]

    if level is not None:
        key = str(level)
        if key in processed:
            logger.debug("Skipping already processed DCA level %s", key)
            return
        processed.add(key)
        position["_processed_dca_fills"] = list(processed)

    """
    Continue DCA lifecycle after a safety order fills.
    """

    import core.state as state

    dca = position.get("dca")
    if not dca:
        return

    logger.info("🔄 Continuing DCA lifecycle for %s", asset)

    if dca.get("_processing"):
        return

    dca["_processing"] = True
    logger.info("position=%s", position)

    active_orders = await _place_dca_ladder(
        asset=asset,
        direction=dca.get("direction", "LONG"),
        entry_price=position.get("avg_entry", position["entry"]),
        base_size=dca["base_size"],
        max_levels=dca["levels"],
        spacing_pct=dca["spacing_pct"],
        size_multiplier=dca.get("size_multiplier", 1.0),
        strategy_label=position.get("strategy", "DCA"),
        regime="AUTO",
    )

    dca["active_orders"] = active_orders

    state.save_state()

    logger.info(
        "✅ DCA lifecycle completed %s (%d ladder orders)",
        asset,
        len(active_orders),
    )

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


async def _execute_reentry(asset: str, chat_id: str, params: dict = None) -> None:
    """Executes full multi-level DCA entry: market base + limit safety orders."""
    if params is None:
        params = state.auto_dca_params.get(asset, {})

    direction = params.get("direction", "LONG")
    base_size = params.get("base_size", 0.00025)
    max_levels = params.get("max_levels", 3)
    spacing_pct = params.get("spacing_pct", 1.2)
    size_multiplier = params.get("size_multiplier", 1.25)
    sl_pct = params.get("sl_pct", 2.5)
    tp_pct = params.get("tp_pct", 2.0)

    side = "BUY" if direction == "LONG" else "SELL"

    try:
        from execution.hl_executor import execute_hl_order
        from core.data_fetcher import get_current_price

        # Level 0: Market base order
        result = execute_hl_order(
            coin=asset, side=side, size=base_size,
            strategy="AUTO_DCA", regime="AUTO", execution_label="DCA_ENTRY"
        )

        if not result.get("success"):
            logger.error(f"❌ Auto-DCA base order failed for {asset}: {result.get('error')}")
            return

        entry_price = float(result.get("avg_price", 0))
        if entry_price == 0:
            entry_price = market_cache.price(f"{asset}-USD")

        logger.info(f"⚡ AUTO-DCA RE-ENTRY: {asset} {direction} @ ${entry_price:.2f} (base={base_size})")
        record_trade(
            "open", asset, "DCA", side, base_size, entry_price,
            metadata={"levels": max_levels, "spacing_pct": spacing_pct},
        )

        # Place limit safety orders via shared helper
        active_orders = await _place_dca_ladder(
            asset=asset,
            direction=direction,
            entry_price=entry_price,
            base_size=base_size,
            max_levels=max_levels,
            spacing_pct=spacing_pct,
            size_multiplier=size_multiplier,
            strategy_label="AUTO_DCA",
            regime="AUTO",
        )

        levels_placed = 1 + sum(1 for o in active_orders if o["status"] == "active")

        # Calculate SL/TP
        if direction == "LONG":
            sl_price = entry_price * (1 - sl_pct / 100)
            tp_price = entry_price * (1 + tp_pct / 100)
        else:
            sl_price = entry_price * (1 + sl_pct / 100)
            tp_price = entry_price * (1 - tp_pct / 100)

        state.OPEN_POSITIONS[asset] = {
            "side": "BUY" if direction == "LONG" else "SELL",
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
                "active_orders": active_orders,
                "filled_levels": [],
                "total_invested": 0.0,
                "avg_entry": entry_price,
            },
        }
        state.save_state()

        logger.info(
            f"🚀 Auto-DCA re-entry complete: {asset} | {levels_placed} levels | "
            f"SL=${sl_price:.2f} TP=${tp_price:.2f}"
        )

    except Exception as e:
        logger.error(f"❌ Auto-DCA re-entry failed for {asset}: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL DCA PLAN CALCULATOR  (Single Source of Truth)
# ─────────────────────────────────────────────────────────────────────────────

def _compute_dca_plan(asset: str, side: str, dca_strategy, exchange: str = None, overrides: dict = None) -> dict:
    """Pure DCA plan calculator — SINGLE SOURCE OF TRUTH."""
    from core.exchange_limits import get_effective_min_notional, get_exchange_limits, can_trade, is_exchange_configured
    import os

    asset = (asset or "").strip().upper()
    side = (side or "").strip().upper()
    exchange = (exchange or os.getenv("DEFAULT_EXCHANGE", "hyperliquid")).lower().strip()

    out: dict = {
        "can_execute": False, "errors": [], "warnings": [],
        "asset": asset, "side": side, "exchange": exchange,
        "price": None, "atr": None, "balance": None,
        "risk_pct": None, "risk_amount": None, "sl_distance": None,
        "base_size": None, "base_notional": None,
        "sl": None, "tp1": None, "tp2": None, "tp3": None, "trailing_stop": None,
        "max_levels": None, "spacing_pct": None, "size_multiplier": None,
        "ladder": [], "total_exposure": None, "exchange_min_notional": None,
        "leverage": None, "max_safe_sl_distance": None,
        "sl_pct": None, "tp_pct": None, "rr_ratio": None,
    }
    errors = out["errors"]
    warnings = out["warnings"]

    # Asset allow-list
    try:
        from config_loader import get_config
        _tradeable = [str(a).upper() for a in get_config().get("dca", {}).get("tradeable_assets", ["BTC", "ETH"])]
    except Exception:
        _tradeable = ["BTC", "ETH"]
    if asset not in _tradeable:
        errors.append(f"DCA not enabled for {asset}. Tradeable set: {', '.join(_tradeable)}.")
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
    leverage = float(m.get("leverage", 10.0))
    max_levels = int(m.get("max_levels", 3))
    spacing_pct = float(m.get("spacing_pct", 1.2))
    size_multiplier = float(m.get("size_multiplier", 1.25))

    ov = overrides or {}
    if ov.get("risk_pct") is not None:
        risk_pct = float(ov["risk_pct"])
    if ov.get("spacing_pct") is not None:
        spacing_pct = float(ov["spacing_pct"])
    if ov.get("size_multiplier") is not None:
        size_multiplier = float(ov["size_multiplier"])
    if ov.get("levels") is not None:
        max_levels = int(ov["levels"])
    if ov.get("leverage") is not None:
        leverage = float(ov["leverage"])

    out["risk_pct"] = risk_pct
    out["max_levels"] = max_levels
    out["spacing_pct"] = spacing_pct
    out["size_multiplier"] = size_multiplier
    out["leverage"] = leverage

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

    # ── LIQUIDATION-SAFE SL ──
    sl_distance = atr * dca_strategy.config.SL_ATR_MULT
    out["sl_distance"] = round(sl_distance, 2)

    max_safe_sl_distance = current_price * ((1.0 / leverage) * 0.75)
    out["max_safe_sl_distance"] = round(max_safe_sl_distance, 2)

    if sl_distance > max_safe_sl_distance:
        errors.append(
            f"ATR-based SL distance (${sl_distance:.2f}) exceeds safe limit "
            f"(${max_safe_sl_distance:.2f}) at {leverage}x leverage."
        )
        return out
    if sl_distance <= 0:
        errors.append("Invalid SL distance (zero or negative).")
        return out

    # ── SL / TP / TRAILING ──
    sign = 1.0 if side == "LONG" else -1.0
    sl_price = round(current_price - sign * sl_distance, 2)
    tp1 = round(current_price + sign * atr * dca_strategy.config.TP1_MULT, 2)
    tp2 = round(current_price + sign * atr * dca_strategy.config.TP2_MULT, 2)
    tp3 = round(current_price + sign * atr * dca_strategy.config.TP3_MULT, 2)
    trailing_stop = round(current_price - sign * atr * dca_strategy.config.TRAILING_ATR_MULT, 2)

    out["sl"] = sl_price
    out["tp1"] = tp1
    out["tp2"] = tp2
    out["tp3"] = tp3
    out["trailing_stop"] = trailing_stop

    # Risk/reward guard
    sl_pct = abs((sl_price - current_price) / current_price * 100)
    tp_pct = abs((tp1 - current_price) / current_price * 100)
    out["sl_pct"] = round(sl_pct, 2)
    out["tp_pct"] = round(tp_pct, 2)
    rr = (tp_pct / sl_pct) if sl_pct > 0 else 0
    out["rr_ratio"] = round(rr, 2)
    if rr < MIN_RR_RATIO:
        warnings.append(
            f"Risk/Reward ratio is {rr:.2f}:1 (minimum {MIN_RR_RATIO}:1). "
            f"TP1 ({tp_pct:.2f}%) is too close to entry vs SL ({sl_pct:.2f}%). "
            f"Consider increasing TP1 ATR multiplier in strategy config."
        )

    # User overrides
    liq_buffer = current_price * ((1.0 / leverage) * 0.75)
    if ov.get("sl") is not None:
        _sl = float(ov["sl"])
        if side == "LONG" and _sl >= current_price - liq_buffer:
            errors.append(f"SL ${_sl:.2f} too close to liquidation buffer.")
        elif side == "SHORT" and _sl <= current_price + liq_buffer:
            errors.append(f"SL ${_sl:.2f} too close to liquidation buffer.")
        else:
            out["sl"] = round(_sl, 2)
    if ov.get("tp1") is not None:
        out["tp1"] = round(float(ov["tp1"]), 2)
    if ov.get("tp2") is not None:
        out["tp2"] = round(float(ov["tp2"]), 2)
    if ov.get("tp3") is not None:
        out["tp3"] = round(float(ov["tp3"]), 2)
    if errors:
        return out

    # ── SIZE CALCULATION ──
    risk_amount = balance * risk_pct
    base_size = risk_amount / sl_distance if sl_distance > 0 else 0.0
    base_notional = round(base_size * current_price, 2)
    out["risk_amount"] = round(risk_amount, 2)
    out["base_size"] = round(base_size, 8)
    out["base_notional"] = base_notional

    if base_size <= 0:
        errors.append("Calculated size is too small.")
        return out

    # ── EXCHANGE MINIMUMS + AUTO-SCALE ──
    if not is_exchange_configured(exchange):
        errors.append(f"Exchange limits not configured for '{exchange}'.")
        return out

    limits = get_exchange_limits(exchange)
    raw_min = float(limits["min_notional_usd"])
    eff_min = get_effective_min_notional(exchange)
    out["exchange_min_notional"] = eff_min

    if base_notional < eff_min:
        scale = eff_min / base_notional if base_notional > 0 else 1.0
        base_size *= scale
        base_notional = round(base_size * current_price, 2)
        risk_amount = base_size * sl_distance
        out["base_size"] = round(base_size, 8)
        out["base_notional"] = base_notional
        out["risk_amount"] = round(risk_amount, 2)
        warnings.append(
            f"Auto-scaled {scale:.2f}x to meet {exchange} minimum "
            f"(raw ${raw_min:.2f}, safe ${eff_min:.2f}). "
            f"Effective risk: {(risk_amount / balance) * 100:.2f}%."
        )

    # ── LADDER CALCULATION ──
    ladder = []
    total_exposure = base_notional
    for lvl in range(1, max_levels + 1):
        lvl_size = base_size * (size_multiplier ** lvl)
        lvl_price = current_price * (1 - sign * (spacing_pct * lvl) / 100.0)
        notional = round(lvl_size * lvl_price, 2)
        total_exposure = round(total_exposure + notional, 2)
        meets = notional >= eff_min
        ladder.append({
            "level": lvl,
            "price": round(lvl_price, 2),
            "size": round(lvl_size, 8),
            "notional": notional,
            "meets_exchange_min": meets
        })
        if not meets:
            warnings.append(f"Ladder level {lvl} notional ${notional:.2f} below {exchange} minimum ${eff_min:.2f}.")

    out["ladder"] = ladder
    out["total_exposure"] = total_exposure

    if not can_trade(balance, exchange):
        warnings.append(f"Balance ${balance:.2f} below safe trading threshold on {exchange}.")

    if total_exposure > balance * 3:
        warnings.append(
            f"Total DCA exposure (${total_exposure:.2f}) is {(total_exposure / balance):.1f}x your balance. "
            f"Consider reducing max_levels or depositing more funds."
        )

    out["can_execute"] = True
    return out


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL DCA OPEN  (Single Source of Truth for execution)
# ─────────────────────────────────────────────────────────────────────────────

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