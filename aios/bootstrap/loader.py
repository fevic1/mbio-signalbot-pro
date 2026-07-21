from aios.agents import (
    ResearchAgent,
    FundamentalAgent,
    RiskAgent,
    SkepticAgent,
    VerificationAgent
)


class AgentBootstrap:


    def __init__(
        self,
        registry,
        memory=None
    ):

        self.registry = registry
        self.memory = memory


    def load_agents(self):

        agents = [

            {
                "name": "ResearchAgent",
                "agent": ResearchAgent(
                    self.memory
                ),
                "capability":
                    "research",
                "permission":
                    "research"
            },


            {
                "name": "FundamentalAgent",
                "agent": FundamentalAgent(
                    self.memory
                ),
                "capability":
                    "analysis",
                "permission":
                    "research"
            },


            {
                "name": "RiskAgent",
                "agent": RiskAgent(
                    self.memory
                ),
                "capability":
                    "risk_analysis",
                "permission":
                    "research"
            },


            {
                "name": "SkepticAgent",
                "agent": SkepticAgent(
                    self.memory
                ),
                "capability":
                    "critical_analysis",
                "permission":
                    "research"
            },


            {
                "name": "VerificationAgent",
                "agent": VerificationAgent(
                    self.memory
                ),
                "capability":
                    "verification",
                "permission":
                    "research"
            }

        ]


        for item in agents:

            self.registry.register(
                item["name"],
                item["agent"],
                item["capability"],
                permission=item["permission"]
            )


        return self.registry.list_agents()
