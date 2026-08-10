"""
MBIO DCA Governor — Supervisor

Decision layer for the DCA lifecycle.

Responsibilities:
    - evaluate the current DCA state
    - decide ADD / REPRICE / HARVEST / PROTECT / CLOSE / HOLD
    - enforce cooldowns and duplicate-action protection
    - remain side-aware for LONG and SHORT positions
    - delegate permission decisions to the risk guard

This module NEVER submits, cancels, or closes exchange orders.

Execution remains owned by the canonical MBIO DCA execution engine.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class SupervisorDecision:
    """
    One supervisor decision.

    The execution bridge is responsible for validating and executing this
    decision against live exchange state.
    """

    action: str  # ADD | REPRICE | HARVEST | PROTECT | CLOSE | HOLD
    level: Optional[int] = None
    price: Optional[float] = None
    size: Optional[float] = None
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class DCASupervisor:
    """
    DCA lifecycle decision engine.

    This class intentionally uses duck-typed state/config/plan objects so the
    governor does not introduce a second DCA state/configuration architecture.

    Expected plan interface:
        next_unfilled_level()
        unfilled_levels()
        current_avg_entry()
        total_filled_size()

    Expected state interface:
        can_add()
        can_harvest()
        mode
        phase
        profit_target_reached
        harvest_count
        unrealized_pnl_pct
        adding_state

    Expected risk guard interface:
        can_add(...)
        can_reprice(...)
        can_protect_profit(...)
        can_close(...)
    """

    ACTIONS = {
        "ADD",
        "REPRICE",
        "HARVEST",
        "PROTECT",
        "CLOSE",
        "HOLD",
    }

    def __init__(self, config: Any, risk_guard: Any) -> None:
        self.config = config
        self.risk_guard = risk_guard

        # Runtime-only fallback timestamps.
        #
        # Persisted order placement timestamps should preferably come from
        # the DCA level itself. These maps exist only for orders created during
        # the current process lifetime.
        self._order_timestamps: Dict[str, float] = {}

        # Prevent repeated identical decisions from firing every supervisor
        # tick before the execution bridge has acknowledged the action.
        self._last_decision: Dict[str, tuple[str, float]] = {}

        # Prevent repeated profit harvesting on the same price movement.
        self._last_harvest_price: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # PUBLIC EVALUATION
    # ------------------------------------------------------------------

    def evaluate(
        self,
        state: Any,
        plan: Any,
        current_price: float,
        available_budget: float,
    ) -> SupervisorDecision:
        """
        Evaluate one DCA position.

        Priority:

            CLOSE
              ↓
            PROTECT
              ↓
            HARVEST
              ↓
            ADD
              ↓
            REPRICE
              ↓
            HOLD

        Only one decision is returned per evaluation.
        """

        current_price = float(current_price)
        available_budget = float(available_budget)

        if current_price <= 0:
            return self._hold(
                "Invalid current price; supervisor refuses to act."
            )

        # --------------------------------------------------------------
        # 1. TERMINAL CLOSE
        # --------------------------------------------------------------

        if self._phase_is(state, "CLOSE"):
            verdict = self.risk_guard.can_close(state)

            if verdict.permitted:
                return self._decision(
                    SupervisorDecision(
                        action="CLOSE",
                        reason="DCA phase=CLOSE and risk guard permitted closure.",
                    ),
                    key=self._state_key(state, plan),
                )

            return self._hold(
                f"CLOSE blocked: {verdict.reason}"
            )

        # --------------------------------------------------------------
        # 2. PROFIT TARGET / PROTECTION
        # --------------------------------------------------------------

        if self._profit_target_reached(state):
            verdict = self.risk_guard.can_protect_profit(
                state,
                current_price,
            )

            if verdict.permitted:
                return self._decision(
                    SupervisorDecision(
                        action="PROTECT",
                        price=current_price,
                        reason="DCA profit target reached; protection permitted.",
                    ),
                    key=self._state_key(state, plan),
                )

        # --------------------------------------------------------------
        # 3. PROFIT HARVEST
        # --------------------------------------------------------------

        if self._can_harvest(state):
            ratchet_enabled = self._config_bool(
                "protection.profit_ratchet_enabled",
                False,
            )

            if ratchet_enabled:
                harvest = self._evaluate_harvest(
                    state=state,
                    plan=plan,
                    current_price=current_price,
                )

                if harvest is not None:
                    return self._decision(
                        harvest,
                        key=self._state_key(state, plan),
                    )

        # --------------------------------------------------------------
        # 4. NORMAL DCA ADD
        # --------------------------------------------------------------

        next_level = self._next_unfilled_level(plan)

        if next_level is not None:
            verdict = self.risk_guard.can_add(
                state,
                plan,
                current_price,
                available_budget,
            )

            if not verdict.permitted:
                return self._decision(
                    SupervisorDecision(
                        action="BLOCK",
                        level=self._level_index(next_level),
                        price=self._level_price(next_level),
                        size=self._level_size(next_level),
                        reason=f"ADD blocked: {verdict.reason}",
                        metadata={
                            "available_budget": available_budget,
                            "current_price": current_price,
                            "side": self._plan_side(plan, state),
                            "blockers": list(verdict.blockers),
                        },
                    ),
                    key=self._state_key(state, plan),
                )

            level_price = self._level_price(next_level)
            level_size = self._level_size(next_level)

            if level_price is None or level_size is None:
                return self._hold(
                    "Next DCA level is malformed; refusing ADD."
                )

            if level_size <= 0:
                return self._hold(
                    f"DCA level {self._level_index(next_level)} has "
                    f"non-positive size."
                )

            if self._price_at_level(
                side=self._plan_side(plan, state),
                current=current_price,
                level_price=level_price,
            ):
                return self._decision(
                    SupervisorDecision(
                        action="ADD",
                        level=self._level_index(next_level),
                        price=level_price,
                        size=level_size,
                        reason=(
                            f"DCA level {self._level_index(next_level)} "
                            f"triggered at {level_price}."
                        ),
                        metadata={
                            "available_budget": available_budget,
                            "current_price": current_price,
                            "side": self._plan_side(plan, state),
                        },
                    ),
                    key=self._state_key(state, plan),
                )

            return self._hold(
                f"Waiting for DCA level {self._level_index(next_level)} "
                f"at {level_price}."
            )

        # --------------------------------------------------------------
        # 5. STALE ORDER REPRICING
        # --------------------------------------------------------------

        reprice = self._evaluate_reprice(
            state=state,
            plan=plan,
            current_price=current_price,
        )

        if reprice is not None:
            return self._decision(
                reprice,
                key=self._state_key(state, plan),
            )

        # --------------------------------------------------------------
        # 6. NOTHING TO DO
        # --------------------------------------------------------------

        return self._hold(
            "No DCA action required at current market state."
        )

    # ------------------------------------------------------------------
    # PROFIT HARVEST
    # ------------------------------------------------------------------

    def _evaluate_harvest(
        self,
        state: Any,
        plan: Any,
        current_price: float,
    ) -> Optional[SupervisorDecision]:
        """
        Calculate a partial profit harvest.

        The calculation is side-aware and uses the canonical average entry
        represented by the plan.

        A harvest is never allowed to exceed 25% of currently filled size.
        """

        if not self._can_harvest(state):
            return None

        pnl_pct = float(
            getattr(state, "unrealized_pnl_pct", 0.0) or 0.0
        )

        harvest_count = int(
            getattr(state, "harvest_count", 0) or 0
        )

        # After the first harvest require a meaningful move before another
        # harvest. This prevents repeated $1 churn on essentially flat prices.
        if harvest_count > 0 and pnl_pct < 2.0:
            return None

        avg_entry = self._average_entry(plan)

        if avg_entry <= 0:
            return None

        side = self._plan_side(plan, state)

        if side == "SHORT":
            price_diff = avg_entry - current_price
        else:
            price_diff = current_price - avg_entry

        if price_diff <= 0:
            return None

        target_profit = self._config_float(
            "protection.profit_ratchet_dollars",
            1.0,
        )

        if target_profit <= 0:
            return None

        harvest_size = target_profit / price_diff

        total_filled = self._total_filled_size(plan)

        if total_filled <= 0:
            return None

        # Hard supervisor cap. The risk layer may impose a stricter limit.
        max_harvest = total_filled * 0.25
        harvest_size = min(harvest_size, max_harvest)

        if harvest_size <= 0:
            return None

        # Do not repeatedly harvest at effectively the same price.
        last_price = self._last_harvest_price.get(
            self._state_key(state, plan)
        )

        min_move_pct = self._config_float(
            "protection.harvest_rearm_move_pct",
            0.25,
        )

        if last_price and last_price > 0:
            move_pct = (
                abs(current_price - last_price)
                / last_price
                * 100.0
            )

            if move_pct < min_move_pct:
                return None

        return SupervisorDecision(
            action="HARVEST",
            price=current_price,
            size=harvest_size,
            reason=(
                f"Harvest ${target_profit:.2f} from {side} DCA position; "
                f"avg_entry={avg_entry:.6f}, "
                f"current={current_price:.6f}."
            ),
            metadata={
                "target_profit_usd": target_profit,
                "avg_entry": avg_entry,
                "pnl_pct": pnl_pct,
                "side": side,
            },
        )

    # ------------------------------------------------------------------
    # REPRICING
    # ------------------------------------------------------------------

    def _evaluate_reprice(
        self,
        state: Any,
        plan: Any,
        current_price: float,
    ) -> Optional[SupervisorDecision]:
        """
        Find one stale DCA order that should be repriced.

        Placement time is taken from persisted level.placed_at first.
        Runtime timestamps are only the fallback.
        """

        levels = self._unfilled_levels(plan)

        if not levels:
            return None

        side = self._plan_side(plan, state)

        min_distance_pct = self._config_float(
            "adaptive.min_reprice_distance_pct",
            0.15,
        )

        for level in levels:
            order_id = getattr(level, "order_id", None)

            if order_id is None:
                continue

            placed_ts = self._placement_timestamp(level)

            if placed_ts is None:
                continue

            age_seconds = max(
                0.0,
                time.time() - placed_ts,
            )

            level_price = self._level_price(level)

            if level_price is None or level_price <= 0:
                continue

            market_move_pct = (
                abs(current_price - level_price)
                / level_price
                * 100.0
            )

            verdict = self.risk_guard.can_reprice(
                order_age_seconds=age_seconds,
                market_move_pct=market_move_pct,
                min_reprice_distance=min_distance_pct,
            )

            if not verdict.permitted:
                continue

            target_price = self._reprice_target(
                side=side,
                current_price=current_price,
                min_distance_pct=min_distance_pct,
            )

            return SupervisorDecision(
                action="REPRICE",
                level=self._level_index(level),
                price=target_price,
                size=self._level_size(level),
                reason=(
                    f"Reprice DCA level {self._level_index(level)}: "
                    f"age={age_seconds:.0f}s, "
                    f"market_move={market_move_pct:.2f}%."
                ),
                metadata={
                    "order_id": str(order_id),
                    "age_seconds": age_seconds,
                    "market_move_pct": market_move_pct,
                    "min_reprice_distance_pct": min_distance_pct,
                    "side": side,
                },
            )

        return None

    @staticmethod
    def _reprice_target(
        side: str,
        current_price: float,
        min_distance_pct: float,
    ) -> float:
        """
        Place the replacement limit order on the correct side of market.

        LONG:
            buy below current price.

        SHORT:
            sell above current price.
        """

        distance = min_distance_pct / 100.0

        if side == "SHORT":
            return current_price * (1.0 + distance)

        return current_price * (1.0 - distance)

    # ------------------------------------------------------------------
    # ORDER TIMESTAMP MANAGEMENT
    # ------------------------------------------------------------------

    def record_order_placed(
        self,
        order_id: str,
        placed_at: Optional[float] = None,
    ) -> None:
        """
        Record a runtime fallback placement timestamp.

        Persisted timestamps on DCA levels remain authoritative.
        """

        if not order_id:
            return

        timestamp = (
            float(placed_at)
            if placed_at is not None
            else time.time()
        )

        self._order_timestamps[str(order_id)] = timestamp

    def record_harvest_executed(
        self,
        state: Any,
        plan: Any,
        execution_price: float,
    ) -> None:
        """
        Mark the last harvest price so the same movement cannot repeatedly
        trigger the ratchet.
        """

        self._last_harvest_price[
            self._state_key(state, plan)
        ] = float(execution_price)

    # ------------------------------------------------------------------
    # DECISION DEDUPLICATION
    # ------------------------------------------------------------------

    def _decision(
        self,
        decision: SupervisorDecision,
        key: str,
    ) -> SupervisorDecision:
        """
        Suppress exact duplicate action decisions during a short cooldown.

        This protects the execution bridge from receiving the same command
        repeatedly while an order is being acknowledged by the exchange.
        """

        now = time.time()

        cooldown = self._config_float(
            "supervisor.action_cooldown_seconds",
            5.0,
        )

        signature = (
            decision.action,
            decision.level,
            decision.price,
            decision.size,
        )

        previous = self._last_decision.get(key)

        if previous is not None:
            previous_signature, previous_ts = previous

            if (
                previous_signature == repr(signature)
                and now - previous_ts < cooldown
            ):
                return SupervisorDecision(
                    action="HOLD",
                    reason=(
                        f"Duplicate {decision.action} suppressed during "
                        f"{cooldown:.1f}s action cooldown."
                    ),
                    metadata={
                        "suppressed_action": decision.action,
                        "cooldown_seconds": cooldown,
                    },
                )

        self._last_decision[key] = (
            repr(signature),
            now,
        )

        return decision

    # ------------------------------------------------------------------
    # GENERIC HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _hold(reason: str) -> SupervisorDecision:
        return SupervisorDecision(
            action="HOLD",
            reason=reason,
        )

    @staticmethod
    def _state_key(
        state: Any,
        plan: Any,
    ) -> str:
        asset = getattr(
            plan,
            "asset",
            getattr(state, "asset", "UNKNOWN"),
        )

        return str(asset).upper()

    @staticmethod
    def _phase_is(
        state: Any,
        phase_name: str,
    ) -> bool:
        phase = getattr(state, "phase", None)

        if phase is None:
            return False

        value = getattr(
            phase,
            "value",
            phase,
        )

        return str(value).upper() == phase_name

    @staticmethod
    def _profit_target_reached(state: Any) -> bool:
        return bool(
            getattr(
                state,
                "profit_target_reached",
                False,
            )
        )

    @staticmethod
    def _can_harvest(state: Any) -> bool:
        method = getattr(
            state,
            "can_harvest",
            None,
        )

        if callable(method):
            return bool(method())

        return False

    @staticmethod
    def _next_unfilled_level(plan: Any) -> Any:
        method = getattr(
            plan,
            "next_unfilled_level",
            None,
        )

        if not callable(method):
            return None

        return method()

    @staticmethod
    def _unfilled_levels(plan: Any) -> list[Any]:
        method = getattr(
            plan,
            "unfilled_levels",
            None,
        )

        if not callable(method):
            return []

        return list(method() or [])

    @staticmethod
    def _level_index(level: Any) -> int:
        value = getattr(
            level,
            "level_index",
            getattr(level, "level", 0),
        )

        return int(value)

    @staticmethod
    def _level_price(level: Any) -> Optional[float]:
        value = getattr(
            level,
            "price",
            None,
        )

        if value is None:
            return None

        return float(value)

    @staticmethod
    def _level_size(level: Any) -> Optional[float]:
        value = getattr(
            level,
            "size",
            None,
        )

        if value is None:
            return None

        return float(value)

    @staticmethod
    def _average_entry(plan: Any) -> float:
        method = getattr(
            plan,
            "current_avg_entry",
            None,
        )

        if not callable(method):
            return 0.0

        value = method()

        return float(value or 0.0)

    @staticmethod
    def _total_filled_size(plan: Any) -> float:
        method = getattr(
            plan,
            "total_filled_size",
            None,
        )

        if callable(method):
            return float(method() or 0.0)

        filled_levels = getattr(
            plan,
            "filled_levels",
            None,
        )

        if callable(filled_levels):
            return sum(
                float(
                    getattr(level, "size", 0.0) or 0.0
                )
                for level in filled_levels()
            )

        return 0.0

    @staticmethod
    def _plan_side(
        plan: Any,
        state: Any,
    ) -> str:
        raw = getattr(
            plan,
            "side",
            getattr(state, "side", "LONG"),
        )

        value = getattr(
            raw,
            "value",
            raw,
        )

        value = str(value).upper()

        if value in {"BUY", "LONG"}:
            return "LONG"

        if value in {"SELL", "SHORT"}:
            return "SHORT"

        return "LONG"

    def _placement_timestamp(
        self,
        level: Any,
    ) -> Optional[float]:
        """
        Prefer persisted level.placed_at over runtime memory.
        """

        placed_at = getattr(
            level,
            "placed_at",
            None,
        )

        if placed_at is not None:
            try:
                return float(placed_at)
            except (TypeError, ValueError):
                pass

        order_id = getattr(
            level,
            "order_id",
            None,
        )

        if order_id is None:
            return None

        return self._order_timestamps.get(
            str(order_id)
        )

    def _price_at_level(
        self,
        side: str,
        current: float,
        level_price: float,
    ) -> bool:
        """
        Determine whether market price has reached a DCA limit level.
        """

        if side == "SHORT":
            return current >= level_price

        return current <= level_price

    # ------------------------------------------------------------------
    # CONFIG ACCESS
    # ------------------------------------------------------------------

    def _config_value(
        self,
        path: str,
        default: Any = None,
    ) -> Any:
        """
        Read nested configuration without requiring a specific configuration
        implementation.

        Supports both:
            config.section.attribute

        and:
            config["section"]["attribute"]
        """

        current = self.config

        for part in path.split("."):
            if current is None:
                return default

            if isinstance(current, dict):
                if part not in current:
                    return default

                current = current[part]
                continue

            if not hasattr(current, part):
                return default

            current = getattr(
                current,
                part,
            )

        return current

    def _config_bool(
        self,
        path: str,
        default: bool,
    ) -> bool:
        return bool(
            self._config_value(
                path,
                default,
            )
        )

    def _config_float(
        self,
        path: str,
        default: float,
    ) -> float:
        value = self._config_value(
            path,
            default,
        )

        try:
            return float(value)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid DCA supervisor config %s=%r; using %s",
                path,
                value,
                default,
            )
            return float(default)
