from datetime import datetime, UTC


class ReflectionEngine:

    def reflect(
        self,
        context,
    ):

        tool_results = context.get(
            "tool_results",
            [],
        )

        total = len(tool_results)
        success = sum(
            1 for r in tool_results
            if r.get("success")
        )

        failed = total - success

        lessons = []

        if failed:
            lessons.append(
                "Improve tool selection."
            )

        if success == total and total:
            lessons.append(
                "Current execution path is reliable."
            )

        return {
            "timestamp": datetime.now(
                UTC
            ).isoformat(),
            "tools": total,
            "successful": success,
            "failed": failed,
            "success_rate": (
                round(success / total,3)
                if total else 0.0
            ),
            "lessons": lessons,
        }
