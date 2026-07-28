from aios.core.identifiable import Identifiable

from .event_store import EventStore
from .evaluator import DecisionEvaluator


class EvaluationRunner(Identifiable):

    def __init__(self):
        self.store = EventStore()
        self.evaluator = DecisionEvaluator()

    def run(self):

        events = self.store.all()

        decisions = [
            e for e in events
            if e.get("event_type") == "trading_decision"
        ]

        outcomes = [
            e for e in events
            if e.get("event_type") == "trade_outcome"
        ]

        results = []

        for decision in decisions:

            decision_asset = (
                decision
                .get("metadata", {})
                .get("asset")
            )

            matching = next(
                (
                    o for o in outcomes
                    if o.get("metadata", {}).get("asset")
                    == decision_asset
                ),
                None,
            )

            outcome = (
                matching.get("metadata", {})
                if matching
                else {}
            )

            result = self.evaluator.evaluate(
                decision_event=type(
                    "Event",
                    (),
                    {
                        "metadata": decision.get(
                            "metadata",
                            {}
                        )
                    },
                )(),
                outcome=outcome,
            )

            results.append(result)

        return results
