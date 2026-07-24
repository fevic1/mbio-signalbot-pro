from .performance_tracker import PerformanceTracker


class TradeOutcomeConsumer:

    def __init__(self):

        self.tracker = PerformanceTracker()

        self.processed = set()


    def consume(
        self,
        event: dict,
    ):

        event_id = event.get(
            "timestamp"
        )

        if not event_id:
            return False


        if event_id in self.processed:
            return False


        if event.get("event_type") != "trade_outcome":
            return False


        metadata = event.get(
            "metadata",
            {}
        )


        trade = {
            "asset": metadata.get(
                "asset",
                "UNKNOWN",
            ),
            "strategy": metadata.get(
                "strategy",
                "UNKNOWN",
            ),
            "pnl": metadata.get(
                "pnl",
                0,
            ),
        }


        self.tracker.record(
            trade
        )


        self.processed.add(
            event_id
        )


        return True


    def strategy_metrics(self):

        return self.tracker.strategy_performance()


    def asset_metrics(self):

        return self.tracker.asset_performance()
