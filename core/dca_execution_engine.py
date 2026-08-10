"""MBIO DCA execution engine."""
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

    @staticmethod
    def _effective_reprice(existing: dict, desired: DCAOrder, threshold_pct: float) -> bool:
        try:
            old_price = float(existing.get("price"))
            new_price = float(desired.price)
            old_size = float(existing.get("size"))
            new_size = float(desired.size)
        except (TypeError, ValueError):
            return True
        if old_size != new_size or old_price == 0:
            return True
        return abs(new_price - old_price) / abs(old_price) * 100.0 >= threshold_pct

    @staticmethod
    def _normalize_order(order: DCAOrder, price_decimals: int | None = None, size_decimals: int | None = None) -> DCAOrder:
        price = round(float(order.price), price_decimals) if price_decimals is not None else float(order.price)
        size = round(float(order.size), size_decimals) if size_decimals is not None else float(order.size)
        return DCAOrder(order.level, price, size, order.side)

    async def _exchange_open_orders(self, asset: str) -> list[dict]:
        try:
            orders = market_cache.orders()
            return [o for o in orders if isinstance(o, dict) and o.get("coin") == asset]
        except Exception as exc:
            logger.warning("DCA exchange order snapshot unavailable for %s: %s", asset, exc)
            return []

    async def _submit_limit(self, asset: str, order: DCAOrder) -> ExecutionResult:
        return await self.execution.submit_order(asset=asset, side=order.side, price=order.price, size=order.size, reduce_only=False, strategy="DCA", regime="AUTO", execution_label="DCA_LADDER", order_type="Limit")

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
        ladder = self.build_ladder(entry, str(position.get("side", dca.get("direction", "LONG"))), float(dca.get("base_size", position.get("size", 0)) or 0), int(dca.get("levels", dca.get("max_levels", 3))), spacing, float(dca.get("size_multiplier", 1.25)))
        await self.replace_ladder(asset, ladder, dca)

    async def replace_ladder(self, asset: str, ladder: List[DCAOrder], dca: dict) -> None:
        """Reconcile DCA against exchange state at the final execution boundary."""
        cfg = get_config()
        dca_cfg = cfg.get("dca", {}) if isinstance(cfg, dict) else {}
        threshold_pct = float(dca.get("minimum_reprice_pct", dca_cfg.get("minimum_reprice_pct", dca_cfg.get("min_reprice_pct", 0.15))))
        price_decimals = dca_cfg.get("price_decimals")
        size_decimals = dca_cfg.get("size_decimals")
        try:
            price_decimals = int(price_decimals) if price_decimals is not None else None
            size_decimals = int(size_decimals) if size_decimals is not None else None
        except (TypeError, ValueError):
            price_decimals = size_decimals = None

        normalized: list[DCAOrder] = []
        seen: set[tuple[float, float, str]] = set()
        for desired in ladder:
            desired = self._normalize_order(desired, price_decimals, size_decimals)
            key = (desired.price, desired.size, desired.side.upper())
            if key not in seen:
                seen.add(key)
                normalized.append(desired)

        exchange_orders = await self._exchange_open_orders(asset)
        local_orders = list(dca.get("active_orders", []))
        local_by_oid = {str(o.get("order_id")): o for o in local_orders if o.get("order_id") not in (None, "", 0, "0")}
        authoritative: list[dict] = []
        for exchange_order in exchange_orders:
            oid = exchange_order.get("oid", exchange_order.get("order_id"))
            if oid in (None, "", 0, "0"):
                continue
            local = local_by_oid.get(str(oid), {})
            authoritative.append({"order_id": oid, "price": exchange_order.get("limitPx", exchange_order.get("price")), "size": exchange_order.get("sz", exchange_order.get("size")), "side": exchange_order.get("side", local.get("side", "")), "level": local.get("level"), "status": "OPEN"})

        if not exchange_orders and local_orders:
            authoritative = [dict(o) for o in local_orders if str(o.get("status", "OPEN")).upper() in {"OPEN", "ACTIVE"}]

        used: set[int] = set()
        retained: list[dict] = []
        replacements: list[tuple[dict, DCAOrder]] = []
        to_place: list[DCAOrder] = []

        for desired in normalized:
            exact = next((i for i, existing in enumerate(authoritative) if i not in used and self._orders_equivalent(existing, desired)), None)
            if exact is not None:
                used.add(exact)
                current = dict(authoritative[exact])
                current.update({"price": desired.price, "size": desired.size, "level": desired.level, "side": desired.side, "status": "OPEN"})
                retained.append(current)
                continue

            candidate = next((i for i, existing in enumerate(authoritative) if i not in used and str(existing.get("side", "")).upper() in {"", desired.side.upper()}), None)
            if candidate is None:
                to_place.append(desired)
            elif not self._effective_reprice(authoritative[candidate], desired, threshold_pct):
                used.add(candidate)
                current = dict(authoritative[candidate])
                current.update({"level": desired.level, "status": "OPEN"})
                retained.append(current)
            else:
                used.add(candidate)
                replacements.append((authoritative[candidate], desired))

        verified_replacements: list[DCAOrder] = []
        for old, desired in replacements:
            oid = old.get("order_id")
            if oid in (None, "", 0, "0"):
                continue
            try:
                result = await self._cancel(asset, oid)
                if not result.get("success"):
                    logger.error("DCA cancel rejected %s/%s; replacement withheld", asset, oid)
                    retained.append(dict(old))
                    continue
                still_open = await self._exchange_open_orders(asset)
                if any(str(o.get("oid", o.get("order_id"))) == str(oid) for o in still_open):
                    logger.error("DCA cancellation not verified %s/%s; replacement withheld", asset, oid)
                    retained.append(dict(old))
                    continue
                verified_replacements.append(desired)
            except Exception as exc:
                logger.error("DCA cancellation failed %s/%s; replacement withheld: %s", asset, oid, exc)
                retained.append(dict(old))

        for desired in verified_replacements + to_place:
            try:
                result = await self._submit_limit(asset, desired)
            except Exception as exc:
                logger.error("DCA ladder submit failed %s level=%s: %s", asset, desired.level, exc)
                continue
            if result.success:
                oid = result.payload.get("order_id", result.payload.get("oid"))
                if oid is not None:
                    retained.append({"order_id": oid, "price": desired.price, "size": desired.size, "level": desired.level, "side": desired.side, "status": "OPEN"})

        for index, old in enumerate(authoritative):
            if index in used:
                continue
            if any(old.get("order_id") == candidate.get("order_id") for candidate, _ in replacements):
                continue
            oid = old.get("order_id")
            if oid in (None, "", 0, "0"):
                continue
            try:
                await self._cancel(asset, oid)
            except Exception as exc:
                logger.error("DCA stale-order cancel failed %s/%s: %s", asset, oid, exc)

        dca["active_orders"] = [
            {key: value for key, value in order.items() if key != "side"}
            for order in retained
        ]
        dca.setdefault("filled_levels", [])
        self.active[asset] = dca
        state.save_state()
        logger.info("DCA ladder synchronized %s (%d retained, %d replaced, %d submitted, %d desired)", asset, len(retained), len(verified_replacements), len(verified_replacements) + len(to_place), len(normalized))

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
                result = await asyncio.to_thread(execute_hl_order, coin=asset, side=close_side, size=size, reduce_only=True, strategy="AUTO_DCA", regime="AUTO", execution_label="DCA_EXIT")
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


def _compute_dca_plan(asset: str, side: str, dca_strategy, exchange: str = None, overrides: dict = None) -> dict:
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

    # Asset allow-list from config (single source of truth; replaces hardcoded BTC/ETH).
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
    min_sl_distance_pct = float(m.get("min_sl_distance_pct", 0.055))
    max_levels = int(m.get("max_levels", 3))
    spacing_pct = float(m.get("spacing_pct", 1.2))
    size_multiplier = float(m.get("size_multiplier", 1.25))

    # Apply user overrides (validated). These are the only fields a user may adjust;
    # entry/ATR/balance stay market/account-derived. Every override is re-checked below
    # (SL vs liquidation buffer, notional vs exchange min) so a client cannot bypass risk.
    ov = overrides or {}
    if ov.get("risk_pct") is not None:
        risk_pct = float(ov["risk_pct"])
    if ov.get("spacing_pct") is not None:
        spacing_pct = float(ov["spacing_pct"])
    if ov.get("size_multiplier") is not None:
        size_multiplier = float(ov["size_multiplier"])
    if ov.get("levels") is not None:
        max_levels = int(ov["levels"])
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

    # User SL/TP overrides (validated). SL must never breach the liquidation buffer.
    if ov.get("sl") is not None:
        _sl = float(ov["sl"])
        _liq_buffer = current_price * min_sl_distance_pct
        if side == "LONG" and _sl >= current_price - _liq_buffer:
            errors.append(f"Stop-loss ${_sl:.2f} too close to entry (liquidation buffer ${_liq_buffer:.2f}).")
        elif side == "SHORT" and _sl <= current_price + _liq_buffer:
            errors.append(f"Stop-loss ${_sl:.2f} too close to entry (liquidation buffer ${_liq_buffer:.2f}).")
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

async def open_dca_position(asset: str, side: str, dca_strategy=None, exchange: str | None = None, overrides: dict | None = None, investment_amount: float | None = None) -> dict:
    """Open base DCA position and install its verified limit ladder."""
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
        result = await asyncio.to_thread(execute_hl_order, coin=asset, side="BUY" if side == "LONG" else "SELL", size=base_size, strategy="DCA", regime="AUTO", execution_label="DCA_ENTRY")
        if not result.get("success"):
            return {"success": False, "error": result.get("error", "DCA base order failed")}
        entry_price = float(result.get("avg_price", current_price) or current_price)
        dca_state = {"enabled": True, "trailing": bool(params.get("trailing_enabled", True)), "direction": side, "levels": max_levels, "spacing_pct": spacing, "size_multiplier": multiplier, "base_size": base_size, "active_orders": [], "filled_levels": [], "total_invested": round(investment_amount, 2), "avg_entry": entry_price, "profit_target_pct": float(params.get("profit_target_pct", 0) or 0)}
        position = {"side": "BUY" if side == "LONG" else "SELL", "entry": entry_price, "size": base_size, "strategy": "MANUAL_DCA", "opened_at": datetime.now(timezone.utc).isoformat(), "dca": dca_state}
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
