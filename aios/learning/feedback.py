from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionFeedback:

    execution_id: str

    success: bool

    score: float

    observations: list[str] = field(default_factory=list)

    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
