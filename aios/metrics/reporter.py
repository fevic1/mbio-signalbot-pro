from datetime import datetime, timezone


class MetricsReporter:

    def __init__(
        self,
        performance_tracker=None,
    ):

        self.performance_tracker = performance_tracker


    def generate_report(self):

        if not self.performance_tracker:
            return {
                "timestamp": self._now(),
                "strategies": {},
                "assets": {},
            }


        return {
            "timestamp": self._now(),
            "strategies": (
                self.performance_tracker
                .strategy_performance()
            ),
            "assets": (
                self.performance_tracker
                .asset_performance()
            ),
        }


    def strategy_report(
        self,
        strategy,
    ):

        report = self.generate_report()

        return (
            report
            .get("strategies", {})
            .get(strategy, {})
        )


    def _now(self):

        return datetime.now(
            timezone.utc
        ).isoformat()
