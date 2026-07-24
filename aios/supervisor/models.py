from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SupervisorReport:

    checked_projects: int

    issues: list = field(
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
            "checked_projects":
                self.checked_projects,

            "issues":
                self.issues,

            "actions":
                self.actions,

            "timestamp":
                self.timestamp,
        }
