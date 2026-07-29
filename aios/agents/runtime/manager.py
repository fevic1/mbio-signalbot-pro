from aios.core.identifiable import Identifiable

from aios.runtime.agents import RuntimeAgentManager


class AgentManager(Identifiable):

    def __init__(self):
        self.runtime = RuntimeAgentManager()
        self.registry = self.runtime


    def create_agent(
        self,
        name,
        role,
        capabilities=None,
    ):

        return self.runtime.register(
            name=name,
            role=role,
            metadata={
                "capabilities": capabilities or [],
            },
        )


    def start_agent(
        self,
        agent_id,
    ):

        return self.runtime.start(
            agent_id
        )


    def stop_agent(
        self,
        agent_id,
    ):

        return self.runtime.stop(
            agent_id
        )


    def describe(self):

        return [
            {
                "id": agent.id,
                "name": agent.name,
                "role": agent.role,
                "state": agent.state,
                "metadata": agent.metadata,
                "capabilities": agent.capabilities,
            }
            for agent in self.runtime.all()
        ]
