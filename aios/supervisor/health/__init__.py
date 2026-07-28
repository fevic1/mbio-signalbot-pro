from dataclasses import dataclass, field
from enum import Enum


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class HealthStatus:
    component: str
    state: HealthState = HealthState.UNKNOWN
    message: str = ""
    metadata: dict = field(default_factory=dict)


from .handler import SupervisorHealthHandler

__all__ = [
    "HealthStatus",
    "HealthState",
    "SupervisorHealthHandler",
]
