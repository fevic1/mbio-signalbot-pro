from typing import List


class TeamBuilder:


    def __init__(
        self,
        registry,
    ):

        self.registry = registry


    def build(
        self,
        capabilities: List[str],
    ):

        team = []


        for capability in capabilities:

            agents = self.registry.find(
                capability
            )

            if agents:

                agent = agents[0]

                agent.assign()

                team.append(
                    agent
                )


        return team
