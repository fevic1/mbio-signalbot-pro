from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ProjectHealth:

    project_id: str

    status: str

    progress: float

    issues: list = field(
        default_factory=list
    )

    recommendations: list = field(
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
            "status": self.status,
            "progress": self.progress,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp,
        }
