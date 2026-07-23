from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Goal:

    objective: str

    constraints: list[str] = field(default_factory=list)

    priority: int = 1

    status: str = "created"

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    metadata: dict = field(
        default_factory=dict
    )
