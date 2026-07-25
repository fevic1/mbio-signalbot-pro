from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class PolicyBinding:


    policy_name: str

    policy_version: int

    decision_id: str

    session_id: str

    evidence: dict

    governance: dict


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

            "policy":
                {
                    "name":
                        self.policy_name,

                    "version":
                        self.policy_version,
                },

            "decision_id":
                self.decision_id,

            "session_id":
                self.session_id,

            "evidence":
                self.evidence,

            "governance":
                self.governance,

            "created_at":
                self.created_at,

        }
