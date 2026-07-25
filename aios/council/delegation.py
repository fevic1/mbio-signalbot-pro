from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class CouncilAssignment:

    agent: str

    task: str

    status: str = "assigned"

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


    def complete(
        self,
    ):

        self.status = "completed"



    def describe(
        self,
    ):

        return {
            "id": self.id,
            "agent": self.agent,
            "task": self.task,
            "status": self.status,
            "created_at": self.created_at,
        }



class DelegationManager:


    def __init__(self):

        self.assignments = []



    def assign(
        self,
        agent,
        task,
    ):

        assignment = CouncilAssignment(
            agent=agent,
            task=task,
        )

        self.assignments.append(
            assignment
        )

        return assignment



    def list(
        self,
    ):

        return [
            item.describe()
            for item
            in self.assignments
        ]
