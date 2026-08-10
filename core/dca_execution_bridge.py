"""
MBIO DCA Governor — Execution Adapter

The Governor owns decisions.
DCAManager remains the sole DCA exchange execution authority.

This adapter intentionally contains no exchange calls.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from core.dca_manager import DCAManager

logger = logging.getLogger(__name__)


class DCAExecutionBridge:
    """
    Translate GovernorCommand into the existing MBIO DCA execution layer.

    IMPORTANT:
        This class never calls the exchange executor directly.

    Execution authority:
        DCAGovernor
            -> DCAExecutionBridge
            -> DCAManager
            -> existing executor
    """

    def __init__(self, exchange_executor: Any) -> None:
        if exchange_executor is None:
            raise ValueError("DCAExecutionBridge requires an exchange executor")

        self.executor = exchange_executor
        self.manager = DCAManager(exchange_executor)

    async def execute(self, command: Any) -> Dict[str, Any]:
        if command is None:
            return {
                "status": "blocked",
                "action": "BLOCK",
                "reason": "Missing GovernorCommand",
            }

        action = str(getattr(command, "action", "BLOCK")).upper()
        plan = getattr(command, "plan", None)
        state = getattr(command, "state", None)
        decision = getattr(command, "decision", None)

        if plan is None:
            return {
                "status": "blocked",
                "action": "BLOCK",
                "reason": "GovernorCommand has no plan",
            }

        asset = str(getattr(plan, "asset", "") or "").upper()
        side = str(getattr(plan, "side", "") or "").upper()

        if not asset or side not in {"LONG", "SHORT"}:
            return {
                "status": "blocked",
                "action": "BLOCK",
                "reason": f"Invalid DCA command identity: asset={asset!r}, side={side!r}",
            }

        reason = str(getattr(decision, "reason", "") or "")

        logger.info(
            "[DCA ADAPTER] action=%s asset=%s side=%s reason=%s",
            action,
            asset,
            side,
            reason,
        )

        if action in {"HOLD", "BLOCK"}:
            return {
                "status": "held" if action == "HOLD" else "blocked",
                "action": action,
                "reason": reason,
            }

        config = self._config_from_command(command)

        if action in {"ADD", "ACCELERATE"}:
            return await self._execute_add(
                asset=asset,
                side=side,
                plan=plan,
                state=state,
                config=config,
                accelerated=action == "ACCELERATE",
            )

        if action == "REPRICE":
            return await self._execute_reprice(
                asset=asset,
                side=side,
                plan=plan,
                state=state,
                config=config,
            )

        if action == "HARVEST":
            return await self._execute_harvest(
                asset=asset,
                side=side,
                plan=plan,
                state=state,
                config=config,
            )

        if action == "PROTECT":
            return await self._execute_protect(
                asset=asset,
                side=side,
                plan=plan,
                state=state,
                config=config,
            )

        if action == "CLOSE":
            return await self._execute_close(
                asset=asset,
                side=side,
                config=config,
            )

        return {
            "status": "error",
            "action": action,
            "reason": f"Unsupported Governor action: {action}",
        }

    async def _execute_add(
        self,
        asset: str,
        side: str,
        plan: Any,
        state: Any,
        config: Dict[str, Any],
        accelerated: bool,
    ) -> Dict[str, Any]:
        """
        Delegate ADD through the existing DCAManager.

        No exchange operation occurs here.
        """

        level = getattr(getattr(state, "decision", None), "level", None)

        decision = getattr(plan, "next_unfilled_level", lambda: None)()
        if decision is None:
            return {
                "status": "held",
                "action": "ADD",
                "reason": "No unfilled DCA level available",
            }

        entry_price = float(
            getattr(plan, "entry_price", 0)
            or getattr(state, "avg_entry_price", 0)
            or 0
        )

        base_size = float(
            getattr(decision, "size", 0)
            or config.get("base_size", 0)
            or 0
        )

        if entry_price <= 0 or base_size <= 0:
            return {
                "status": "blocked",
                "action": "ADD",
                "reason": "Invalid canonical DCA entry price or size",
            }

        config["direction"] = side
        config["base_size"] = base_size

        # DCAManager owns placement. The manager's canonical ladder path
        # performs exchange execution and persistence.
        result = await self.manager.place_dca_orders(
            asset=asset,
            entry_price=entry_price,
            base_size=base_size,
            config=config,
        )

        return {
            **(result if isinstance(result, dict) else {"result": result}),
            "action": "ACCELERATE" if accelerated else "ADD",
            "adapter": "DCAManager",
        }

    async def _execute_reprice(
        self,
        asset: str,
        side: str,
        plan: Any,
        state: Any,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        current_price = float(
            getattr(state, "current_price", 0)
            or config.get("current_price", 0)
            or 0
        )

        if current_price <= 0:
            return {
                "status": "blocked",
                "action": "REPRICE",
                "reason": "Current price unavailable for DCA repricing",
            }

        config["direction"] = side

        result = await self.manager.monitor_adaptive_dca(
            asset,
            config,
            current_price,
        )

        return {
            **(result if isinstance(result, dict) else {"result": result}),
            "action": "REPRICE",
            "adapter": "DCAManager",
        }

    async def _execute_harvest(
        self,
        asset: str,
        side: str,
        plan: Any,
        state: Any,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        percent = float(
            getattr(
                getattr(state, "decision", None),
                "harvest_percent",
                25.0,
            )
            or 25.0
        )

        percent = max(0.01, min(percent, 100.0))
        config["direction"] = side

        result = await self.manager.close_dca_position_partial(
            asset=asset,
            config=config,
            close_side=("SELL" if side == "LONG" else "BUY"),
            percent=percent,
        )

        return {
            **(result if isinstance(result, dict) else {"result": result}),
            "action": "HARVEST",
            "adapter": "DCAManager",
            "percent": percent,
        }

    async def _execute_protect(
        self,
        asset: str,
        side: str,
        plan: Any,
        state: Any,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        current_price = float(
            getattr(state, "current_price", 0)
            or config.get("current_price", 0)
            or 0
        )

        if current_price <= 0:
            return {
                "status": "blocked",
                "action": "PROTECT",
                "reason": "Current price unavailable for DCA protection",
            }

        config["direction"] = side

        result = await self.manager.update_trailing_orders(
            asset,
            config,
            current_price,
        )

        return {
            **(result if isinstance(result, dict) else {"result": result}),
            "action": "PROTECT",
            "adapter": "DCAManager",
        }

    async def _execute_close(
        self,
        asset: str,
        side: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        config["direction"] = side

        result = await self.manager.close_dca_position(
            asset=asset,
            config=config,
            close_side=("SELL" if side == "LONG" else "BUY"),
        )

        return {
            **(result if isinstance(result, dict) else {"result": result}),
            "action": "CLOSE",
            "adapter": "DCAManager",
        }

    @staticmethod
    def _config_from_command(command: Any) -> Dict[str, Any]:
        """
        Construct the manager-compatible state projection.

        Persisted/live DCA state remains owned by the existing MBIO state
        system. This projection only translates Governor state.
        """

        plan = command.plan
        state = command.state
        metadata = dict(getattr(command, "metadata", {}) or {})

        levels = []
        for level in list(getattr(plan, "levels", []) or []):
            levels.append(
                {
                    "level": int(getattr(level, "level_index", 0)),
                    "price": float(getattr(level, "price", 0) or 0),
                    "size": float(getattr(level, "size", 0) or 0),
                    "order_id": getattr(level, "order_id", None),
                    "status": (
                        "filled"
                        if bool(getattr(level, "filled", False))
                        else "active"
                    ),
                }
            )

        return {
            "enabled": True,
            "direction": str(getattr(plan, "side", "LONG")).upper(),
            "base_size": float(
                getattr(plan, "total_planned_size", 0)
                or 0
            ),
            "active_orders": [
                x for x in levels if x["status"] == "active"
            ],
            "filled_levels": [
                x["level"] for x in levels if x["status"] == "filled"
            ],
            "profit_target_pct": float(
                metadata.get("profit_target_pct", 0) or 0
            ),
            "adaptive": {
                "enabled": True,
            },
            "current_price": float(
                metadata.get("current_price", 0) or 0
            ),
            "governor_mode": str(
                getattr(getattr(state, "mode", None), "value", "")
                or ""
            ),
            "governor_phase": str(
                getattr(getattr(state, "phase", None), "value", "")
                or ""
            ),
        }
