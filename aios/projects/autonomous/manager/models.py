from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ProjectOperationResult:

    project_id: str

    health: dict

    decisions: list = field(
        default_factory=list
    )

    actions: list = field(
        default_factory=list
    )

    timestamp: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def describe(self):

        return {
            "project_id": self.project_id,
            "health": self.health,
            "decisions": self.decisions,
            "actions": self.actions,
            "timestamp": self.timestamp,
        }
