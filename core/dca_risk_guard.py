"""
DCA Governor — Risk Guard

Guardrails and block conditions for the MBIO DCA lifecycle.

This component is permission-only:
    - ADD
    - ACCELERATE
    - REPRICE
    - PROTECT
    - CLOSE

It never submits, cancels, reprices, or closes orders.

The execution layer remains responsible for acting on a permitted verdict.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, List

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RiskVerdict:
    """Immutable permission result returned by the risk guard."""

    permitted: bool
    reason: str
    blockers: List[str]

    @classmethod
    def allow(cls, action: str) -> "RiskVerdict":
        return cls(
            permitted=True,
            reason=f"{action} permitted",
            blockers=[],
        )

    @classmethod
    def block(cls, action: str, blockers: List[str]) -> "RiskVerdict":
        return cls(
            permitted=False,
            reason=f"{action} blocked: {', '.join(blockers)}",
            blockers=list(blockers),
        )


class DCARiskGuard:
    """
    Single authority for DCA permission decisions.

    The guard does not execute trading operations. It evaluates state,
    configuration, and proposed actions and returns a RiskVerdict.

    Supported decisions:
        ADD
        ACCELERATE
        REPRICE
        PROTECT
        CLOSE
    """

    def __init__(self, config: Any) -> None:
        self.config = config

    @staticmethod
    def _section(config: Any, name: str) -> Any:
        """Safely retrieve a configuration section."""
        return getattr(config, name, None)

    @staticmethod
    def _enum_name(value: Any) -> str:
        """
        Return an enum's symbolic name without importing a specific DCA
        state module.

        This keeps the risk guard decoupled from the state-machine
        implementation while still supporting real Enum instances.
        """
        if value is None:
            return ""

        name = getattr(value, "name", None)
        if name:
            return str(name).upper()

        raw_value = getattr(value, "value", value)
        return str(raw_value).upper()

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def can_add(
        self,
        state: Any,
        plan: Any,
        current_price: float,
        available_budget: float,
    ) -> RiskVerdict:
        """
        Judge whether a normal DCA ADD is permitted.

        This checks:
            - state add permission
            - maximum filled levels
            - total DCA risk budget
            - maximum position exposure
            - configured pause guardrail
            - consecutive-loss/unfilled breaker
            - available execution budget
            - valid current market price
        """
        blockers: List[str] = []

        guardrails = self._section(self.config, "guardrails")

        max_levels = self._safe_int(
            getattr(guardrails, "max_levels", 0),
            default=0,
        )

        risk_budget_usd = getattr(
            guardrails,
            "risk_budget_usd",
            None,
        )

        max_position_size_usd = getattr(
            guardrails,
            "max_position_size_usd",
            None,
        )

        pause = bool(getattr(guardrails, "pause", False))

        consecutive_loss_breaker = self._safe_int(
            getattr(
                guardrails,
                "consecutive_loss_breaker",
                0,
            ),
            default=0,
        )

        can_add = getattr(state, "can_add", None)
        if callable(can_add):
            try:
                if not can_add():
                    adding_state = self._enum_name(
                        getattr(state, "adding_state", None)
                    )
                    blockers.append(
                        f"adding_state={adding_state or 'blocked'}"
                    )
            except Exception as exc:
                logger.warning(
                    "DCA risk guard could not evaluate state.can_add(): %s",
                    exc,
                )
                blockers.append("adding_state_check_failed")
        else:
            blockers.append("adding_state_check_unavailable")

        levels_filled = self._safe_int(
            getattr(state, "levels_filled", 0)
        )

        if max_levels > 0 and levels_filled >= max_levels:
            blockers.append("max_levels_filled")

        planned_exposure = self._safe_float(
            getattr(plan, "total_planned_size", 0.0)
        )

        if risk_budget_usd is not None:
            risk_budget = self._safe_float(risk_budget_usd)
            if planned_exposure > risk_budget:
                blockers.append(
                    "risk_budget_exceeded"
                )

        total_filled_size = getattr(
            plan,
            "total_filled_size",
            None,
        )

        if callable(total_filled_size):
            try:
                filled_exposure = self._safe_float(
                    total_filled_size()
                )
            except Exception:
                filled_exposure = 0.0
                blockers.append("filled_exposure_calculation_failed")
        else:
            filled_exposure = self._safe_float(
                getattr(plan, "total_filled_size", 0.0)
            )

        if max_position_size_usd is not None:
            max_position = self._safe_float(max_position_size_usd)

            if filled_exposure > max_position:
                blockers.append(
                    "max_position_size_exceeded"
                )

            if (
                planned_exposure > max_position
                and filled_exposure <= max_position
            ):
                blockers.append(
                    "planned_position_size_exceeded"
                )

        if pause:
            blockers.append("guardrail_pause_active")

        consecutive_unfilled = self._safe_int(
            getattr(state, "consecutive_unfilled_levels", 0)
        )

        if (
            consecutive_loss_breaker > 0
            and consecutive_unfilled >= consecutive_loss_breaker
        ):
            blockers.append("consecutive_loss_breaker")

        price = self._safe_float(current_price)

        if price <= 0:
            blockers.append("invalid_current_price")

        budget = self._safe_float(available_budget)

        if planned_exposure > budget:
            blockers.append("available_budget_exceeded")

        return (
            RiskVerdict.allow("ADD")
            if not blockers
            else RiskVerdict.block("ADD", blockers)
        )

    def can_accelerate(
        self,
        state: Any,
        ai_confidence: float,
        learner_score: float,
    ) -> RiskVerdict:
        """
        Judge whether adaptive DCA acceleration is permitted.

        Acceleration is strictly more constrained than normal ADD.
        """
        blockers: List[str] = []

        acceleration = self._section(
            self.config,
            "acceleration",
        )

        if not bool(
            getattr(
                acceleration,
                "enabled",
                False,
            )
        ):
            blockers.append("acceleration_disabled")

        can_add = getattr(state, "can_add", None)

        if callable(can_add):
            try:
                if not can_add():
                    adding_state = self._enum_name(
                        getattr(state, "adding_state", None)
                    )
                    blockers.append(
                        f"adding_state={adding_state or 'blocked'}"
                    )
            except Exception as exc:
                logger.warning(
                    "DCA acceleration state check failed: %s",
                    exc,
                )
                blockers.append("adding_state_check_failed")
        else:
            blockers.append("adding_state_check_unavailable")

        confidence = self._safe_float(ai_confidence)
        learner = self._safe_float(learner_score)

        confidence_threshold = self._safe_float(
            getattr(
                acceleration,
                "confidence_threshold",
                1.0,
            ),
            default=1.0,
        )

        learner_threshold = self._safe_float(
            getattr(
                acceleration,
                "learner_score_threshold",
                1.0,
            ),
            default=1.0,
        )

        if confidence < confidence_threshold:
            blockers.append(
                f"ai_confidence={confidence:.2f} < threshold"
            )

        if learner < learner_threshold:
            blockers.append(
                f"learner_score={learner:.2f} < threshold"
            )

        return (
            RiskVerdict.allow("ACCELERATE")
            if not blockers
            else RiskVerdict.block("ACCELERATE", blockers)
        )

    def can_reprice(
        self,
        order_age_seconds: float,
        market_move_pct: float,
        min_reprice_distance: float,
    ) -> RiskVerdict:
        """
        Judge whether an existing DCA order may be repriced.

        Repricing requires:
            - TTL expiry, OR max-age expiry, with market movement required
              for ordinary TTL expiry.
            - minimum reprice distance from the current order.

        This method never decides the replacement price.
        """
        blockers: List[str] = []

        adaptive = self._section(
            self.config,
            "adaptive",
        )

        age = self._safe_float(order_age_seconds)
        move = abs(self._safe_float(market_move_pct))
        min_distance = abs(
            self._safe_float(min_reprice_distance)
        )

        ttl = self._safe_float(
            getattr(
                adaptive,
                "order_ttl_seconds",
                0,
            )
        )

        max_age = self._safe_float(
            getattr(
                adaptive,
                "max_order_age_seconds",
                0,
            )
        )

        market_trigger = abs(
            self._safe_float(
                getattr(
                    adaptive,
                    "market_move_trigger_pct",
                    0,
                )
            )
        )

        ttl_expired = ttl <= 0 or age >= ttl
        max_age_expired = max_age > 0 and age >= max_age

        if not ttl_expired and not max_age_expired:
            blockers.append("order_ttl_not_expired")

        if (
            ttl_expired
            and not max_age_expired
            and move < market_trigger
        ):
            blockers.append(
                f"market_move={self._safe_float(market_move_pct):.3f}% "
                f"< trigger"
            )

        if move < min_distance:
            blockers.append(
                f"move={self._safe_float(market_move_pct):.3f}% "
                f"< min_reprice={min_distance:.3f}%"
            )

        return (
            RiskVerdict.allow("REPRICE")
            if not blockers
            else RiskVerdict.block("REPRICE", blockers)
        )

    def can_protect_profit(
        self,
        state: Any,
        current_price: float,
    ) -> RiskVerdict:
        """
        Judge whether DCA profit-protection logic is permitted.

        Protection is mode/phase aware:

            RECOVERY:
                Wait for the configured recovery target.

            HYBRID / ACCUMULATION:
                Do not harvest while still accumulating.

            HARVEST:
                Protection requires an established harvest state.

        The execution layer determines the actual protection order.
        """
        blockers: List[str] = []

        mode = self._enum_name(
            getattr(state, "mode", None)
        )

        phase = self._enum_name(
            getattr(state, "phase", None)
        )

        profit_target_reached = bool(
            getattr(
                state,
                "profit_target_reached",
                False,
            )
        )

        harvest_count = self._safe_int(
            getattr(
                state,
                "harvest_count",
                0,
            )
        )

        price = self._safe_float(current_price)

        if price <= 0:
            blockers.append("invalid_current_price")

        if (
            mode == "RECOVERY"
            and not profit_target_reached
        ):
            blockers.append(
                "recovery_mode: waiting for profit_target"
            )

        if (
            mode == "HYBRID"
            and phase == "ACCUMULATION"
        ):
            blockers.append(
                "hybrid: still accumulating"
            )

        if (
            mode == "HARVEST"
            and harvest_count == 0
        ):
            blockers.append(
                "harvest: no harvests yet"
            )

        return (
            RiskVerdict.allow("PROTECT")
            if not blockers
            else RiskVerdict.block("PROTECT", blockers)
        )

    def can_close(self, state: Any) -> RiskVerdict:
        """
        Judge whether a DCA position may enter its CLOSE path.

        CLOSE is intentionally not blocked merely because the position
        is in an accumulation phase. Emergency/risk exits must remain
        available. The guard only blocks an already terminal/invalid
        state when the state explicitly reports that it cannot close.

        If the state exposes can_close(), that state-level permission is
        respected.
        """
        blockers: List[str] = []

        state_can_close = getattr(
            state,
            "can_close",
            None,
        )

        if callable(state_can_close):
            try:
                if not state_can_close():
                    blockers.append("state_close_permission_denied")
            except Exception as exc:
                logger.warning(
                    "DCA close permission check failed: %s",
                    exc,
                )
                blockers.append("state_close_check_failed")

        lifecycle_state = self._enum_name(
            getattr(state, "lifecycle_state", None)
        )

        if lifecycle_state in {
            "CLOSED",
            "CLOSING",
            "TERMINATED",
        }:
            blockers.append(
                f"position_already_terminal={lifecycle_state}"
            )

        return (
            RiskVerdict.allow("CLOSE")
            if not blockers
            else RiskVerdict.block("CLOSE", blockers)
        )
