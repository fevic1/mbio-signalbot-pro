from .base import BaseAgent


class FundamentalAgent(BaseAgent):

    def __init__(
        self,
        memory=None
    ):

        super().__init__(
            name="Fundamental Analyst",
            role="Evaluate project quality",
            memory=memory
        )


    def analyze(
        self,
        context
    ):

        research = context.get_result(
            "ResearchAgent"
        )

        result = {
            "evaluation": [
                "Technology",
                "Team",
                "Adoption",
                "Tokenomics"
            ],
            "research_input": research
        }


        return self.report(
            result
        )
