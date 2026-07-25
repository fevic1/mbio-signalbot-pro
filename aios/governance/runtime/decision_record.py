from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class DecisionRecord:

    decision: dict

    session_id: str

    policies: dict

    evidence: list


    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )


    created_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def describe(self):

        return {

            "id":
                self.id,

            "decision":
                self.decision,

            "session_id":
                self.session_id,

            "policies":
                self.policies,

            "evidence":
                self.evidence,

            "created_at":
                self.created_at,

        }
