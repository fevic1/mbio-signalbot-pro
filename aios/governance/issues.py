from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class SystemIssue:

    title: str

    description: str

    severity: str

    source: str

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )

    status: str = "detected"

    created_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def requires_council(self):

        return self.severity in [
            "high",
            "critical",
        ]


    def describe(self):

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "source": self.source,
            "status": self.status,
            "created_at": self.created_at,
        }
