from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AgentContext:

    agent_id: str

    task: str | None = None

    memory_id: str | None = None

    decisions: list = field(
        default_factory=list
    )

    created_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    def add_decision(
        self,
        decision,
    ):

        self.decisions.append(
            decision
        )


    def describe(self):

        return {
            "agent_id": self.agent_id,
            "task": self.task,
            "memory_id": self.memory_id,
            "decisions": self.decisions,
            "created_at": self.created_at,
        }
