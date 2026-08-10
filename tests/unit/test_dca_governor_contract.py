import inspect

from core.dca_config import DCAConfig
from core.dca_governor import DCAGovernor, GovernorCommand
from core.dca_execution_bridge import DCAExecutionBridge
from core.dca_state_machine import (
    DCAState,
    DCAMode,
    DCAPhase,
    AddingState,
)
from core.dca_planner import DCAPlan, DCAPlanner
from core.dca_risk_guard import DCARiskGuard
from monitoring.dca_supervisor import (
    DCASupervisor,
    SupervisorDecision,
)


def test_governor_public_contract():
    config = DCAConfig()

    assert inspect.isclass(DCAGovernor)
    assert inspect.isclass(GovernorCommand)
    assert inspect.isclass(DCAExecutionBridge)
    assert inspect.isclass(DCAPlan)
    assert inspect.isclass(DCAPlanner)
    assert inspect.isclass(DCARiskGuard)
    assert inspect.isclass(DCASupervisor)


def test_governor_can_initialize_with_canonical_config():
    config = DCAConfig()
    governor = DCAGovernor(config)

    assert governor is not None
    assert hasattr(governor, "start_dca")
    assert hasattr(governor, "tick")
    assert hasattr(governor, "request_close")


def test_governor_start_creates_canonical_position_state():
    config = DCAConfig()
    governor = DCAGovernor(config)

    command = governor.start_dca(
        asset="ETH",
        side="LONG",
        entry_price=2500.0,
    )

    assert isinstance(command, GovernorCommand)
    assert command.plan.asset == "ETH"
    assert command.plan.side == "LONG"
    assert command.plan.entry_price == 2500
    assert command.state.mode in set(DCAMode)
    assert command.state.phase in set(DCAPhase)
    assert command.state.adding_state in set(AddingState)


def test_governor_tick_returns_single_command():
    config = DCAConfig()
    governor = DCAGovernor(config)

    governor.start_dca(
        asset="ETH",
        side="LONG",
        entry_price=2500.0,
    )

    command = governor.tick(
        asset="ETH",
        side="LONG",
        current_price=2500.0,
        available_budget=10000.0,
        ai_confidence=0.0,
        learner_score=0.0,
    )

    assert isinstance(command, GovernorCommand)
    assert command.action in {
        "ADD",
        "ACCELERATE",
        "REPRICE",
        "HARVEST",
        "PROTECT",
        "CLOSE",
        "HOLD",
        "BLOCK",
    }


def test_governor_unknown_position_blocks():
    config = DCAConfig()
    governor = DCAGovernor(config)

    command = governor.tick(
        asset="UNKNOWN",
        side="LONG",
        current_price=2500.0,
        available_budget=10000.0,
    )

    assert isinstance(command, GovernorCommand)
    assert command.action == "BLOCK"


def test_execution_bridge_requires_executor():
    try:
        DCAExecutionBridge(None)
    except (TypeError, ValueError):
        return

    raise AssertionError(
        "DCAExecutionBridge must reject a missing production executor"
    )


def test_risk_guard_is_decision_only():
    config = DCAConfig()
    guard = DCARiskGuard(config)

    assert callable(guard.can_add)
    assert callable(guard.can_accelerate)
    assert callable(guard.can_reprice)
    assert callable(guard.can_protect_profit)
    assert callable(guard.can_close)


def test_supervisor_is_decision_only():
    config = DCAConfig()
    guard = DCARiskGuard(config)
    supervisor = DCASupervisor(config, guard)

    assert supervisor is not None
    assert callable(supervisor.evaluate)
