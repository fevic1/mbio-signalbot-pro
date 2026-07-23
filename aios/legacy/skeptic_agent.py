from .base import BaseAgent


class SkepticAgent(BaseAgent):

    def __init__(
        self,
        memory=None
    ):

        super().__init__(
            name="Skeptic Agent",
            role="Challenge investment thesis",
            memory=memory
        )


    def analyze(
        self,
        context
    ):

        risk_analysis = context.get_result(
            "RiskAgent"
        )

        result = {
            "challenge": [
                "What could make this wrong?",
                "What assumptions are weak?",
                "What evidence is missing?"
            ],
            "thesis": risk_analysis
        }


        return self.report(
            result
        )
