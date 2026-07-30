from aios.agents.runtime import AgentRuntime as CanonicalAgentRuntime
from aios.agents.runtime.agent import Agent


class AgentRuntimeAdapter:

    def __init__(self):
        self.runtime = CanonicalAgentRuntime()

    def register(
        self,
        name,
        role,
        tools=None,
        metadata=None,
    ):
        agent = Agent(
            name=name,
            role=role,
            tools=tools or [],
            metadata=metadata or {},
        )

        return self.runtime.register(agent)

    def start(self, agent_id):
        self.runtime.start(agent_id)
        return self.runtime.get(agent_id)

    def stop(self, agent_id):
        self.runtime.stop(agent_id)
        return self.runtime.get(agent_id)

    def get(self, agent_id):
        return self.runtime.get(agent_id)

    def list(self):
        return tuple(self.runtime._agents.values())

    def remove(self, agent_id):
        return self.runtime.unregister(agent_id)
