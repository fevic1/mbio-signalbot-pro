from typing import Dict, List

from .models import SpecialistAgent


class AgentRegistry:


    def __init__(self):

        self.agents: Dict[str, SpecialistAgent] = {}


    def register(
        self,
        agent: SpecialistAgent,
    ):

        self.agents[
            agent.name
        ] = agent

        return agent


    def available(
        self,
    ) -> List[SpecialistAgent]:

        return [
            agent
            for agent in self.agents.values()
            if agent.status == "available"
        ]


    def find(
        self,
        capability,
    ):

        return [
            agent
            for agent in self.available()
            if agent.can_handle(capability)
        ]
