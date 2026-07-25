from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class AgentRuntime:

    name: str

    role: str

    capabilities: list[str] = field(
        default_factory=list
    )

    state: str = "initialized"

    memory_id: str | None = None

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )

    created_at: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


    def start(self):

        self.state = "running"


    def stop(self):

        self.state = "stopped"


    def describe(self):

        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "capabilities": self.capabilities,
        }
