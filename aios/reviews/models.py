from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ReviewResult:

    reviewer: str

    decision: str

    findings: list = field(
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


    def approved(self):

        return self.decision == "approved"
