"""
MBIO DCA Governor — Canonical Lifecycle Controller

The governor owns DCA decision policy.

It:
    - maintains one plan/state pair per DCA position
    - processes verified fill events
    - evaluates lifecycle transitions
    - delegates immediate action selection to the supervisor
    - applies the final risk decision
    - never submits, cancels, or closes exchange orders

Execution remains owned by:
    core.dca_execution_engine

This module intentionally does not duplicate exchange execution logic.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from core.dca_config import DCAConfig
from core.dca_planner import DCAPlan
from core.dca_state_machine import (
    AddingState,
    DCAMode,
    DCAPhase,
    DCAState,
    DCATransitionRules,
)
from core.dca_risk_guard import DCARiskGuard
from core.dca_planner import DCAPlanner
from monitoring.dca_supervisor import DCASupervisor, SupervisorDecision

logger = logging.getLogger(__name__)


@dataclass
class GovernorCommand:
    """
    Decision emitted by the DCA governor.

    The execution bridge is the only component allowed to turn this command
    into an exchange operation.
    """

    action: str
    plan: DCAPlan
    state: DCAState
    decision: SupervisorDecision
    metadata: Dict[str, Any] = field(default_factory=dict)


class DCAGovernor:
    """
    Canonical DCA lifecycle controller.

    Policy flow:

        fill/update
             ↓
        state update
             ↓
        transition evaluation
             ↓
        supervisor decision
             ↓
        final risk gate
             ↓
        GovernorCommand
             ↓
        execution bridge
             ↓
        canonical execution engine

    No exchange API is called here.
    """

    ACTIONS = {
        "ADD",
        "ACCELERATE",
        "REPRICE",
        "HARVEST",
        "PROTECT",
        "CLOSE",
        "HOLD",
        "BLOCK",
    }

    def __init__(self, config: DCAConfig) -> None:
        self.config = config

        self.planner = DCAPlanner(config)
        self.risk_guard = DCARiskGuard(config)
        self.supervisor = DCASupervisor(
            config,
            self.risk_guard,
        )
        self.transition_rules = DCATransitionRules(config)

        # One plan/state pair per asset + side.
        self._plans: Dict[str, DCAPlan] = {}
        self._states: Dict[str, DCAState] = {}

    # ------------------------------------------------------------------
    # ENTRY
    # ------------------------------------------------------------------

    def start_dca(
        self,
        asset: str,
        side: str,
        entry_price: float,
        mode: Optional[str] = None,
        current_price: Optional[float] = None,
    ) -> GovernorCommand:
        """
        Initialize a DCA position.

        The planner remains the sole authority for ladder construction.
        """

        normalized_side = self._normalize_side(side)

        if entry_price <= 0:
            raise ValueError(
                f"Invalid DCA entry price: {entry_price}"
            )

        key = self._key(
            asset,
            normalized_side,
        )

        if key in self._plans:
            raise ValueError(
                f"DCA position already exists: {key}"
            )

        plan = self.planner.plan_entry(
            asset=asset,
            side=normalized_side,
            entry_price=float(entry_price),
            current_price=current_price,
        )

        selected_mode = (
            mode
            if mode is not None
            else getattr(
                self.config,
                "default_mode",
                "RECOVERY",
            )
        )

        state = DCAState(
            mode=DCAMode(selected_mode),
            phase=DCAPhase.ACCUMULATION,
            adding_state=AddingState.ALLOWED,
        )

        # Initialize the state from the canonical plan.
        state.avg_entry_price = float(
            plan.current_avg_entry()
        )

        state.total_filled_size = float(
            plan.total_filled_size()
        )

        state.levels_filled = len(
            plan.filled_levels()
        )

        self._plans[key] = plan
        self._states[key] = state

        logger.info(
            "[GOVERNOR] DCA started asset=%s side=%s mode=%s "
            "levels=%s entry=%s",
            asset,
            normalized_side,
            state.mode.value,
            len(plan.levels),
            entry_price,
        )

        return self._command(
            action="HOLD",
            plan=plan,
            state=state,
            decision=SupervisorDecision(
                action="HOLD",
                reason="DCA initialized",
            ),
            metadata={
                "event": "DCA_STARTED",
                "asset": asset,
                "side": normalized_side,
                "entry_price": float(entry_price),
            },
        )

    # ------------------------------------------------------------------
    # MAIN TICK
    # ------------------------------------------------------------------

    def tick(
        self,
        asset: str,
        side: str,
        current_price: float,
        available_budget: float,
        ai_confidence: Optional[float] = None,
        learner_score: Optional[float] = None,
        fill_event: Optional[Dict[str, Any]] = None,
    ) -> GovernorCommand:
        """
        Evaluate one DCA lifecycle tick.

        Fill events are applied before market-state evaluation.

        AI and learner values are advisory inputs only. They can never bypass
        the risk guard.
        """

        normalized_side = self._normalize_side(side)
        key = self._key(
            asset,
            normalized_side,
        )

        plan = self._plans.get(key)
        state = self._states.get(key)

        if plan is None or state is None:
            return self._blocked_command(
                asset=asset,
                side=normalized_side,
                reason=f"No active DCA plan/state for {key}",
            )

        try:
            current_price = float(current_price)
            available_budget = float(available_budget)
        except (TypeError, ValueError):
            return self._blocked_command(
                asset=asset,
                side=normalized_side,
                reason="Invalid market price or available budget",
                plan=plan,
                state=state,
            )

        if current_price <= 0:
            return self._blocked_command(
                asset=asset,
                side=normalized_side,
                reason="Current market price must be positive",
                plan=plan,
                state=state,
            )

        # --------------------------------------------------------------
        # 1. APPLY VERIFIED FILL
        # --------------------------------------------------------------

        if fill_event:
            plan, state = self._process_fill(
                plan=plan,
                state=state,
                fill_event=fill_event,
            )

        # --------------------------------------------------------------
        # 2. UPDATE POSITION METRICS
        # --------------------------------------------------------------

        state.unrealized_pnl_pct = self._calc_pnl_pct(
            plan=plan,
            current_price=current_price,
            side=normalized_side,
        )

        # --------------------------------------------------------------
        # 3. PROFIT TARGET
        # --------------------------------------------------------------

        self._update_profit_target(
            state=state,
            plan=plan,
            current_price=current_price,
            side=normalized_side,
        )

        # --------------------------------------------------------------
        # 4. STATE MACHINE
        # --------------------------------------------------------------

        transition_result = self.transition_rules.evaluate(state, current_price)
        state, transition_directive = transition_result

        # --------------------------------------------------------------
        # 5. SUPERVISOR
        # --------------------------------------------------------------

        decision = self.supervisor.evaluate(
            state=state,
            plan=plan,
            current_price=current_price,
            available_budget=available_budget,
        )

        # --------------------------------------------------------------
        # 6. FINAL GOVERNOR/RISK GATE
        # --------------------------------------------------------------

        command = self._risk_gate(
            decision=decision,
            state=state,
            plan=plan,
            ai_confidence=ai_confidence,
            learner_score=learner_score,
        )

        self._plans[key] = command.plan
        self._states[key] = command.state

        logger.debug(
            "[GOVERNOR] tick asset=%s side=%s action=%s "
            "mode=%s phase=%s pnl=%.4f%%",
            asset,
            normalized_side,
            command.action,
            state.mode.value,
            state.phase.value,
            state.unrealized_pnl_pct,
        )

        return command

    # ------------------------------------------------------------------
    # CLOSE
    # ------------------------------------------------------------------

    def request_close(
        self,
        asset: str,
        side: str,
    ) -> GovernorCommand:
        """
        Request terminal DCA closure.

        The governor only authorizes the close. Execution remains external.
        """

        normalized_side = self._normalize_side(side)
        key = self._key(
            asset,
            normalized_side,
        )

        plan = self._plans.get(key)
        state = self._states.get(key)

        if plan is None or state is None:
            return self._blocked_command(
                asset=asset,
                side=normalized_side,
                reason=f"No active DCA position to close: {key}",
            )

        state.phase = DCAPhase.CLOSE

        verdict = self.risk_guard.can_close(
            state
        )

        if not verdict.permitted:
            return self._command(
                action="BLOCK",
                plan=plan,
                state=state,
                decision=SupervisorDecision(
                    action="BLOCK",
                    reason=f"Close blocked: {verdict.reason}",
                ),
                metadata={
                    "event": "DCA_CLOSE_BLOCKED",
                    "blockers": list(
                        verdict.blockers
                    ),
                },
            )

        return self._command(
            action="CLOSE",
            plan=plan,
            state=state,
            decision=SupervisorDecision(
                action="CLOSE",
                reason="Close requested and risk guard permitted closure",
            ),
            metadata={
                "event": "DCA_CLOSE_REQUESTED",
            },
        )

    # ------------------------------------------------------------------
    # FILL PROCESSING
    # ------------------------------------------------------------------

    def _process_fill(
        self,
        plan: DCAPlan,
        state: DCAState,
        fill_event: Dict[str, Any],
    ) -> Tuple[DCAPlan, DCAState]:
        """
        Apply one verified exchange fill to canonical DCA state.

        The event must identify the DCA ladder level. Unknown/malformed fill
        events are rejected instead of mutating state.
        """

        if not isinstance(fill_event, dict):
            raise TypeError(
                "fill_event must be a dictionary"
            )

        level_index = fill_event.get(
            "level_index"
        )

        fill_price = fill_event.get(
            "fill_price"
        )

        fill_size = fill_event.get(
            "fill_size"
        )

        if level_index is None:
            raise ValueError(
                "DCA fill event missing level_index"
            )

        if fill_price is None:
            raise ValueError(
                "DCA fill event missing fill_price"
            )

        if fill_size is None:
            raise ValueError(
                "DCA fill event missing fill_size"
            )

        fill_price = float(fill_price)
        fill_size = float(fill_size)

        if fill_price <= 0:
            raise ValueError(
                f"Invalid DCA fill price: {fill_price}"
            )

        if fill_size <= 0:
            raise ValueError(
                f"Invalid DCA fill size: {fill_size}"
            )

        updated_plan = self.planner.replan_after_fill(
            plan=plan,
            filled_level_index=int(level_index),
            fill_price=fill_price,
            fill_size=fill_size,
        )

        state.levels_filled = len(
            updated_plan.filled_levels()
        )

        state.total_filled_size = float(
            updated_plan.total_filled_size()
        )

        state.avg_entry_price = float(
            updated_plan.current_avg_entry()
        )

        state.last_fill_at = fill_event.get(
            "timestamp"
        )

        # A verified fill resets the consecutive-unfilled breaker.
        state.consecutive_unfilled_levels = 0

        logger.info(
            "[GOVERNOR] fill asset=%s level=%s "
            "price=%.8f size=%.8f filled=%s avg=%.8f",
            updated_plan.asset,
            level_index,
            fill_price,
            fill_size,
            state.levels_filled,
            state.avg_entry_price,
        )

        return updated_plan, state

    # ------------------------------------------------------------------
    # PROFIT TARGET
    # ------------------------------------------------------------------

    @staticmethod
    def _update_profit_target(
        state: DCAState,
        plan: DCAPlan,
        current_price: float,
        side: str,
    ) -> None:
        target = getattr(
            plan,
            "profit_target_price",
            None,
        )

        if target is None:
            return

        target = float(target)

        if target <= 0:
            return

        if side == "SHORT":
            reached = current_price <= target
        else:
            reached = current_price >= target

        if reached:
            state.profit_target_reached = True

    # ------------------------------------------------------------------
    # RISK GATE
    # ------------------------------------------------------------------

    def _risk_gate(
        self,
        decision: SupervisorDecision,
        state: DCAState,
        plan: DCAPlan,
        ai_confidence: Optional[float],
        learner_score: Optional[float],
    ) -> GovernorCommand:
        """
        Apply final risk authority.

        IMPORTANT:
        A normal ADD is NOT automatically converted into ACCELERATE merely
        because acceleration is enabled.

        ACCELERATE requires explicit AI/learner evidence and must independently
        pass the risk guard.
        """

        action = str(
            decision.action
        ).upper()

        if action not in self.ACTIONS:
            logger.error(
                "[GOVERNOR] Unknown supervisor action=%s",
                action,
            )

            return self._command(
                action="BLOCK",
                plan=plan,
                state=state,
                decision=SupervisorDecision(
                    action="BLOCK",
                    reason=f"Unknown supervisor action: {action}",
                ),
                metadata={
                    "event": "INVALID_SUPERVISOR_ACTION",
                },
            )

        # --------------------------------------------------------------
        # ACCELERATION
        # --------------------------------------------------------------

        if action == "ADD":
            acceleration_enabled = bool(
                getattr(
                    getattr(
                        self.config,
                        "acceleration",
                        None,
                    ),
                    "enabled",
                    False,
                )
            )

            # Acceleration is optional. A normal ADD remains ADD unless
            # explicit AI/learner gates pass.
            if acceleration_enabled:
                confidence = self._bounded_score(
                    ai_confidence
                )

                learner = self._bounded_score(
                    learner_score
                )

                acceleration = self.risk_guard.can_accelerate(
                    state=state,
                    ai_confidence=confidence,
                    learner_score=learner,
                )

                if acceleration.permitted:
                    action = "ACCELERATE"

                    decision = SupervisorDecision(
                        action="ACCELERATE",
                        level=decision.level,
                        price=decision.price,
                        size=decision.size,
                        reason=(
                            f"{decision.reason}; "
                            "AI/learner acceleration risk gate passed"
                        ),
                        metadata={
                            **getattr(
                                decision,
                                "metadata",
                                {},
                            ),
                            "ai_confidence": confidence,
                            "learner_score": learner,
                        },
                    )

        # --------------------------------------------------------------
        # CLOSE
        # --------------------------------------------------------------

        if action == "CLOSE":
            verdict = self.risk_guard.can_close(
                state
            )

            if not verdict.permitted:
                return self._command(
                    action="BLOCK",
                    plan=plan,
                    state=state,
                    decision=SupervisorDecision(
                        action="BLOCK",
                        reason=(
                            f"CLOSE blocked: "
                            f"{verdict.reason}"
                        ),
                        metadata={
                            "blockers": list(
                                verdict.blockers
                            ),
                        },
                    ),
                    metadata={
                        "event": "RISK_BLOCK",
                        "requested_action": "CLOSE",
                    },
                )

        # --------------------------------------------------------------
        # ADD / ACCELERATE
        # --------------------------------------------------------------

        if action in {"ADD", "ACCELERATE"}:
            verdict = self.risk_guard.can_add(
                state=state,
                plan=plan,
                current_price=float(
                    decision.price
                    if decision.price is not None
                    else 0.0
                ),
                available_budget=0.0,
            )

            if not verdict.permitted:
                return self._command(
                    action="BLOCK",
                    plan=plan,
                    state=state,
                    decision=SupervisorDecision(
                        action="BLOCK",
                        level=decision.level,
                        price=decision.price,
                        size=decision.size,
                        reason=(
                            f"{action} blocked: "
                            f"{verdict.reason}"
                        ),
                        metadata={
                            "blockers": list(
                                verdict.blockers
                            ),
                        },
                    ),
                    metadata={
                        "event": "RISK_BLOCK",
                        "requested_action": action,
                    },
                )

        return self._command(
            action=action,
            plan=plan,
            state=state,
            decision=decision,
            metadata={
                "mode": self._enum_value(
                    state.mode
                ),
                "phase": self._enum_value(
                    state.phase
                ),
                "adding_state": self._enum_value(
                    state.adding_state
                ),
            },
        )

    # ------------------------------------------------------------------
    # COMMAND CONSTRUCTION
    # ------------------------------------------------------------------

    @staticmethod
    def _command(
        action: str,
        plan: DCAPlan,
        state: DCAState,
        decision: SupervisorDecision,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GovernorCommand:
        return GovernorCommand(
            action=action,
            plan=plan,
            state=state,
            decision=decision,
            metadata=metadata or {},
        )

    def _blocked_command(
        self,
        asset: str,
        side: str,
        reason: str,
        plan: Optional[DCAPlan] = None,
        state: Optional[DCAState] = None,
    ) -> GovernorCommand:
        """
        Produce a BLOCK command without attempting exchange execution.

        When no plan/state exists, this requires the DCAPlan/DCAState classes
        to support their normal empty constructors. If they do not, the caller
        receives the original exception rather than silently fabricating state.
        """

        if plan is None:
            plan = DCAPlan(
                asset=asset,
                side=side,
                entry_price=0,
                levels=[],
                total_planned_size=0,
                total_planned_value=0,
                avg_entry_target=0,
                profit_target_price=None,
                config_hash="blocked",
            )

        if state is None:
            state = DCAState()

        return self._command(
            action="BLOCK",
            plan=plan,
            state=state,
            decision=SupervisorDecision(
                action="BLOCK",
                reason=reason,
            ),
            metadata={
                "event": "DCA_BLOCKED",
                "asset": asset,
                "side": side,
            },
        )

    # ------------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_pnl_pct(
        plan: DCAPlan,
        current_price: float,
        side: str,
    ) -> float:
        """
        Calculate directional unrealized PnL percentage.

        LONG:
            (current - avg) / avg

        SHORT:
            (avg - current) / avg
        """

        avg = float(
            plan.current_avg_entry()
        )

        if avg <= 0:
            return 0.0

        if side == "SHORT":
            return (
                (avg - current_price)
                / avg
                * 100.0
            )

        return (
            (current_price - avg)
            / avg
            * 100.0
        )

    # ------------------------------------------------------------------
    # STATE ACCESS
    # ------------------------------------------------------------------

    def get_state(
        self,
        asset: str,
        side: str,
    ) -> Optional[DCAState]:
        return self._states.get(
            self._key(
                asset,
                self._normalize_side(side),
            )
        )

    def get_plan(
        self,
        asset: str,
        side: str,
    ) -> Optional[DCAPlan]:
        return self._plans.get(
            self._key(
                asset,
                self._normalize_side(side),
            )
        )

    def list_active(self) -> List[str]:
        return list(
            self._plans.keys()
        )

    def remove(
        self,
        asset: str,
        side: str,
    ) -> bool:
        """
        Remove an in-memory governor position after the execution bridge has
        confirmed terminal closure and persistence has been cleared.
        """

        key = self._key(
            asset,
            self._normalize_side(side),
        )

        existed = (
            key in self._plans
            or key in self._states
        )

        self._plans.pop(
            key,
            None,
        )

        self._states.pop(
            key,
            None,
        )

        return existed

    # ------------------------------------------------------------------
    # NORMALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_side(side: str) -> str:
        value = str(side).upper()

        if value in {"BUY", "LONG"}:
            return "LONG"

        if value in {"SELL", "SHORT"}:
            return "SHORT"

        raise ValueError(
            f"Unsupported DCA side: {side}"
        )

    @staticmethod
    def _key(
        asset: str,
        side: str,
    ) -> str:
        return (
            f"{str(asset).upper()}:"
            f"{str(side).upper()}"
        )

    @staticmethod
    def _enum_value(value: Any) -> str:
        return str(
            getattr(
                value,
                "value",
                value,
            )
        )

    @staticmethod
    def _bounded_score(
        value: Optional[float],
    ) -> float:
        try:
            number = float(
                value
                if value is not None
                else 0.0
            )
        except (TypeError, ValueError):
            return 0.0

        if number != number:
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                number,
            ),
        )
