from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class AIOSDomainEvent:

    event_type: str

    source: str

    payload: dict = field(
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
            "event_type": self.event_type,
            "source": self.source,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }
