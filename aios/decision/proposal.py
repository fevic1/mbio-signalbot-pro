from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Proposal:

    title: str

    description: str

    category: str

    created_by: str

    id: str = field(
        default_factory=lambda:
            str(uuid.uuid4())
    )

    created_at: str = field(
        default_factory=lambda:
            datetime.utcnow().isoformat()
    )

    opinions: list = field(
        default_factory=list
    )

    status: str = "pending"


    def add_opinion(
        self,
        agent,
        opinion,
        confidence
    ):

        self.opinions.append(
            {
                "agent": agent,

                "opinion": opinion,

                "confidence": confidence,

                "timestamp":
                    datetime.utcnow()
                    .isoformat()
            }
        )


    def summary(self):

        return {

            "id": self.id,

            "title": self.title,

            "category": self.category,

            "status": self.status,

            "opinions":
                len(self.opinions)

        }

