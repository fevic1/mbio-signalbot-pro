from enum import Enum


class ExecutionState(str, Enum):

    READY = "ready"

    RUNNING = "running"

    WAITING = "waiting"

    BLOCKED = "blocked"

    FAILED = "failed"

    COMPLETED = "completed"

    PAUSED = "paused"

    CANCELLED = "cancelled"
