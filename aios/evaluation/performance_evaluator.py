class PerformanceEvaluator:


    def __init__(
        self,
        analyzer,
    ):

        self.analyzer = analyzer



    def evaluate(
        self,
        outcome,
    ):

        return self.analyzer.analyze(
            outcome["metrics_before"],
            outcome["metrics_after"],
        )
