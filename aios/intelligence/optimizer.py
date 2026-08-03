class Optimizer:

    def optimize(self, learner):

        recommendations = []

        if learner["success_rate"] < 0.70:
            recommendations.append(
                "increase_tool_diversity"
            )

        if learner["success_rate"] >= 0.90:
            recommendations.append(
                "promote_strategy"
            )

        return recommendations
