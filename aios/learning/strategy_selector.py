class StrategySelector:

    def select(
        self,
        candidates,
    ):

        ranked = []

        for candidate in candidates:

            confidence = float(
                candidate.get(
                    "confidence",
                    0,
                )
            )

            learning_score = float(
                candidate.get(
                    "learning_score",
                    0,
                )
            )

            combined_score = (
                confidence / 100 * 0.7
                +
                learning_score * 0.3
            )

            ranked.append(
                {
                    **candidate,
                    "strategy_score": round(
                        combined_score,
                        4,
                    ),
                }
            )

        return sorted(
            ranked,
            key=lambda x: x["strategy_score"],
            reverse=True,
        )
