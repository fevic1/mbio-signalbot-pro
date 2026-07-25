from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class CouncilSession:

    question: str

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )

    responses: list = field(
        default_factory=list
    )

    decision: dict | None = None

    created_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def add_response(
        self,
        response,
    ):

        self.responses.append(
            response
        )


    def finalize(
        self,
        decision,
    ):

        self.decision = decision



    def set_decision(
        self,
        decision,
    ):

        self.decision = decision



    def status(self):

        return {
            "id": self.id,
            "question": self.question,
            "response_count": len(self.responses),
            "decision": self.decision,
        }


    def describe(self):

        return {
            "id": self.id,
            "question": self.question,
            "responses": self.responses,
            "decision": self.decision,
            "created_at": self.created_at,
        }
