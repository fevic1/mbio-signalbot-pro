from .agent import AgentRuntime
from .registry import AgentRegistry


class AgentManager:


    def __init__(self):

        self.registry = AgentRegistry()



    def create_agent(
        self,
        name,
        role,
        capabilities=None,
    ):

        agent = AgentRuntime(
            name=name,
            role=role,
            capabilities=capabilities or [],
        )

        self.registry.register(
            agent
        )

        return agent



    def start_agent(
        self,
        name,
    ):

        agent = self.registry.get(
            name
        )

        if not agent:
            raise ValueError(
                "Agent not found"
            )

        agent.start()

        return agent.describe()



    def stop_agent(
        self,
        name,
    ):

        agent = self.registry.get(
            name
        )

        if not agent:
            raise ValueError(
                "Agent not found"
            )

        agent.stop()

        return agent.describe()



    def describe(self):

        return self.registry.list()
