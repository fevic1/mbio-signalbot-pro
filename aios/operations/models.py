from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class OperationEvent:

    action: str

    status: str

    details: dict = field(
        default_factory=dict
    )

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )

    timestamp: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def describe(self):

        return {
            "id": self.id,
            "action": self.action,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp,
        }
