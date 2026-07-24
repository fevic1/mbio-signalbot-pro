from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RuntimeHealth:

    status: str

    details: dict

    timestamp: str = ""


    def __post_init__(self):

        if not self.timestamp:

            self.timestamp = datetime.now(
                timezone.utc
            ).isoformat()


    def describe(self):

        return {
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp,
        }
