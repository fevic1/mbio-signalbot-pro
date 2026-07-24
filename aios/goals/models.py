from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict
import uuid


@dataclass
class Goal:

    objective: str

    priority: str = "normal"

    constraints: List[str] = field(
        default_factory=list
    )

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    status: str = "created"

    tasks: List[Dict] = field(
        default_factory=list
    )

    created_at: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


    def add_task(
        self,
        task,
    ):

        self.tasks.append(
            task
        )


    def start(self):

        self.status = "active"


    def complete(self):

        self.status = "completed"


    def fail(self):

        self.status = "failed"


    def describe(self):

        return {
            "id": self.id,
            "objective": self.objective,
            "priority": self.priority,
            "constraints": self.constraints,
            "status": self.status,
            "tasks": self.tasks,
            "created_at": self.created_at,
        }
