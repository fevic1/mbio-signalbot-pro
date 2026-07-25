
from dataclasses import dataclass


@dataclass
class CouncilTask:

    category: str

    objective: str

    agent: str

    capabilities: list[str]


class CouncilTaskBuilder:


    def build(
        self,
        agent,
        question,
    ):

        return CouncilTask(
            category="analysis",
            objective=question,
            agent=agent.name,
            capabilities=agent.capabilities,
        ).__dict__
