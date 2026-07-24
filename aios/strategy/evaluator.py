class StrategyEvaluator:

    def __init__(
        self,
        min_samples=30,
    ):

        self.min_samples = min_samples


    def evaluate(
        self,
        current_metrics: dict,
        candidate_metrics: dict,
    ):

        current_samples = current_metrics.get(
            "trades",
            0,
        )

        candidate_samples = candidate_metrics.get(
            "trades",
            0,
        )

        if (
            current_samples < self.min_samples
            or
            candidate_samples < self.min_samples
        ):
            return {
                "decision": "insufficient_data",
                "reason": "Minimum sample size not reached",
            }


        current_expectancy = current_metrics.get(
            "expectancy",
            0,
        )

        candidate_expectancy = candidate_metrics.get(
            "expectancy",
            0,
        )


        current_drawdown = current_metrics.get(
            "drawdown",
            0,
        )

        candidate_drawdown = candidate_metrics.get(
            "drawdown",
            0,
        )


        if (
            candidate_expectancy > current_expectancy
            and
            candidate_drawdown <= current_drawdown
        ):

            return {
                "decision": "candidate_preferred",
                "reason": (
                    "Higher expectancy with equal or lower drawdown"
                ),
            }


        return {
            "decision": "keep_current",
            "reason": (
                "Candidate does not outperform current version"
            ),
        }
