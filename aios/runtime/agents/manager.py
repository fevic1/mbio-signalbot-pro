from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(slots=True)
class RuntimeAgent:
    id: str
    name: str
    role: str
    state: str = "created"
    metadata: dict = field(default_factory=dict)
    created: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


class RuntimeAgentManager:

    def __init__(self):
        self._agents = {}

    def register(
        self,
        name: str,
        role: str,
        metadata=None,
    ):
        agent = RuntimeAgent(
            id=str(uuid.uuid4()),
            name=name,
            role=role,
            metadata=metadata or {},
        )

        self._agents[agent.id] = agent
        return agent

    def start(self, agent_id: str):
        agent = self._agents[agent_id]
        agent.state = "running"
        return agent

    def stop(self, agent_id: str):
        agent = self._agents[agent_id]
        agent.state = "stopped"
        return agent

    def get(self, agent_id: str):
        return self._agents.get(agent_id)

    def running(self):
        return tuple(
            agent
            for agent in self._agents.values()
            if agent.state == "running"
        )

    def all(self):
        return tuple(self._agents.values())

    def clear(self):
        self._agents.clear()

    def __len__(self):
        return len(self._agents)
