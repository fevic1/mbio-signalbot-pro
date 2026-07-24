from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RuntimeState:

    status: str

    pid: int | None = None

    timestamp: str = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def describe(self):

        return {
            "status": self.status,
            "pid": self.pid,
            "timestamp": self.timestamp,
        }
