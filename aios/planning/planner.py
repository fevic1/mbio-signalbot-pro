from .models import Plan
from .strategy import StrategyGenerator
from .criteria import CriteriaGenerator


class PlanningEngine:


    def __init__(self):

        self.strategy = StrategyGenerator()

        self.criteria = CriteriaGenerator()


    def create_plan(
        self,
        goal,
    ):

        plan = Plan(
            objective=goal.objective
        )


        plan.strategy = (
            self.strategy.generate(
                goal.objective
            )
        )


        for criteria in (
            self.criteria.generate(
                goal.objective
            )
        ):

            plan.add_criteria(
                criteria
            )


        self._infer_capabilities(
            plan
        )


        return plan



    def _infer_capabilities(
        self,
        plan,
    ):

        text = (
            plan.objective.lower()
        )


        mapping = {

            "build": [
                "architecture",
                "planning",
                "code",
                "testing",
                "verification",
            ],

            "research": [
                "research",
                "fact_check",
                "verification",
            ],

            "analyze": [
                "analysis",
                "reasoning",
            ],
        }


        for keyword, capabilities in mapping.items():

            if keyword in text:

                for capability in capabilities:

                    plan.add_capability(
                        capability
                    )
