from .optimizer_store import OptimizerStore


class LearningRanker:

    def __init__(self):

        self.store = OptimizerStore()


    def rank(
        self,
        candidates,
    ):

        ranked = []

        for candidate in candidates:

            key = f"{candidate.get('asset')}:{candidate.get('signal')}"

            records = [
                e.get("metadata", {})
                for e in self.store.store.all()
                if e.get("event_type") == "optimizer_learning"
                and e.get("metadata", {}).get("key", "").endswith(key)
            ]

            if records:

                scores = [
                    r.get("score", 0)
                    for r in records
                ]

                average = sum(scores) / len(scores)

                confidence = min(
                    len(scores) / 50,
                    1.0,
                )

                learning_score = average * confidence

            else:

                learning_score = 0


            ranked.append(
                {
                    **candidate,
                    "learning_score": learning_score,
                }
            )


        return sorted(
            ranked,
            key=lambda x: x["learning_score"],
            reverse=True,
        )
