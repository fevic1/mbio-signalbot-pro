from datetime import datetime, timezone

from aios.memory import EventStore, MemoryEvent


class OptimizerStore:

    def __init__(self):

        self.store = EventStore()


    def save_score(
        self,
        key,
        score,
    ):

        event = MemoryEvent(
            event_type="optimizer_learning",
            action="score_recorded",
            source="aios_optimizer",
            metadata={
                "key": key,
                "score": score,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        self.store.append(event)

        return event


    def history(self):

        return [
            event
            for event in self.store.all()
            if event.get("event_type")
            == "optimizer_learning"
        ]
