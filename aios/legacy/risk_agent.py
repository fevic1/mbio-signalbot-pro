from .base import BaseAgent


class RiskAgent(BaseAgent):

    def __init__(
        self,
        memory=None
    ):

        super().__init__(
            name="Risk Analyst",
            role="Identify investment risks",
            memory=memory
        )


    def analyze(
        self,
        context
    ):

        fundamental = context.get_result(
            "FundamentalAgent"
        )

        result = {
            "risks": [
                "Tokenomics risk",
                "Liquidity risk",
                "Development risk",
                "Market risk"
            ],
            "input": fundamental
        }


        self.remember(
            "Risk Analysis",
            str(result),
            {
                "agent": self.name
            }
        )


        return self.report(
            result
        )
