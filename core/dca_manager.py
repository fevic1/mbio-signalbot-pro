"""Canonical institutional DCA manager.

The manager owns DCA sizing, order execution, adaptive decisions, and exits.
Runtime reconciliation lives in ``core.dca_runtime`` and is executed before
adaptive policy is allowed to alter exposure.
"""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import core.state as state
from config_loader import get_config
from core.adaptive_dca import AdaptiveDCAConfig, DCAAction, MarketSnapshot, evaluate_dca_order
from core.executor_utils import run_executor_method

logger = logging.getLogger(__name__)


class DCAManager:
    """Own DCA sizing, order lifecycle, adaptive policy, and exits."""

    def __init__(self, executor):
        self.executor = executor
        self.active_dca: Dict[str, Dict] = {}

    def _global_config(self) -> Dict:
        try:
            return get_config().get("dca", {}) or {}
        except Exception:
            return {}

    def enable_dca(self, asset: str, levels: int = 3, spacing_pct: float = 1.2, multiplier: float = 1.25,
                   direction: str = "LONG", base_size: float = 0.00025, trailing: bool = False,
                   trailing_offset_pct: float = 0.8, profit_target_pct: float = 0.0) -> Dict:
        adaptive = {
            "enabled": True, "aggressive_enabled": True, "order_ttl_seconds": 45.0,
            "monitor_interval_sec": 5.0, "ai_review_interval_sec": 45.0,
            "acceleration_confidence": 0.72, "min_learner_score": 0.60,
            "max_acceleration_multiplier": 1.25, "market_move_trigger_pct": 0.25,
            "min_reprice_distance_pct": 0.15, "max_order_age_seconds": 300.0,
        }
        adaptive.update(self._global_config().get("adaptive", {}) or {})
        config = {
            "enabled": True, "levels": max(1, int(levels)),
            "spacing_pct": max(0.01, float(spacing_pct)),
            "multiplier": max(1.0, float(multiplier)),
            "size_multiplier": max(1.0, float(multiplier)),
            "direction": direction.upper(), "base_size": float(base_size),
            "trailing": bool(trailing), "trailing_offset_pct": max(0.01, float(trailing_offset_pct)),
            "profit_target_pct": max(0.0, float(profit_target_pct)), "active_orders": [],
            "filled_levels": [], "total_invested": 0.0, "avg_entry": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat(), "adaptive": adaptive,
        }
        self.active_dca[asset] = config
        return config

    def calculate_dca_levels(self, entry_price: float, base_size: float, config: Dict) -> List[Dict]:
        levels = []
        multiplier = float(config.get("size_multiplier", config.get("multiplier", 1.25)))
        spacing = float(config.get("spacing_pct", config.get("level_spacing_pct", 1.2)))
        direction = str(config.get("direction", "LONG")).upper()
        current_size = float(base_size) * multiplier
        for level in range(1, max(1, int(config.get("levels", config.get("max_levels", 3)))) + 1):
            distance = spacing * level / 100.0
            price = entry_price * (1.0 - distance) if direction == "LONG" else entry_price * (1.0 + distance)
            levels.append({"level": level, "price": round(price, 8), "size": round(current_size, 8),
                           "status": "pending", "order_id": None})
            current_size *= multiplier
        return levels

    def calculate_trailing_levels(self, entry_price: float, current_price: float, base_size: float, config: Dict) -> List[Dict]:
        offset = float(config.get("trailing_offset_pct", config.get("spacing_pct", 1.2))) / 100.0
        spacing = float(config.get("spacing_pct", 1.2)) / 100.0
        multiplier = float(config.get("size_multiplier", config.get("multiplier", 1.25)))
        direction = str(config.get("direction", "LONG")).upper()
        price = current_price * (1.0 - offset) if direction == "LONG" else current_price * (1.0 + offset)
        size = float(base_size) * multiplier
        levels = []
        for level in range(1, max(1, int(config.get("levels", 3))) + 1):
            levels.append({"level": level, "price": round(price, 8), "size": round(size, 8),
                           "status": "pending", "order_id": None, "trailing": True})
            price = price * (1.0 - spacing) if direction == "LONG" else price * (1.0 + spacing)
            size *= multiplier
        return levels

    def should_pause_dca(self, asset: str, current_price: float) -> bool:
        if current_price <= 0:
            return True
        threshold = float(self._global_config().get("pause_on_large_drop_pct", 0.0) or 0.0)
        if threshold <= 0:
            return False
        position = state.OPEN_POSITIONS.get(asset, {})
        anchor = float(position.get("entry", 0) or position.get("entry_price", 0) or
                       state.DCA_POSITIONS.get(asset, {}).get("entry_price", 0) or 0)
        if anchor <= 0:
            return False
        direction = str(position.get("side", "BUY")).upper()
        adverse = ((anchor - current_price) / anchor * 100.0) if direction in {"BUY", "LONG"} else ((current_price - anchor) / anchor * 100.0)
        return adverse >= threshold

    async def _submit_limit(self, asset: str, side: str, size: float, price: float, label: str) -> dict:
        from execution.hl_executor import execute_hl_order
        return await asyncio.to_thread(execute_hl_order, coin=asset, side=side, size=size,
                                       limit_px=price, order_type="Limit", strategy="AUTO_DCA",
                                       regime="AUTO", execution_label=label)

    async def _submit_aggressive(self, asset: str, side: str, size: float, label: str) -> dict:
        from execution.hl_executor import execute_hl_order
        return await asyncio.to_thread(execute_hl_order, coin=asset, side=side, size=size,
                                       limit_px=None, order_type="Limit", strategy="AUTO_DCA",
                                       regime="AUTO", execution_label=label)

    async def _cancel_order(self, asset: str, order_id: int) -> dict:
        return await run_executor_method(self.executor.cancel_order, coin=asset, order_id=int(order_id))

    def _adaptive_config(self, config: Dict) -> AdaptiveDCAConfig:
        adaptive = dict(self._global_config().get("adaptive", {}) or {})
        adaptive.update(config.get("adaptive", {}) or {})
        return AdaptiveDCAConfig(
            enabled=bool(adaptive.get("enabled", True)),
            aggressive_enabled=bool(adaptive.get("aggressive_enabled", True)),
            order_ttl_seconds=max(10.0, float(adaptive.get("order_ttl_seconds", 45.0))),
            min_reprice_distance_pct=max(0.01, float(adaptive.get("min_reprice_distance_pct", 0.15))),
            acceleration_confidence=max(0.50, min(1.0, float(adaptive.get("acceleration_confidence", 0.72)))),
            min_learner_score=max(0.0, min(1.0, float(adaptive.get("min_learner_score", 0.60)))),
            max_acceleration_multiplier=max(1.0, min(1.25, float(adaptive.get("max_acceleration_multiplier", 1.25)))),
            max_order_age_seconds=max(30.0, float(adaptive.get("max_order_age_seconds", 300.0))),
        )

    async def place_dca_orders(self, asset: str, entry_price: float, base_size: float, config: Dict) -> List[Dict]:
        if self.should_pause_dca(asset, entry_price):
            logger.warning("DCA paused for %s by large-drop guardrail", asset)
            return []
        levels = self.calculate_dca_levels(entry_price, base_size, config)
        side = side_to_order_side(str(config.get("direction", "LONG")))
        placed = []
        now_ts = time.time()
        for level in levels:
            try:
                result = await self._submit_limit(asset, side, float(level["size"]), float(level["price"]), "DCA_ENTRY")
                if result.get("success"):
                    level.update({"order_id": result.get("order_id"), "status": "active",
                                  "placed_at": datetime.now(timezone.utc).isoformat(), "placed_at_ts": now_ts})
                    placed.append(level)
            except Exception as exc:
                logger.error("DCA order placement failed %s/L%s: %s", asset, level["level"], exc)
        config["active_orders"] = placed
        config["is_waiting_for_fill"] = bool(placed)
        config["last_monitor_ts"] = now_ts
        config["last_exchange_size"] = float(config.get("base_size", base_size) or base_size)
        self.active_dca[asset] = config
        if placed:
            async with state.STATE_LOCK:
                state.DCA_POSITIONS[asset] = {
                    "entry_price": float(config.get("avg_entry", entry_price) or entry_price),
                    "base_size": float(base_size), "direction": config.get("direction", "LONG"),
                    "levels": placed, "is_waiting_for_fill": True,
                    "last_fill_price": float(config.get("last_fill_price", entry_price) or entry_price),
                    "filled_levels": list(config.get("filled_levels", [])),
                    "opened_at": datetime.now(timezone.utc).isoformat(),
                }
                state.save_state()
        return placed

    async def _ai_advice(self, asset: str, config: Dict, market_data: dict, now_ts: float) -> dict:
        adaptive = config.setdefault("adaptive", {})
        review_interval = max(15.0, float(adaptive.get("ai_review_interval_sec", 45.0)))
        if now_ts - float(adaptive.get("last_ai_review_ts", 0.0) or 0.0) < review_interval:
            return config.get("last_ai_advice", {})
        adaptive["last_ai_review_ts"] = now_ts
        try:
            from core.signal_generator import analyze_batch
            from core.meta_learner import get_meta_learner
            from core.regime import detect_regime
            result, provider = await analyze_batch({asset: market_data}, get_config())
            item = result.get(asset, {}) if isinstance(result, dict) else {}
            signal = str(item.get("signal", "HOLD")).upper()
            raw_conf = float(item.get("confidence", 0) or 0)
            confidence = max(0.0, min(1.0, raw_conf / 100.0 if raw_conf > 1 else raw_conf))
            regime = detect_regime(market_data.get("4h", {}) or {})
            weights = get_meta_learner().get_weights(regime)
            learner_score = float(weights.get("LLM", 0.0) or 0.0)
            direction = str(config.get("direction", "LONG")).upper()
            aligned = (direction == "LONG" and signal in {"BUY", "STRONG BUY"}) or (direction == "SHORT" and signal in {"SELL", "STRONG SELL"})
            advice = {"action": "ACCELERATE" if aligned else "WAIT", "confidence": confidence,
                      "learner_score": max(0.0, min(1.0, learner_score)),
                      "max_price": float(market_data.get("1h", {}).get("price", 0) or 0),
                      "size_multiplier": min(1.25, float(adaptive.get("max_acceleration_multiplier", 1.25))),
                      "valid_for_seconds": review_interval,
                      "reason": f"{provider} {signal} ({confidence:.0%}); MetaLearner LLM weight={learner_score:.2f}"}
            config["last_ai_advice"] = advice
            return advice
        except Exception as exc:
            logger.warning("Adaptive DCA AI review failed for %s: %s", asset, exc)
            return config.get("last_ai_advice", {})

    async def _risk_budget_allows_acceleration(self, asset: str, config: Dict, proposed_size: float, price: float) -> bool:
        max_pct = float(self._global_config().get("max_total_dca_exposure_pct", 0.0) or 0.0)
        if max_pct <= 0:
            return False
        try:
            from core.data_fetcher import get_account_balance
            balance = await asyncio.to_thread(get_account_balance)
            if balance <= 0:
                return False
            positions = (await run_executor_method(self.executor.get_open_positions)) or []
            current_notional = sum(abs(float(p.get("size", 0) or 0)) * price for p in positions
                                   if isinstance(p, dict) and p.get("coin") == asset)
            return current_notional + abs(float(proposed_size)) * price <= balance * max_pct / 100.0 + 1e-9
        except Exception as exc:
            logger.error("DCA risk budget check failed for %s: %s", asset, exc)
            return False

    async def monitor_adaptive_dca(self, asset: str, config: Dict, current_price: float) -> Dict:
        if not config.get("enabled") or current_price <= 0:
            return {"action": "WAIT", "updated": 0, "cancelled": 0, "errors": []}
        adaptive = config.setdefault("adaptive", {})
        now_ts = time.time()
        config["last_monitor_ts"] = now_ts
        self.active_dca[asset] = config
        orders = [o for o in config.get("active_orders", []) if o.get("status") == "active" and o.get("order_id")]
        if not orders:
            state.save_state()
            return {"action": "WAIT", "updated": 0, "cancelled": 0, "errors": []}
        ttl = max(10.0, float(adaptive.get("order_ttl_seconds", 45.0)))
        stale_exists = any(
            now_ts - float(o.get("placed_at_ts") if o.get("placed_at_ts") is not None else now_ts) >= ttl
            for o in orders
        )
        last_price = float(adaptive.get("last_monitor_price", 0.0) or 0.0)
        movement_pct = abs(current_price - last_price) / last_price * 100.0 if last_price > 0 else 0.0
        adaptive["last_monitor_price"] = current_price
        trigger = max(0.10, float(adaptive.get("market_move_trigger_pct", 0.25)))
        if not stale_exists and movement_pct < trigger:
            return {"action": "WAIT", "updated": 0, "cancelled": 0, "errors": []}
        from core.data_fetcher import get_mtf_data
        try:
            market_data = await asyncio.to_thread(get_mtf_data, f"{asset}-USD")
        except Exception as exc:
            return {"action": "WAIT", "updated": 0, "cancelled": 0, "errors": [str(exc)]}
        one_hour = market_data.get("1h", {}) or {}
        price = float(one_hour.get("price", current_price) or current_price)
        atr = float(one_hour.get("atr", 0) or 0)
        rsi = float(one_hour.get("rsi", 50) or 50)
        snapshot = MarketSnapshot(price=price, volatility=abs(atr / price) if price > 0 else 0.0,
                                  momentum=max(-1.0, min(1.0, (rsi - 50.0) / 50.0)),
                                  regime="UNKNOWN", spread_pct=0.0, liquidity_score=1.0)
        advice = await self._ai_advice(asset, config, market_data, now_ts)
        policy = self._adaptive_config(config)
        side = str(config.get("direction", "LONG")).upper()
        results = {"action": "WAIT", "updated": 0, "cancelled": 0, "errors": []}
        for order in list(orders):
            placed_ts = order.get("placed_at_ts")
            if placed_ts is None:
                try:
                    placed_ts = datetime.fromisoformat(str(order.get("placed_at", "")).replace("Z", "+00:00")).timestamp()
                except (TypeError, ValueError):
                    placed_ts = now_ts
            decision = evaluate_dca_order(side=side, market=snapshot, order={**order, "placed_at_ts": placed_ts},
                                          now_ts=now_ts, config=policy, ai_advice=advice, risk_allowed=True)
            if decision.action == DCAAction.WAIT:
                continue
            if decision.action == DCAAction.REPRICE:
                target = float(decision.target_price or order["price"])
                cancel = await self._cancel_order(asset, int(order["order_id"]))
                if not cancel.get("success"):
                    results["errors"].append(f"Cancel {order['order_id']}: {cancel.get('error')}")
                    continue
                result = await self._submit_limit(asset, side_to_order_side(side), float(order["size"]), target, "DCA_REPRICE")
                if result.get("success"):
                    order.update({"order_id": result.get("order_id"), "price": target, "status": "active",
                                  "placed_at": datetime.now(timezone.utc).isoformat(), "placed_at_ts": now_ts})
                    results["action"] = "REPRICE"; results["updated"] += 1; results["cancelled"] += 1
                else:
                    results["errors"].append(f"Reprice failed: {result.get('error', 'unknown')}")
                continue
            if decision.action == DCAAction.ACCELERATE:
                accelerated_size = float(order["size"]) * float(decision.size_multiplier)
                if not await self._risk_budget_allows_acceleration(asset, config, accelerated_size, price):
                    results["errors"].append("Acceleration blocked by DCA exposure budget")
                    continue
                cancelled = 0
                for active in list(orders):
                    cancel = await self._cancel_order(asset, int(active["order_id"]))
                    if cancel.get("success"):
                        active["status"] = "cancelled"; cancelled += 1
                if cancelled < len(orders):
                    results["errors"].append("Acceleration aborted: not all resting DCA orders were cancelled")
                    continue
                result = await self._submit_aggressive(asset, side_to_order_side(side), accelerated_size, "DCA_ACCELERATED")
                if not result.get("success"):
                    results["errors"].append(f"Acceleration failed: {result.get('error', 'unknown')}")
                    continue
                level = int(order.get("level", 1)); filled = config.setdefault("filled_levels", [])
                if level not in filled: filled.append(level)
                fill_price = float(result.get("avg_price", price) or price)
                config["last_fill_price"] = fill_price; config["last_acceleration_ts"] = now_ts; config["active_orders"] = []
                for level_data in self._build_remaining_levels(config, fill_price):
                    try:
                        rebuilt_result = await self._submit_limit(asset, side_to_order_side(side), float(level_data["size"]), float(level_data["price"]), "DCA_REBUILD")
                        if rebuilt_result.get("success"):
                            level_data.update({"order_id": rebuilt_result.get("order_id"), "status": "active",
                                               "placed_at": datetime.now(timezone.utc).isoformat(), "placed_at_ts": now_ts})
                            config["active_orders"].append(level_data)
                        else:
                            results["errors"].append(f"Rebuild L{level_data['level']} failed: {rebuilt_result.get('error', 'unknown')}")
                    except Exception as exc:
                        results["errors"].append(f"Rebuild L{level_data['level']} failed: {exc}")
                results.update({"action": "ACCELERATE", "updated": results["updated"] + 1,
                                "cancelled": results["cancelled"] + cancelled})
                break
        self.active_dca[asset] = config
        state.save_state()
        return results

    def _build_remaining_levels(self, config: Dict, anchor: float) -> List[Dict]:
        filled = {int(x) for x in config.get("filled_levels", [])}
        return [x for x in self.calculate_dca_levels(anchor, float(config.get("base_size", 0) or 0), config)
                if int(x["level"]) not in filled]

    async def close_dca_position(self, asset: str, config: Dict, close_side: str) -> Dict:
        results = {"base_closed": False, "dca_cancelled": 0, "dca_closed": 0, "total_pnl": 0.0, "errors": []}
        for order in list(config.get("active_orders", [])):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    result = await self._cancel_order(asset, int(order["order_id"]))
                    if result.get("success"): results["dca_cancelled"] += 1
                    else: results["errors"].append(f"Cancel {order['order_id']}: {result.get('error')}")
                except Exception as exc: results["errors"].append(f"Cancel error: {exc}")
        try:
            positions = (await run_executor_method(self.executor.get_open_positions)) or []
            for pos in positions:
                if not isinstance(pos, dict) or pos.get("coin") != asset: continue
                size = abs(float(pos.get("size", 0) or 0))
                if size <= 0: continue
                from execution.hl_executor import execute_hl_order
                result = await asyncio.to_thread(execute_hl_order, coin=asset, side=close_side, size=size,
                                                 reduce_only=True, strategy="AUTO_DCA", regime="AUTO", execution_label="DCA_EXIT")
                if result.get("success"):
                    results["base_closed"] = True; results["dca_closed"] += 1
                    entry = float(pos.get("entry_price", 0) or 0); exit_price = float(result.get("avg_price", entry) or entry)
                    results["total_pnl"] += ((exit_price - entry) * size) if close_side == "SELL" else ((entry - exit_price) * size)
                else: results["errors"].append(f"Close failed: {result.get('error')}")
        except Exception as exc: results["errors"].append(f"Position close error: {exc}")
        config["enabled"] = False; config["active_orders"] = []; config["closed_at"] = datetime.now(timezone.utc).isoformat()
        self.active_dca.pop(asset, None)
        async with state.STATE_LOCK:
            state.DCA_POSITIONS.pop(asset, None); state.save_state()
        return results

    async def close_dca_position_partial(self, asset: str, config: Dict, close_side: str, percent: float) -> Dict:
        percent = max(0.0, min(100.0, float(percent)))
        results = {"base_closed_pct": 0.0, "dca_closed": 0, "dca_cancelled": 0, "total_pnl": 0.0, "errors": []}
        for order in list(config.get("active_orders", [])):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    if (await self._cancel_order(asset, int(order["order_id"]))).get("success"): results["dca_cancelled"] += 1
                except Exception as exc: results["errors"].append(f"Cancel error: {exc}")
        try:
            positions = (await run_executor_method(self.executor.get_open_positions)) or []
            for pos in positions:
                if not isinstance(pos, dict) or pos.get("coin") != asset: continue
                total_size = abs(float(pos.get("size", 0) or 0)); close_size = total_size * percent / 100.0
                if close_size <= 0: continue
                from execution.hl_executor import execute_hl_order
                result = await asyncio.to_thread(execute_hl_order, coin=asset, side=close_side, size=close_size,
                                                 reduce_only=True, strategy="AUTO_DCA", regime="AUTO", execution_label="DCA_EXIT")
                if result.get("success"):
                    results["dca_closed"] += 1
                    entry = float(pos.get("entry_price", 0) or 0); exit_price = float(result.get("avg_price", entry) or entry)
                    results["total_pnl"] += ((exit_price - entry) * close_size) if close_side == "SELL" else ((entry - exit_price) * close_size)
        except Exception as exc: results["errors"].append(f"Position close error: {exc}")
        results["base_closed_pct"] = percent
        if percent >= 100:
            config["enabled"] = False; config["active_orders"] = []; self.active_dca.pop(asset, None); state.DCA_POSITIONS.pop(asset, None)
        state.save_state(); return results

    async def update_trailing_orders(self, asset: str, config: Dict, current_price: float) -> Dict:
        if not config.get("enabled"): return {"updated": 0, "cancelled": 0, "errors": []}
        if (config.get("adaptive", {}) or {}).get("enabled", True): return await self.monitor_adaptive_dca(asset, config, current_price)
        if not config.get("trailing"): return {"updated": 0, "cancelled": 0, "errors": []}
        last_fill = float(config.get("last_fill_price", config.get("avg_entry", 0)) or 0); base_size = float(config.get("base_size", 0) or 0)
        side = side_to_order_side(str(config.get("direction", "LONG"))); results = {"updated": 0, "cancelled": 0, "errors": []}
        for order in list(config.get("active_orders", [])):
            if order.get("status") == "active" and order.get("order_id"):
                try:
                    if (await self._cancel_order(asset, int(order["order_id"]))).get("success"): results["cancelled"] += 1
                except Exception as exc: results["errors"].append(str(exc))
        placed = []
        for level in self.calculate_trailing_levels(last_fill, current_price, base_size, config):
            result = await self._submit_limit(asset, side, float(level["size"]), float(level["price"]), "DCA_ADD")
            if result.get("success"):
                level.update({"order_id": result.get("order_id"), "status": "active", "placed_at_ts": time.time()}); placed.append(level); results["updated"] += 1
        config["active_orders"] = placed; state.save_state(); return results

    def check_profit_target(self, asset: str, config: Dict, current_price: float) -> Optional[Dict]:
        target = float(config.get("profit_target_pct", 0) or 0); avg_entry = float(config.get("avg_entry", 0) or 0)
        if target <= 0 or avg_entry <= 0 or not config.get("enabled"): return None
        direction = str(config.get("direction", "LONG")).upper()
        pnl_pct = ((current_price - avg_entry) / avg_entry * 100.0) if direction == "LONG" else ((avg_entry - current_price) / avg_entry * 100.0)
        return {"action": "close_all", "pnl_pct": pnl_pct, "target_pct": target} if pnl_pct >= target else None

    def get_dca_status(self, asset: str) -> Optional[Dict]:
        config = self.active_dca.get(asset) or state.OPEN_POSITIONS.get(asset, {}).get("dca") or state.DCA_POSITIONS.get(asset)
        if not config: return None
        active = [o for o in config.get("active_orders", []) if o.get("status") == "active"]
        return {"enabled": bool(config.get("enabled")), "levels": int(config.get("levels", 0) or 0),
                "active_orders": len(active), "filled_levels": len(config.get("filled_levels", [])),
                "total_invested": config.get("total_invested", 0.0), "avg_entry": config.get("avg_entry", 0.0)}

    async def synchronize(self, asset: str, position: Dict) -> Dict:
        from core.dca_runtime import DCARuntimeCoordinator
        return await DCARuntimeCoordinator(self).ensure(asset, position)

    async def on_fill(self, asset: str, position: Dict) -> Dict:
        return await self.synchronize(asset, position)

    async def on_regime_change(self, asset: str, position: Dict) -> Dict:
        return await self.synchronize(asset, position)


def side_to_order_side(direction: str) -> str:
    return "BUY" if str(direction).upper() in {"LONG", "BUY"} else "SELL"
