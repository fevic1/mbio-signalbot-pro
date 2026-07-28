from aios.core.identifiable import Identifiable

from .event_store import EventStore


class LearningSearch(Identifiable):

    def __init__(self):

        self.store = EventStore()


    def optimizer_history(
        self,
        key=None,
    ):

        results = []

        for event in self.store.all():

            if event.get("event_type") != "optimizer_learning":
                continue

            metadata = event.get(
                "metadata",
                {}
            )

            stored_key = metadata.get(
                "key",
                "",
            )

            if key:
                if stored_key == key:
                    pass
                elif stored_key.endswith(
                    f":{key}"
                ):
                    pass
                else:
                    continue

            results.append(
                metadata
            )

        return results


    def performance_summary(
        self,
        key,
    ):

        records = self.optimizer_history(
            key
        )

        if not records:
            return {
                "key": key,
                "samples": 0,
                "average_score": 0,
            }


        scores = [
            r.get("score", 0)
            for r in records
        ]

        return {
            "key": key,
            "samples": len(scores),
            "average_score": (
                sum(scores) / len(scores)
            ),
        }
