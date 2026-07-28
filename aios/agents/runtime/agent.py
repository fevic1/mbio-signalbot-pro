from dataclasses import dataclass, field
from enum import Enum


class AgentState(str, Enum):
    IDLE = "idle"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(slots=True)
class Agent:
    id: str
    state: AgentState = AgentState.IDLE
    metadata: dict = field(default_factory=dict)
