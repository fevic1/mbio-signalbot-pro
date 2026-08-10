"""MBIO DCA Governor state machine.

Pure decision/state logic. No exchange calls.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DCAMode(Enum):
    RECOVERY = "RECOVERY"
    HARVEST = "HARVEST"
    HYBRID = "HYBRID"


class DCAPhase(Enum):
    ACCUMULATION = "ACCUMULATION"
    HARVEST = "HARVEST"
    PROTECT = "PROTECT"
    CLOSE = "CLOSE"
    COMPLETE = "COMPLETE"


class AddingState(Enum):
    ALLOWED = "ALLOWED"
    PAUSED = "PAUSED"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"


class DCAAction(Enum):
    HOLD = "HOLD"
    ADD = "ADD"
    REPRICE = "REPRICE"
    HARVEST = "HARVEST"
    PROTECT = "PROTECT"
    CLOSE = "CLOSE"


@dataclass(frozen=True)
class DCADirective:
    action: DCAAction
    mode: DCAMode
    phase: DCAPhase
    reason: str

    add_allowed: bool = False
    add_level: Optional[int] = None
    add_multiplier: Optional[float] = None

    reprice_allowed: bool = False

    harvest_allowed: bool = False
    harvest_pct: float = 0.0
    harvest_profit_usd: float = 0.0
    reduce_only: bool = False

    trailing_allowed: bool = False
    trailing_stop_price: Optional[float] = None

    close_allowed: bool = False


@dataclass
class DCAState:
    mode: DCAMode = DCAMode.HYBRID
    phase: DCAPhase = DCAPhase.ACCUMULATION
    adding_state: AddingState = AddingState.ALLOWED

    side: str = "LONG"
    entry_price: float = 0.0
    current_price: float = 0.0

    levels_filled: int = 0
    total_filled_size: float = 0.0
    avg_entry_price: float = 0.0

    unrealized_pnl_pct: float = 0.0
    unrealized_pnl_usd: float = 0.0
    realized_pnl_usd: float = 0.0

    local_low: Optional[float] = None
    local_high: Optional[float] = None

    profit_target_reached: bool = False
    trailing_stop_price: Optional[float] = None

    harvest_count: int = 0
    last_harvest_price: Optional[float] = None
    harvested_pnl_usd: float = 0.0

    consecutive_losses: int = 0
    consecutive_unfilled_levels: int = 0
    last_fill_at: Optional[str] = None

    accelerated_levels: int = 0

    def can_add(self) -> bool:
        return self.adding_state == AddingState.ALLOWED

    def can_harvest(self) -> bool:
        return (
            self.mode in (DCAMode.HARVEST, DCAMode.HYBRID)
            and self.phase in (DCAPhase.HARVEST, DCAPhase.PROTECT)
        )

    def can_apply_trailing(self) -> bool:
        return (
            self.mode in (DCAMode.HARVEST, DCAMode.HYBRID)
            and self.phase == DCAPhase.PROTECT
        )


class DCATransitionRules:
    def __init__(self, config):
        self.config = config
        self.config.assert_valid()

    @staticmethod
    def _copy_state(state: DCAState) -> DCAState:
        values = vars(state).copy()
        return DCAState(**values)

    def evaluate(self, state: DCAState, current_price: float):
        if current_price <= 0:
            return (
                state,
                DCADirective(
                    DCAAction.HOLD,
                    state.mode,
                    state.phase,
                    "invalid market price",
                ),
            )

        new = self._copy_state(state)
        new.current_price = float(current_price)

        self._update_extremes(new)
        self._update_pnl(new)
        self._update_target(new)

        if new.phase == DCAPhase.CLOSE:
            return new, self._close(new, "close already requested")

        self._transition(new)
        new.adding_state = self._adding_permission(new)

        return new, self._directive(new)

    def _update_extremes(self, state):
        p = state.current_price

        if state.local_low is None:
            state.local_low = p
        else:
            state.local_low = min(state.local_low, p)

        if state.local_high is None:
            state.local_high = p
        else:
            state.local_high = max(state.local_high, p)

    def _update_pnl(self, state):
        avg = state.avg_entry_price
        if avg <= 0:
            return

        if state.side.upper() == "LONG":
            state.unrealized_pnl_pct = ((state.current_price - avg) / avg) * 100
        else:
            state.unrealized_pnl_pct = ((avg - state.current_price) / avg) * 100

    def _bounce_pct(self, state):
        if state.side.upper() == "LONG":
            if not state.local_low:
                return 0.0
            return max(
                0.0,
                ((state.current_price - state.local_low) / state.local_low) * 100,
            )

        if not state.local_high:
            return 0.0
        return max(
            0.0,
            ((state.local_high - state.current_price) / state.local_high) * 100,
        )

    def _update_target(self, state):
        target = self.config.protection.profit_target_pct
        if target is None or state.avg_entry_price <= 0:
            return

        if state.unrealized_pnl_pct >= target:
            state.profit_target_reached = True

    def _transition(self, state):
        p = self.config.protection

        if state.mode == DCAMode.RECOVERY:
            if state.profit_target_reached:
                state.phase = DCAPhase.CLOSE
            else:
                state.phase = DCAPhase.ACCUMULATION
            return

        if state.mode == DCAMode.HARVEST:
            if state.levels_filled > 0:
                state.phase = DCAPhase.HARVEST

            if (
                p.trailing_exit_enabled
                and state.unrealized_pnl_pct >= p.profit_to_protect_pct
            ):
                state.phase = DCAPhase.PROTECT
            return

        if state.phase == DCAPhase.ACCUMULATION:
            if (
                state.levels_filled > 0
                and self._bounce_pct(state) >= p.bounce_to_harvest_pct
            ):
                state.phase = DCAPhase.HARVEST

        elif state.phase == DCAPhase.HARVEST:
            if (
                p.trailing_exit_enabled
                and state.unrealized_pnl_pct >= p.profit_to_protect_pct
            ):
                state.phase = DCAPhase.PROTECT
            elif state.unrealized_pnl_pct <= -p.deterioration_pct:
                state.phase = DCAPhase.ACCUMULATION

        elif state.phase == DCAPhase.PROTECT:
            if self._trailing_hit(state):
                state.phase = DCAPhase.CLOSE
                return

            if state.unrealized_pnl_pct <= -p.deterioration_pct:
                state.phase = DCAPhase.ACCUMULATION
                state.trailing_stop_price = None
                return

            self._update_trailing(state)

    def _adding_permission(self, state):
        g = self.config.guardrails

        if state.adding_state == AddingState.BLOCKED:
            return AddingState.BLOCKED

        if state.adding_state == AddingState.COMPLETE:
            return AddingState.COMPLETE

        if state.levels_filled >= min(self.config.levels, g.max_levels):
            return AddingState.COMPLETE

        if g.pause:
            return AddingState.PAUSED

        if state.consecutive_losses >= g.consecutive_loss_breaker:
            return AddingState.PAUSED

        return AddingState.ALLOWED

    def _update_trailing(self, state):
        p = self.config.protection
        if not p.trailing_exit_enabled or state.current_price <= 0:
            return

        distance = p.trailing_exit_pct / 100.0

        if state.side.upper() == "LONG":
            candidate = state.current_price * (1 - distance)
            if (
                state.trailing_stop_price is None
                or candidate > state.trailing_stop_price
            ):
                state.trailing_stop_price = candidate
        else:
            candidate = state.current_price * (1 + distance)
            if (
                state.trailing_stop_price is None
                or candidate < state.trailing_stop_price
            ):
                state.trailing_stop_price = candidate

    def _trailing_hit(self, state):
        if state.trailing_stop_price is None:
            return False

        if state.side.upper() == "LONG":
            return state.current_price <= state.trailing_stop_price

        return state.current_price >= state.trailing_stop_price

    def _directive(self, state):
        if state.phase == DCAPhase.CLOSE:
            return self._close(state, "governor close condition reached")

        if state.phase == DCAPhase.PROTECT:
            return DCADirective(
                action=DCAAction.PROTECT,
                mode=state.mode,
                phase=state.phase,
                reason="profit protection phase active",
                trailing_allowed=state.can_apply_trailing(),
                trailing_stop_price=state.trailing_stop_price,
                reduce_only=True,
            )

        if state.phase == DCAPhase.HARVEST:
            return self._harvest(state)

        if state.adding_state == AddingState.ALLOWED:
            return DCADirective(
                action=DCAAction.ADD,
                mode=state.mode,
                phase=state.phase,
                reason="DCA addition permitted by governor",
                add_allowed=True,
                add_level=state.levels_filled + 1,
                add_multiplier=1.0,
            )

        return DCADirective(
            action=DCAAction.HOLD,
            mode=state.mode,
            phase=state.phase,
            reason=f"adding state: {state.adding_state.value}",
        )

    def _harvest(self, state):
        p = self.config.protection

        if not p.profit_ratchet_enabled:
            return DCADirective(
                DCAAction.HOLD,
                state.mode,
                state.phase,
                "profit ratchet disabled",
            )

        if state.unrealized_pnl_usd < p.min_harvest_profit_usd:
            return DCADirective(
                DCAAction.HOLD,
                state.mode,
                state.phase,
                "harvest threshold not reached",
            )

        if state.last_harvest_price is not None:
            if state.side.upper() == "LONG":
                move = state.current_price - state.last_harvest_price
            else:
                move = state.last_harvest_price - state.current_price

            if move <= 0:
                return DCADirective(
                    DCAAction.HOLD,
                    state.mode,
                    state.phase,
                    "waiting for next profitable ratchet step",
                )

        return DCADirective(
            action=DCAAction.HARVEST,
            mode=state.mode,
            phase=state.phase,
            reason="profit-harvest threshold reached",
            harvest_allowed=True,
            harvest_pct=p.harvest_pct,
            harvest_profit_usd=state.unrealized_pnl_usd,
            reduce_only=True,
        )

    @staticmethod
    def _close(state, reason):
        return DCADirective(
            action=DCAAction.CLOSE,
            mode=state.mode,
            phase=DCAPhase.CLOSE,
            reason=reason,
            close_allowed=True,
            reduce_only=True,
        )
