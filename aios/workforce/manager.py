from .registry import AgentRegistry
from .team_builder import TeamBuilder


class WorkforceManager:


    def __init__(self):

        self.registry = AgentRegistry()

        self.builder = TeamBuilder(
            self.registry
        )


    def register(
        self,
        agent,
    ):

        return self.registry.register(
            agent
        )


    def assemble_team(
        self,
        capabilities,
    ):

        return self.builder.build(
            capabilities
        )
