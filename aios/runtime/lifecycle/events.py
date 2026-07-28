from dataclasses import dataclass
from enum import Enum


class LifecyclePhase(str, Enum):
    CREATED = "created"
    INITIALIZING = "initializing"
    STARTED = "started"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass(slots=True)
class LifecycleEvent:
    phase: LifecyclePhase
    component: str
