from .base import BaseAgent


class ResearchAgent(BaseAgent):

    def __init__(
        self,
        memory=None
    ):

        super().__init__(
            name="Research Agent",
            role="Collect project intelligence",
            memory=memory
        )


    def analyze(
        self,
        context
    ):

        task = context.task

        objective = task.get(
            "name",
            "Unknown Project"
        )

        result = {
            "project": objective,
            "analysis": [
                "Collect fundamentals",
                "Collect development activity",
                "Collect ecosystem data"
            ]
        }


        self.remember(
            f"{objective} Research",
            str(result),
            {
                "agent": self.name
            }
        )


        return self.report(
            result
        )
