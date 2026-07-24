from datetime import datetime, timezone

from aios.memory import EventStore, MemoryEvent


class StrategyEvaluationStore:

    def __init__(self):

        self.store = EventStore()


    def record(
        self,
        strategy,
        current_version,
        candidate_version,
        evaluation,
    ):

        event = MemoryEvent(
            event_type="strategy_evaluation",
            action=evaluation.get(
                "decision",
                "unknown",
            ),
            source="aios_strategy",
            metadata={
                "strategy": strategy,
                "current_version": current_version,
                "candidate_version": candidate_version,
                "evaluation": evaluation,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            },
        )

        self.store.append(
            event
        )

        return event


    def history(
        self,
        strategy=None,
    ):

        results = []

        for event in self.store.all():

            if event.get(
                "event_type"
            ) != "strategy_evaluation":
                continue


            metadata = event.get(
                "metadata",
                {}
            )

            if (
                strategy
                and
                metadata.get("strategy") != strategy
            ):
                continue


            results.append(
                metadata
            )


        return results
