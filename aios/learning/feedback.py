from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionFeedback:

    execution_id: str

    success: bool

    score: float

    observations: list[str] = field(default_factory=list)

    asset: str = ""

    strategy: str = ""

    signal: str = ""

    pnl: float = 0.0

    confidence: float = 0.0

    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
