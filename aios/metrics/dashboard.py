from .reporter import MetricsReporter


class MetricsDashboard:

    def __init__(
        self,
        reporter=None,
    ):

        self.reporter = reporter


    def snapshot(self):

        if not self.reporter:
            return {}

        return self.reporter.generate_report()


    def health(self):

        snapshot = self.snapshot()

        strategies = snapshot.get(
            "strategies",
            {},
        )

        return {
            "tracked_strategies": len(strategies),
            "status": (
                "healthy"
                if strategies
                else "no_data"
            ),
        }
