"""MBIO DCA Governor compatibility facade.

Canonical implementation lives in core/ and monitoring/.
"""

from core.dca_config import (
    DCAConfig,
    DCAAdaptiveConfig,
    DCAAccelerationConfig,
    DCAProtectionConfig,
    DCAGuardrailConfig,
    DCAModeConfig,
)
from core.dca_planner import (
    DCAPlan,
    DCAPlanBuilder,
    DCALevel,
    DCAPlanner,
)
from core.dca_state_machine import (
    DCAMode,
    DCAPhase,
    DCAState,
    DCATransitionRules,
    AddingState,
    DCAAction,
    DCADirective,
)
from core.dca_risk_guard import DCARiskGuard, RiskVerdict
from monitoring.dca_supervisor import DCASupervisor, SupervisorDecision
from core.dca_governor import DCAGovernor, GovernorCommand
from core.dca_execution_bridge import DCAExecutionBridge

__all__ = [
    "DCAConfig",
    "DCAAdaptiveConfig",
    "DCAAccelerationConfig",
    "DCAProtectionConfig",
    "DCAGuardrailConfig",
    "DCAModeConfig",
    "DCAPlan",
    "DCAPlanBuilder",
    "DCALevel",
    "DCAPlanner",
    "DCAMode",
    "DCAPhase",
    "DCAState",
    "DCATransitionRules",
    "AddingState",
    "DCAAction",
    "DCADirective",
    "DCARiskGuard",
    "RiskVerdict",
    "DCASupervisor",
    "SupervisorDecision",
    "DCAGovernor",
    "GovernorCommand",
    "DCAExecutionBridge",
]
