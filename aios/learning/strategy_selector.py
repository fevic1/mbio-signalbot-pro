class StrategySelector:

    def __init__(
        self,
        performance_tracker=None,
        optimizer=None,
    ):

        self.performance_tracker = performance_tracker
        self.optimizer = optimizer


    def select(
        self,
        candidates,
    ):

        ranked = []

        for candidate in candidates:

            confidence_score = (
                float(candidate.get("confidence", 0))
                / 100
            )

            optimizer_score = float(
                candidate.get(
                    "learning_score",
                    0,
                )
            )

            performance_score = self._performance_score(
                candidate
            )


            strategy_score = (
                confidence_score * 0.50
                +
                optimizer_score * 0.25
                +
                performance_score * 0.25
            )


            ranked.append(
                {
                    **candidate,
                    "performance_score": round(
                        performance_score,
                        4,
                    ),
                    "strategy_score": round(
                        strategy_score,
                        4,
                    ),
                }
            )


        return sorted(
            ranked,
            key=lambda x: x["strategy_score"],
            reverse=True,
        )


    def _performance_score(
        self,
        candidate,
    ):

        if not self.performance_tracker:
            return 0


        strategy = candidate.get(
            "strategy",
            "HUNTER",
        )


        metrics = (
            self.performance_tracker
            .strategy_performance()
            .get(strategy)
        )


        if not metrics:
            return 0


        expectancy = metrics.get(
            "expectancy",
            0,
        )


        # normalize expectancy
        if expectancy <= 0:
            return 0


        return min(
            expectancy / 100,
            1,
        )
