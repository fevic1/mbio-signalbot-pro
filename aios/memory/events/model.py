from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict


@dataclass
class MemoryEvent:

    event_type: str
    action: str
    source: str = "aios"

    metadata: Dict = field(
        default_factory=dict
    )

    timestamp: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


    def to_dict(self):

        return {
            "event_type": self.event_type,
            "action": self.action,
            "source": self.source,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
