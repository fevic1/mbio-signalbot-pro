
from datetime import datetime, timezone
import uuid


class AgentRuntime:

    def __init__(self):
        self.agents = {}

    def register(
        self,
        name,
        role,
        tools=None,
        metadata=None,
    ):
        agent_id = str(uuid.uuid4())

        agent = {
            "id": agent_id,
            "name": name,
            "role": role,
            "tools": tools or [],
            "metadata": metadata or {},
            "state": "created",
            "created": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self.agents[agent_id] = agent

        return agent

    def start(self, agent_id):
        agent = self.agents[agent_id]
        agent["state"] = "running"
        return agent

    def stop(self, agent_id):
        agent = self.agents[agent_id]
        agent["state"] = "stopped"
        return agent

    def get(self, agent_id):
        return self.agents.get(agent_id)

    def list(self):
        return tuple(self.agents.values())

    def remove(self, agent_id):
        return self.agents.pop(
            agent_id,
            None
        )
