from collections import defaultdict

from .optimizer_store import OptimizerStore


class PlannerOptimizer:

    def __init__(self):

        self.history = []

        self.capability_scores = defaultdict(list)

        self.recommendations = []
        self.store = OptimizerStore()


    def update(
        self,
        feedback,
    ):

        self.history.append(
            feedback
        )

        key = ":".join(
            [
                feedback.strategy or "UNKNOWN",
                feedback.asset or "UNKNOWN",
                feedback.signal or "UNKNOWN",
            ]
        )

        self.capability_scores[
            key
        ].append(
            feedback.score
        )

        self.store.save_score(
            key,
            feedback.score,
        )


        for observation in feedback.observations:

            if "failed" in observation.lower():

                self.recommendations.append(
                    {
                        "type": "failure",
                        "observation": observation,
                    }
                )


        return feedback


    def capability_performance(
        self,
    ):

        return {
            key: (
                sum(scores) / len(scores)
            )
            for key, scores in self.capability_scores.items()
        }


    def get_recommendations(
        self,
    ):

        return self.recommendations
