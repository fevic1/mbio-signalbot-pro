from .evaluator import StrategyEvaluator
from .evaluation_store import StrategyEvaluationStore


class StrategyWorkflow:

    def __init__(
        self,
        evaluator=None,
        store=None,
    ):

        self.evaluator = evaluator or StrategyEvaluator()

        self.store = store or StrategyEvaluationStore()


    def evaluate_version(
        self,
        strategy,
        current_version,
        candidate_version,
        current_metrics,
        candidate_metrics,
    ):

        evaluation = self.evaluator.evaluate(
            current_metrics,
            candidate_metrics,
        )


        self.store.record(
            strategy,
            current_version,
            candidate_version,
            evaluation,
        )


        return {
            "strategy": strategy,
            "current_version": current_version,
            "candidate_version": candidate_version,
            "evaluation": evaluation,
        }
