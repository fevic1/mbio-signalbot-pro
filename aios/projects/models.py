from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime, timezone
import uuid


@dataclass
class Project:

    name: str

    description: str = ""

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    status: str = "created"

    goals: List[Dict] = field(
        default_factory=list
    )

    milestones: List[Dict] = field(
        default_factory=list
    )

    created_at: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


    def add_goal(
        self,
        goal,
    ):

        self.goals.append(
            goal
        )


    def add_milestone(
        self,
        milestone,
    ):

        self.milestones.append(
            milestone
        )


    def start(self):

        self.status = "active"


    def complete(self):

        self.status = "completed"


    def describe(self):

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "goals": self.goals,
            "milestones": self.milestones,
            "created_at": self.created_at,
        }
