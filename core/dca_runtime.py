"""Institutional DCA runtime coordinator.

This module closes the gap between persisted DCA intent and live exchange state.
It is deliberately separate from the policy layer:

* ``core.adaptive_dca`` decides what should happen.
* ``core.dca_manager`` owns order placement/cancellation and adaptive decisions.
* this coordinator reconciles fills, restarts, missing orders, and ladder state.

No LLM output is executed here. All placement still flows through DCAManager.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Dict, Iterable

import core.state as state
from core.dca_manager import DCAManager

logger = logging.getLogger(__name__)

_DEFAULT_ADAPTIVE = {
    "enabled": True,
    "aggressive_enabled": True,
    "order_ttl_seconds": 45.0,
    "monitor_interval_sec": 5.0,
    "ai_review_interval_sec": 45.0,
    "acceleration_confidence": 0.72,
    "min_learner_score": 0.60,
    "max_acceleration_multiplier": 1.25,
    "market_move_trigger_pct": 0.25,
    "min_reprice_distance_pct": 0.15,
    "max_order_age_seconds": 300.0,
}


class DCARuntimeCoordinator:
    """Reconcile persisted DCA state with the live exchange before adaptation."""

    def __init__(self, manager: DCAManager):
        self.manager = manager

    @staticmethod
    def normalize_config(position: Dict) -> Dict:
        dca = position.setdefault("dca", {})
        adaptive = dca.setdefault("adaptive", {})
        for key, value in _DEFAULT_ADAPTIVE.items():
            adaptive.setdefault(key, value)

        dca.setdefault("enabled", True)
        dca.setdefault("direction", "LONG" if position.get("side") == "BUY" else "SHORT")
        dca.setdefault("levels", dca.get("max_levels", 3))
        dca.setdefault("spacing_pct", dca.get("level_spacing_pct", 1.2))
        dca.setdefault("size_multiplier", dca.get("multiplier", 1.25))
        dca.setdefault("base_size", position.get("size", 0.0))
        dca.setdefault("active_orders", [])
        dca.setdefault("filled_levels", [])
        dca.setdefault("total_invested", 0.0)
        dca.setdefault("avg_entry", position.get("entry", 0.0))

        # Level 1 is the already-filled base position. Older persisted state may
        # have an empty filled_levels list even though the base order is live.
        if position.get("size", 0) and not dca.get("filled_levels"):
            dca["filled_levels"] = [1]

        return dca

    async def _live_position(self, asset: str) -> Dict:
        positions = await self._executor_call("get_open_positions")
        for position in positions or []:
            if isinstance(position, dict) and str(position.get("coin", "")).upper() == asset.upper():
                return position
        return {}

    async def _open_orders(self) -> Iterable[Dict]:
        return await self._executor_call("get_open_orders")

    async def _executor_call(self, method_name: str, **kwargs):
        method = getattr(self.manager.executor, method_name, None)
        if method is None:
            raise RuntimeError(f"DCA executor missing required method: {method_name}")
        from core.executor_utils import run_executor_method
        result = await run_executor_method(method, **kwargs)
        return result or []

    @staticmethod
    def _order_map(open_orders: Iterable[Dict]) -> Dict[int, Dict]:
        mapped: Dict[int, Dict] = {}
        for order in open_orders or []:
            if not isinstance(order, dict):
                continue
            oid = order.get("oid", order.get("order_id"))
            try:
                if oid is not None:
                    mapped[int(oid)] = order
            except (TypeError, ValueError):
                continue
        return mapped

    @staticmethod
    def _live_size(position: Dict) -> float:
        try:
            return abs(float(position.get("size", 0) or 0))
        except (TypeError, ValueError):
            return 0.0

    async def reconcile(self, asset: str, position: Dict) -> Dict:
        """Reconcile active order IDs and fill state against exchange snapshots."""
        dca = self.normalize_config(position)
        active = [
            order for order in dca.get("active_orders", [])
            if order.get("status") == "active" and order.get("order_id")
        ]
        if not active:
            live = await self._live_position(asset)
            self._update_position_projection(dca, live)
            return {"filled": [], "missing": [], "partial": [], "active": 0}

        try:
            open_orders = await self._open_orders()
        except Exception as exc:
            logger.error("DCA exchange reconciliation unavailable %s: %s", asset, exc)
            return {"filled": [], "missing": [], "partial": [], "active": len(active), "error": str(exc)}

        live = await self._live_position(asset)
        live_size = self._live_size(live)
        previous_size = float(dca.get("last_exchange_size", dca.get("base_size", 0.0)) or 0.0)
        order_map = self._order_map(open_orders)
        filled = []
        missing = []
        partial = []
        retained = []

        for order in active:
            try:
                oid = int(order["order_id"])
            except (TypeError, ValueError):
                missing.append(order)
                continue

            exchange_order = order_map.get(oid)
            if exchange_order is not None:
                try:
                    remaining = float(exchange_order.get("sz", order.get("size", 0)) or 0)
                    expected = float(order.get("size", 0) or 0)
                except (TypeError, ValueError):
                    remaining, expected = 0.0, 0.0
                if expected > 0 and 0 < remaining < expected:
                    order["size_remaining"] = remaining
                    order["filled_size"] = max(0.0, expected - remaining)
                    partial.append(order)
                retained.append(order)
                continue

            missing.append(order)

        # A missing order is considered filled only when the live position grew.
        # If the exchange position did not grow, the order was canceled/rejected
        # outside this process and is eligible for controlled replacement.
        growth = max(0.0, live_size - previous_size)
        if missing and growth > 0:
            expected_missing = sum(float(o.get("size", 0) or 0) for o in missing)
            if growth + max(1e-12, expected_missing * 0.02) >= expected_missing:
                for order in missing:
                    order["status"] = "filled"
                    order["filled_at"] = datetime.now(timezone.utc).isoformat()
                    filled.append(order)
            else:
                # Ambiguous partial/multi-order fill: do not guess which level
                # filled. Keep state conservative and let the next tick resolve it.
                retained.extend(missing)
                missing = []

        if filled:
            filled_levels = dca.setdefault("filled_levels", [])
            for order in filled:
                level = int(order.get("level", 0) or 0)
                if level > 0 and level not in filled_levels:
                    filled_levels.append(level)
            dca["last_fill_price"] = float(
                live.get("entry_price", dca.get("last_fill_price", position.get("entry", 0)))
                or dca.get("last_fill_price", position.get("entry", 0))
            )

        dca["active_orders"] = retained
        dca["last_exchange_size"] = live_size
        self._update_position_projection(dca, live)
        self._persist(asset, dca)

        return {
            "filled": filled,
            "missing": missing,
            "partial": partial,
            "active": len(retained),
        }

    @staticmethod
    def _update_position_projection(dca: Dict, live: Dict) -> None:
        if not live:
            return
        try:
            size = abs(float(live.get("size", 0) or 0))
            entry = float(live.get("entry_price", 0) or 0)
        except (TypeError, ValueError):
            return
        if size > 0 and entry > 0:
            dca["avg_entry"] = entry
            dca["total_invested"] = round(size * entry, 8)
            dca["last_exchange_size"] = size

    def _persist(self, asset: str, dca: Dict) -> None:
        state.DCA_POSITIONS[asset] = {
            "entry_price": float(dca.get("avg_entry", 0) or 0),
            "base_size": float(dca.get("base_size", 0) or 0),
            "direction": dca.get("direction", "LONG"),
            "levels": list(dca.get("active_orders", [])),
            "is_waiting_for_fill": bool(dca.get("active_orders")),
            "last_fill_price": float(dca.get("last_fill_price", dca.get("avg_entry", 0)) or 0),
            "filled_levels": list(dca.get("filled_levels", [])),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        state.save_state()

    async def rebuild_remaining(self, asset: str, position: Dict) -> Dict:
        """Build only unfilled DCA levels from the latest exchange entry anchor."""
        dca = self.normalize_config(position)
        levels = max(1, int(dca.get("levels", 3)))
        filled_levels = {int(x) for x in dca.get("filled_levels", [])}
        anchor = float(
            dca.get("last_fill_price", 0)
            or dca.get("avg_entry", 0)
            or position.get("entry", 0)
            or 0
        )
        base_size = float(dca.get("base_size", position.get("size", 0)) or 0)
        if anchor <= 0 or base_size <= 0:
            return {"placed": 0, "cancelled": 0, "errors": ["invalid DCA anchor or base size"]}
        if self.manager.should_pause_dca(asset, anchor):
            return {"placed": 0, "cancelled": 0, "errors": ["large-drop guardrail active"]}

        cancelled = 0
        errors = []
        for order in list(dca.get("active_orders", [])):
            if order.get("status") != "active" or not order.get("order_id"):
                continue
            try:
                result = await self.manager._cancel_order(asset, int(order["order_id"]))
                if result.get("success"):
                    cancelled += 1
                else:
                    errors.append(f"cancel {order['order_id']}: {result.get('error')}")
            except Exception as exc:
                errors.append(f"cancel {order.get('order_id')}: {exc}")

        dca["active_orders"] = []
        placed = 0
        side = "BUY" if str(dca.get("direction", "LONG")).upper() == "LONG" else "SELL"
        ladder = self.manager.calculate_dca_levels(anchor, base_size, dca)
        now_ts = time.time()

        for level in ladder:
            if int(level["level"]) in filled_levels:
                continue
            try:
                result = await self.manager._submit_limit(
                    asset, side, float(level["size"]), float(level["price"]), "DCA_REBUILD"
                )
                if not result.get("success"):
                    errors.append(f"L{level['level']}: {result.get('error', 'placement failed')}")
                    continue
                level.update(
                    {
                        "order_id": result.get("order_id"),
                        "status": "active",
                        "placed_at": datetime.now(timezone.utc).isoformat(),
                        "placed_at_ts": now_ts,
                    }
                )
                dca["active_orders"].append(level)
                placed += 1
            except Exception as exc:
                errors.append(f"L{level['level']}: {exc}")

        dca["last_monitor_ts"] = now_ts
        self._persist(asset, dca)
        return {"placed": placed, "cancelled": cancelled, "errors": errors}

    async def ensure(self, asset: str, position: Dict) -> Dict:
        """Startup-safe entry point used by the supervisor for every DCA position."""
        dca = self.normalize_config(position)
        if not dca.get("enabled"):
            return {"action": "DISABLED"}

        reconciliation = await self.reconcile(asset, position)
        if reconciliation.get("filled") or reconciliation.get("missing"):
            rebuild = await self.rebuild_remaining(asset, position)
            return {"action": "REBUILD", "reconciliation": reconciliation, "rebuild": rebuild}

        if not dca.get("active_orders") and len(dca.get("filled_levels", [])) < int(dca.get("levels", 3)):
            rebuild = await self.rebuild_remaining(asset, position)
            return {"action": "INITIALIZE", "rebuild": rebuild}

        return {"action": "SYNC", "reconciliation": reconciliation}
