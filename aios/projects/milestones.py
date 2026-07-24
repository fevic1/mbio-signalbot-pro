from dataclasses import dataclass, field
import uuid


@dataclass
class Milestone:

    name: str

    description: str = ""

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    status: str = "pending"

    tasks: list = field(
        default_factory=list
    )


    def add_task(
        self,
        task,
    ):

        self.tasks.append(
            task
        )


    def complete(self):

        self.status = "completed"


    def describe(self):

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "tasks": self.tasks,
        }
