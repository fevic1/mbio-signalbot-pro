from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RecoveryProposal:

    action: str

    reason: str

    priority: str

    metadata: dict

    timestamp: str = ""


    def __post_init__(self):

        if not self.timestamp:

            self.timestamp = datetime.now(
                timezone.utc
            ).isoformat()


    def describe(self):

        return {
            "action": self.action,
            "reason": self.reason,
            "priority": self.priority,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
