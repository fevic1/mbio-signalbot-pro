from datetime import datetime, timezone


class MemoryWriter:

    def snapshot(
        self,
        context,
    ):

        return {
            "timestamp": datetime.now(
                UTC
            ).isoformat(),
            "task": context.get(
                "task_plan",
            ),
            "reflection": context.get(
                "reflection",
            ),
            "verification": context.get(
                "verification",
            ),
            "metrics": context.get(
                "metrics",
            ),
        }
