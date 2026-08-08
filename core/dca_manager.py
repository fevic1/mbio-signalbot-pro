"""
core/dca_manager.py — Adaptive professional DCA engine.

The engine keeps the DCA ladder live, but never lets an LLM bypass deterministic
risk controls. AI/learner output is advisory and is normalized before execution.
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import core.state as state
from config_loader import get_config
from core.adaptive_dca import (
    AdaptiveDCAConfig,
    DCAAction,
    MarketSnapshot,
    evaluate_dca_order,
)
from core.executor_utils import run_executor_method

logger = logging.getLogger(__name__)


class DCAManager:
    """Manages DCA strategies, adaptive repricing, and guarded acceleration."""

    def __init__(self, executor):
        self.executor = executor
        self.active_dca: Dict[str, Dict] = {}

    def enable_dca(
        self,
        asset: str,
        levels: int = 3,
        spacing_pct: float = 1.2,
        multiplier: float = 1.25,
        direction: str = "LONG",
        base_size: float = 0.00025,
        trailing: bool = False,
        trailing_offset_pct: float = 0.8,
        profit_target_pct: float = 0.0,
    ) -> Dict:
        config = {
            "enabled": True,
            "levels": max(1, int(levels)),
            "spacing_pct": max(0.01, float(spacing_pct)),
            "multiplier": max(1.0, float(multiplier)),
            "direction": direction.upper(),
            "base_size": float(base_size),
            "trailing": bool(trailing),
            "trailing_offset_pct": max(0.01, float(trailing_offset_pct)),
            "profit_target_pct": max(0.0, float(profit_target_pct)),
            "active_orders": [],
            "filled_levels": [],
            "total_invested": 0.0,
            "avg_entry": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "adaptive": {
                "enabled": True,
                "aggressive_enabled": True,
                "order_ttl_seconds": 45.0,
                "monitor_interval_sec": 10.0,
                "ai_review_interval_sec": 45.0,
                "acceleration_confidence": 0.72,
                "min_learner_score": 0.60,
                "max_acceleration_multiplier": 1.25,
            },
        }
        self.active_dca[asset] = config
        logger.info(
            "Adaptive DCA activated: %s %s | levels=%s spacing=%.3f%% multiplier=%.3fx",
            asset,
            direction,
            config["levels"],
            config["spacing_pct"],
            config["multiplier"],
        )
        return config

    def calculate_dca_levels(
        self, entry_price: float, base_size: float, config: Dict
    ) -> List[Dict]:
        levels = []
        current_size = base_size * config["multiplier"]
        direction = config.get("direction", "LONG")
        for i in range(1, int(config["levels"]) + 1):
            if direction == "LONG":
                level_price = entry_price * (1 - config["spacing_pct"] / 100 * i)
            else:
                level_price = entry_price * (1 + config["spacing_pct"] / 100 * i)
            levels.append(
                {
                    "level": i,
                    "price": round(level_price, 2),
                    "size": round(current_size, 8),
                    "status": "pending",
                    "order_id": None,
                }
            )
            current_size *= config["multiplier"]
        return levels

    def calculate_trailing_levels(
        self, entry_price: float, current_price: float, base_size: float, config: Dict
    ) -> List[Dict]:
        if current_price >= entry_price:
            return self.calculate_dca_levels(entry_price, base_size, config)
        trailing_offset = config.get("trailing_offset_pct", config["spacing_pct"])
        current_level_price = current_price * (1 - trailing_offset / 100)
        current_size = base_size * config["multiplier"]
        levels = []
        for i in range(1, int(config["levels"]) + 1):
            levels.append(
                {
                    "level": i,
                    "price": round(current_level_price, 2),
                    "size": round(current_size, 8),
                    "status": "pending",
                    "order_id": None,
                    "trailing": True,
                }
            )
            current_level_price *= 1 - config["spacing_pct"] / 100
            current_size *= config["multiplier"]
        return levels

    def should_pause_dca(self, asset: str, current_price: float) -> bool:
        """Apply the existing large-drop guardrail before adding exposure."""
        if current_price <= 0:
            return True
        cfg = get_config().get("dca", {})
        threshold = float(cfg.get("pause_on_large_drop_pct", 0.0) or 0.0)
        if threshold <= 0:
            return False
        position = state.OPEN_POSITIONS.get(asset, {})
        anchor = float(
            position.get("entry", 0)
            or position.get("entry_price", 0)
            or state.DCA_POSITIONS.get(asset, {}).get("entry_price", 0)
            or 0
        )
        if anchor <= 0:
            return False
        direction = str(position.get("side", "BUY")).upper()
        adverse_drop = (
            (anchor - current_price) / anchor * 100
            if direction in {"BUY", "LONG"}
            else (current_price - anchor) / anchor * 100
        )
        return adverse_drop >= threshold

    async def _submit_limit(self, asset: str, side: str, size: float, price: float, label: str) -> dict:
        from execution.hl_executor import execute_hl_order

        return await asyncio.to_thread(
            execute_hl_order,
            coin=asset,
            side=side,
            size=size,
            limit_price=price,
            order_type="Limit",
            strategy="AUTO_DCA",
            regime="AUTO",
            execution_label=label,
        )

    async def _submit_aggressive(self, asset: str, side: str, size: float, label: str) -> dict:
        """Use the verified executor's marketable-limit path, not an unbounded market order."""
        from execution.hl_executor import execute_hl_order

        return await asyncio.to_thread(
            execute_hl_order,
            coin=asset,
            side=side,
            size=size,
            strategy="AUTO_DCA",
            regime="AUTO",
            execution_label=label,
        )

    async def _cancel_order(self, asset: str, order_id: int) -> dict:
        return await run_executor_method(
            self.executor.cancel_order, coin=asset, order_id=int(order_id)
        )

    async def place_dca_orders(
        self, asset: str, entry_price: float, base_size: float, config: Dict
    ) -> List[Dict]:
        if self.should_pause_dca(asset, entry_price):
            logger.warning("DCA paused for %s by large-drop guardrail", asset)
            return []

        levels = self.calculate_dca_levels(entry_price, base_size, config)
        placed = []
        side = "BUY" if config.get("direction", "LONG") == "LONG" else "SELL"

        for level in levels:
            try:
                result = await self._submit_limit(
                    asset, side, level["size"], level["price"], "DCA_ENTRY"
                )
                if result.get("success"):
                    level["order_id"] = result.get("order_id")
                    level["status"] = "active"
                    level["placed_at"] = datetime.now(timezone.utc).isoformat()
                    level["placed_at_ts"] = time.time()
                    placed.append(level)
                    logger.info(
                        "DCA level %s placed: %s %s %.8f @ %.8f",
                        level["level"],
                        asset,
                        side,
                        level["size"],
                        level["price"],
                    )
                else:
                    logger.warning(
                        "DCA level %s failed for %s: %s",
                        level["level"],
                        asset,
                        result.get("error"),
                    )
            except Exception as exc:
                logger.error("DCA order placement failed %s/L%s: %s", asset, level["level"], exc)

        config["active_orders"] = placed
        config["is_waiting_for_fill"] = False
        config["last_monitor_ts"] = time.time()

        if placed:
            async with state.STATE_LOCK:
                state.DCA_POSITIONS[asset] = {
                    "entry_price": entry_price,
                    "base_size": base_size,
                    "direction": config.get("direction", "LONG"),
                    "levels": placed,
                    "is_waiting_for_fill": False,
                    "last_fill_price": config.get("last_fill_price", entry_price),
                    "opened_at": datetime.now(timezone.utc).isoformat(),
                }
                state.save_state()
        return placed

    def _adaptive_config(self, config: Dict) -> AdaptiveDCAConfig:
        adaptive = config.get("adaptive", {}) or {}
        return AdaptiveDCAConfig(
            enabled=bool(adaptive.get("enabled", True)),
            aggressive_enabled=bool(adaptive.get("aggressive_enabled", True)),
            order_ttl_seconds=max(10.0, float(adaptive.get("order_ttl_seconds", 45.0))),
            min_reprice_distance_pct=max(
                0.01, float(adaptive.get("min_reprice_distance_pct", 0.15))
            ),
            acceleration_confidence=max(
                0.50, min(1.0, float(adaptive.get("acceleration_confidence", 0.72)))
            ),
            min_learner_score=max(
                0.0, min(1.0, float(adaptive.get("min_learner_score", 0.60)))
            ),
            max_acceleration_multiplier=max(
                1.0, min(1.25, float(adaptive.get("max_acceleration_multiplier", 1.25)))
            ),
            max_order_age_seconds=max(
                30.0, float(adaptive.get("max_order_age_seconds", 300.0))
            ),
        )

    async def _ai_advice(
        self, asset: str, config: Dict, market_data: dict, now_ts: float
    ) -> dict:
        """Ask the existing multi-provider AI path only when an order needs review."""
        adaptive = config.setdefault("adaptive", {})
        review_interval = max(15.0, float(adaptive.get("ai_review_interval_sec", 45.0)))
        last_review = float(adaptive.get("last_ai_review_ts", 0.0) or 0.0)
        if now_ts - last_review < review_interval:
            return config.get("last_ai_advice", {})

        adaptive["last_ai_review_ts"] = now_ts
        try:
            from core.signal_generator import analyze_batch
            from core.meta_learner import get_meta_learner
            from core.regime import detect_regime

            cfg = get_config()
            result, provider = await analyze_batch({asset: market_data}, cfg)
            item = result.get(asset, {})
            signal = str(item.get("signal", "HOLD")).upper()
            confidence = max(0.0, min(1.0, float(item.get("confidence", 0)) / 100.0))

            regime = detect_regime(market_data.get("4h", {}))
            learner_score = float(
                get_meta_learner().get_weights(regime).get("LLM", 0.0)
            )
            direction = str(config.get("direction", "LONG")).upper()
            aligned = (
                direction == "LONG" and signal in {"BUY", "STRONG BUY"}
            ) or (
                direction == "SHORT" and signal in {"SELL", "STRONG SELL"}
            )
            advice = {
                "action": "ACCELERATE" if aligned else "WAIT",
                "confidence": confidence,
                "learner_score": max(0.0, min(1.0, learner_score)),
                "max_price": float(market_data.get("1h", {}).get("price", 0) or 0),
                "size_multiplier": min(
                    1.25, float(adaptive.get("max_acceleration_multiplier", 1.25))
                ),
                "valid_for_seconds": review_interval,
                "reason": (
                    f"{provider} {signal} ({confidence:.0%}); "
                    f"MetaLearner LLM weight={learner_score:.2f}"
                ),
            }
            config["last_ai_advice"] = advice
            return advice
        except Exception as exc:
            logger.warning("Adaptive DCA AI review failed for %s: %s", asset, exc)
            config["last_ai_advice"] = {}
            return {}

    async def _risk_budget_allows_acceleration(
        self, asset: str, config: Dict, proposed_size: float, price: float
    ) -> bool:
        """Cap aggregate DCA notional using live equity; fail closed if equity is unavailable."""
        dca_cfg = get_config().get("dca", {})
        max_pct = float(dca_cfg.get("max_total_dca_exposure_pct", 0.0) or 0.0)
        if max_pct <= 0:
            return False

        try:
            from core.data_fetcher import get_account_balance

            balance = await asyncio.to_thread(get_account_balance)
            if balance <= 0:
                return False

            positions = (await run_executor_method(self.executor.get_open_positions)) or []
            current_notional = 0.0
            for position in positions:
                if isinstance(position, dict) and position.get("coin") == asset:
                    current_notional += abs(float(position.get("size", 0) or 0)) * price

            proposed_notional = abs(float(proposed_size)) * price
            max_notional = balance * (max_pct / 100.0)
            allowed = current_notional + proposed_notional <= max_notional + 1e-9
            if not allowed:
                logger.warning(
                    "DCA acceleration blocked %s: current=$%.2f proposed=$%.2f max=$%.2f",
                    asset,
                    current_notional,
                    proposed_notional,
                    max_notional,
                )
            return allowed
        except Exception as exc:
            logger.error("DCA risk budget check failed for %s: %s", asset, exc)
            return False

    async def monitor_adaptive_dca(
        self, asset: str, config: Dict, current_price: float
    ) -> Dict:
        """Reassess live DCA orders and accelerate only after AI + learner + risk approval."""
        if not config.get("enabled") or current_price <= 0:
            return {"action": "WAIT", "updated": 0, "errors": []}

        adaptive = config.setdefault("adaptive", {})
        now_ts = time.time()
        interval = max(2.0, float(adaptive.get("monitor_interval_sec", 10.0)))
        last_monitor = float(adaptive.get("last_monitor_ts", 0.0) or 0.0)
        if now_ts - last_monitor < interval:
            return {"action": "WAIT", "updated": 0, "errors": []}
        adaptive["last_monitor_ts"] = now_ts

        orders = [
            order
            for order in config.get("active_orders", [])
            if order.get("status") == "active" and order.get("order_id")
        ]
        if not orders:
            return {"action": "WAIT", "updated": 0, "errors": []}

        ttl = max(10.0, float(adaptive.get("order_ttl_seconds", 45.0)))
        stale_exists = False
        for order in orders:
            try:
                placed_ts = float(order.get("placed_at_ts", now_ts))
            except (TypeError, ValueError):
                placed_ts = now_ts
            if now_ts - placed_ts >= ttl:
                stale_exists = True
                break

        last_price = float(adaptive.get("last_monitor_price", 0.0) or 0.0)
        movement_pct = (
            abs(current_price - last_price) / last_price * 100.0
            if last_price > 0
            else 0.0
        )
        adaptive["last_monitor_price"] = current_price

        # Fast loop remains cheap. Only fetch indicators/LLM input when an order
        # is stale or the pair has moved materially since the previous observation.
        move_trigger_pct = max(
            0.10, float(adaptive.get("market_move_trigger_pct", 0.25))
        )
        if not stale_exists and movement_pct < move_trigger_pct:
            return {"action": "WAIT", "updated": 0, "errors": []}

        from core.data_fetcher import get_mtf_data

        try:
            market_data = await asyncio.to_thread(get_mtf_data, f"{asset}-USD")
        except Exception as exc:
            logger.warning("Adaptive DCA market data unavailable for %s: %s", asset, exc)
            return {"action": "WAIT", "updated": 0, "errors": [str(exc)]}

        one_hour = market_data.get("1h", {}) or {}
        price = float(one_hour.get("price", current_price) or current_price)
        atr = float(one_hour.get("atr", 0) or 0)
        rsi = float(one_hour.get("rsi", 50) or 50)
        momentum = max(-1.0, min(1.0, (rsi - 50.0) / 50.0))
        volatility = abs(atr / price) if price > 0 else 0.0
        snapshot = MarketSnapshot(
            price=price,
            volatility=volatility,
            momentum=momentum,
            regime="UNKNOWN",
            spread_pct=0.0,
            liquidity_score=1.0,
        )

        ai_advice = await self._ai_advice(asset, config, market_data, now_ts)
        decision_config = self._adaptive_config(config)
        side = str(config.get("direction", "LONG")).upper()

        results = {"action": "WAIT", "updated": 0, "cancelled": 0, "errors": []}
        for order in orders:
            order_age_ts = order.get("placed_at_ts")
            if order_age_ts is None:
                try:
                    order_age_ts = datetime.fromisoformat(
                        str(order.get("placed_at", "")).replace("Z", "+00:00")
                    ).timestamp()
                except (TypeError, ValueError):
                    order_age_ts = now_ts

            order_for_policy = dict(order)
            order_for_policy["placed_at_ts"] = order_age_ts
            decision = evaluate_dca_order(
                side=side,
                market=snapshot,
                order=order_for_policy,
                now_ts=now_ts,
                config=decision_config,
                ai_advice=ai_advice,
                risk_allowed=True,
            )

            if decision.action == DCAAction.WAIT:
                continue

            if decision.action == DCAAction.REPRICE:
                new_price = float(decision.target_price or order["price"])
                if new_price <= 0:
                    continue
                cancel = await self._cancel_order(asset, int(order["order_id"]))
                if not cancel.get("success"):
                    results["errors"].append(
                        f"Cancel {order['order_id']}: {cancel.get('error')}"
                    )
                    continue
                result = await self._submit_limit(
                    asset, side, float(order["size"]), new_price, "DCA_REPRICE"
                )
                if result.get("success"):
                    order["order_id"] = result.get("order_id")
                    order["price"] = new_price
                    order["placed_at"] = datetime.now(timezone.utc).isoformat()
                    order["placed_at_ts"] = now_ts
                    results["action"] = "REPRICE"
                    results["updated"] += 1
                    results["cancelled"] += 1
                else:
                    results["errors"].append(
                        f"Reprice failed: {result.get('error', 'unknown')}"
                    )
                continue

            if decision.action == DCAAction.ACCELERATE:
                accelerated_size = float(order["size"]) * float(decision.size_multiplier)
                if not await self._risk_budget_allows_acceleration(
                    asset, config, accelerated_size, price
                ):
                    results["errors"].append("Acceleration blocked by DCA exposure budget")
                    continue

                # Cancel every resting DCA order first to eliminate race-condition
                # double fills before submitting the accelerated leg.
                cancelled = 0
                for active in list(orders):
                    cancel = await self._cancel_order(asset, int(active["order_id"]))
                    if cancel.get("success"):
                        active["status"] = "cancelled"
                        cancelled += 1

                if cancelled < len(orders):
                    results["errors"].append(
                        "Acceleration aborted: not all resting DCA orders were cancelled"
                    )
                    continue

                result = await self._submit_aggressive(
                    asset, side, accelerated_size, "DCA_ACCELERATED"
                )
                if not result.get("success"):
                    results["errors"].append(
                        f"Acceleration failed: {result.get('error', 'unknown')}"
                    )
                    continue

                level = int(order.get("level", 1))
                config.setdefault("filled_levels", [])
                if level not in config["filled_levels"]:
                    config["filled_levels"].append(level)
                config["last_fill_price"] = float(result.get("avg_price", price) or price)
                config["last_acceleration_ts"] = now_ts
                config["active_orders"] = []

                # Rebuild only the unfilled portion of the ladder from the new
                # execution anchor. This prevents the remaining orders from
                # becoming stale while preserving the already accelerated leg.
                rebuilt = self.calculate_dca_levels(
                    config["last_fill_price"],
                    float(config.get("base_size", order["size"])),
                    config,
                )
                for rebuilt_level in rebuilt:
                    if rebuilt_level["level"] in config["filled_levels"]:
                        continue
                    rebuilt_result = await self._submit_limit(
                        asset,
                        side,
                        float(rebuilt_level["size"]),
                        float(rebuilt_level["price"]),
                        "DCA_REBUILD",
                    )
                    if rebuilt_result.get("success"):
                        rebuilt_level["order_id"] = rebuilt_result.get("order_id")
                        rebuilt_level["status"] = "active"
                        rebuilt_level["placed_at"] = datetime.now(timezone.utc).isoformat()
                        rebuilt_level["placed_at_ts"] = now_ts
                        config["active_orders"].append(rebuilt_level)
                    else:
                        results["errors"].append(
                            f"Rebuild L{rebuilt_level['level']} failed: "
                            f"{rebuilt_result.get('error', 'unknown')}"
                        )

                results["action"] = "ACCELERATE"
                results["updated"] += 1
                results["cancelled"] += cancelled
                logger.warning(
                    "DCA ACCELERATED %s L%s size=%.8f @ %.8f | %s",
                    asset,
                    level,
                    accelerated_size,
                    config["last_fill_price"],
                    decision.reason,
                )
                break

        config["last_monitor_ts"] = now_ts
        state.save_state()
        return results

    async def close_dca_position(
        self, asset: str, config: Dict, close_side: str
    ) -> Dict:
        results = {
            "base_closed": False,
            "dca_cancelled": 0,
            "dca_closed": 0,
            "total_pnl": 0.0,
            "errors": [],
        }
        for order in config.get("active_orders", []):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    cancel_result = await self._cancel_order(asset, int(order["order_id"]))
                    if cancel_result.get("success"):
                        results["dca_cancelled"] += 1
                    else:
                        results["errors"].append(
                            f"Cancel {order['order_id']}: {cancel_result.get('error')}"
                        )
                except Exception as exc:
                    results["errors"].append(f"Cancel error: {exc}")

        try:
            positions = (await run_executor_method(self.executor.get_open_positions)) or []
            asset_positions = [
                p for p in positions if isinstance(p, dict) and p.get("coin") == asset
            ]
            for pos in asset_positions:
                size = abs(float(pos.get("size", 0) or 0))
                if size <= 0:
                    continue
                from execution.hl_executor import execute_hl_order

                close_result = await asyncio.to_thread(
                    execute_hl_order,
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
                    entry = float(pos.get("entry_price", 0) or 0)
                    exit_price = float(close_result.get("avg_price", entry) or entry)
                    pnl = (
                        (exit_price - entry) * size
                        if close_side == "SELL"
                        else (entry - exit_price) * size
                    )
                    results["total_pnl"] += pnl
                else:
                    results["errors"].append(
                        f"Close failed: {close_result.get('error')}"
                    )
        except Exception as exc:
            results["errors"].append(f"Position close error: {exc}")

        config["enabled"] = False
        config["closed_at"] = datetime.now(timezone.utc).isoformat()
        async with state.STATE_LOCK:
            state.DCA_POSITIONS.pop(asset, None)
            state.save_state()
        return results

    async def close_dca_position_partial(
        self, asset: str, config: Dict, close_side: str, percent: float
    ) -> Dict:
        percent = max(0.0, min(100.0, float(percent)))
        results = {
            "base_closed_pct": 0.0,
            "dca_closed": 0,
            "dca_cancelled": 0,
            "total_pnl": 0.0,
            "errors": [],
        }
        for order in config.get("active_orders", []):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    cancel_result = await self._cancel_order(
                        asset, int(order["order_id"])
                    )
                    if cancel_result.get("success"):
                        results["dca_cancelled"] += 1
                except Exception as exc:
                    results["errors"].append(f"Cancel error: {exc}")

        try:
            positions = (await run_executor_method(self.executor.get_open_positions)) or []
            asset_positions = [
                p for p in positions if isinstance(p, dict) and p.get("coin") == asset
            ]
            for pos in asset_positions:
                total_size = abs(float(pos.get("size", 0) or 0))
                if total_size <= 0:
                    continue
                close_size = total_size * percent / 100.0
                if close_size <= 0:
                    continue
                from execution.hl_executor import execute_hl_order

                close_result = await asyncio.to_thread(
                    execute_hl_order,
                    coin=asset,
                    side=close_side,
                    size=close_size,
                    reduce_only=True,
                    strategy="AUTO_DCA",
                    regime="AUTO",
                    execution_label="DCA_EXIT",
                )
                if close_result.get("success"):
                    results["dca_closed"] += 1
                    entry = float(pos.get("entry_price", 0) or 0)
                    exit_price = float(close_result.get("avg_price", entry) or entry)
                    pnl = (
                        (exit_price - entry) * close_size
                        if close_side == "SELL"
                        else (entry - exit_price) * close_size
                    )
                    results["total_pnl"] += pnl
            results["base_closed_pct"] = percent
        except Exception as exc:
            results["errors"].append(f"Position close error: {exc}")

        if percent >= 100:
            config["enabled"] = False
            config["closed_at"] = datetime.now(timezone.utc).isoformat()
        return results

    async def update_trailing_orders(
        self, asset: str, config: Dict, current_price: float
    ) -> Dict:
        """Maintain trailing DCA and run the adaptive monitor on every fast tick."""
        if not config.get("enabled"):
            return {"updated": 0, "errors": []}

        adaptive_result = await self.monitor_adaptive_dca(
            asset, config, current_price
        )

        # Adaptive mode owns active orders. Legacy trailing mode is retained as a
        # fallback only when adaptive mode is explicitly disabled.
        if config.get("adaptive", {}).get("enabled", True):
            return {
                "updated": adaptive_result.get("updated", 0),
                "cancelled": adaptive_result.get("cancelled", 0),
                "action": adaptive_result.get("action", "WAIT"),
                "errors": adaptive_result.get("errors", []),
            }

        if not config.get("trailing"):
            return {"updated": 0, "errors": []}

        results = {"updated": 0, "cancelled": 0, "errors": []}
        last_fill_price = config.get("last_fill_price", config.get("avg_entry", 0))
        base_size = config.get("base_size", 0.00018)
        new_levels = self.calculate_trailing_levels(
            last_fill_price, current_price, base_size, config
        )
        side = "BUY" if config.get("direction", "LONG") == "LONG" else "SELL"

        for order in config.get("active_orders", []):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    cancel_result = await self._cancel_order(
                        asset, int(order["order_id"])
                    )
                    if cancel_result.get("success"):
                        results["cancelled"] += 1
                except Exception as exc:
                    results["errors"].append(f"Cancel error: {exc}")

        placed = []
        for level in new_levels:
            if abs(level["price"] - current_price) / current_price < 0.001:
                continue
            try:
                result = await self._submit_limit(
                    asset, side, level["size"], level["price"], "DCA_ADD"
                )
                if result.get("success"):
                    level["order_id"] = result.get("order_id")
                    level["status"] = "active"
                    level["updated_at"] = datetime.now(timezone.utc).isoformat()
                    level["placed_at_ts"] = time.time()
                    placed.append(level)
                    results["updated"] += 1
            except Exception as exc:
                results["errors"].append(f"Place error: {exc}")

        config["active_orders"] = placed
        config["last_trailing_update"] = datetime.now(timezone.utc).isoformat()
        return results

    def check_profit_target(
        self, asset: str, config: Dict, current_price: float
    ) -> Optional[Dict]:
        target_pct = float(config.get("profit_target_pct", 0) or 0)
        if target_pct <= 0 or not config.get("enabled"):
            return None
        avg_entry = float(config.get("avg_entry", 0) or 0)
        if avg_entry <= 0:
            return None
        direction = config.get("direction", "LONG")
        if direction == "LONG":
            pnl_pct = ((current_price - avg_entry) / avg_entry) * 100
        else:
            pnl_pct = ((avg_entry - current_price) / avg_entry) * 100
        if pnl_pct >= target_pct:
            logger.info(
                "DCA profit target hit for %s: %.2f%% >= %.2f%%",
                asset,
                pnl_pct,
                target_pct,
            )
            return {
                "action": "close_all",
                "pnl_pct": pnl_pct,
                "target_pct": target_pct,
            }
        return None

    def get_dca_status(self, asset: str) -> Optional[Dict]:
        if asset not in self.active_dca:
            return None
        config = self.active_dca[asset]
        return {
            "enabled": config["enabled"],
            "levels": config["levels"],
            "active_orders": len(
                [o for o in config["active_orders"] if o.get("status") == "active"]
            ),
            "filled_levels": len(config.get("filled_levels", [])),
            "total_invested": config.get("total_invested", 0.0),
            "avg_entry": config.get("avg_entry", 0.0),
        }
