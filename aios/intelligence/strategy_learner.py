class StrategyLearner:

    def learn(self, replay):

        stats = {
            "runs": len(replay),
            "successful": 0,
        }

        for item in replay:

            verification = item.get(
                "verification",
            )

            if verification and verification.get(
                "passed",
            ):
                stats["successful"] += 1

        if stats["runs"]:
            stats["success_rate"] = round(
                stats["successful"] / stats["runs"],
                3,
            )
        else:
            stats["success_rate"] = 0.0

        return stats
