from datetime import datetime, timezone


class RuntimeExecutor:

    def __init__(self):
        self._executions = []

    def execute(self, name: str, action, *args, **kwargs):
        started = datetime.now(timezone.utc)

        try:
            result = action(*args, **kwargs)

            record = {
                "name": name,
                "success": True,
                "result": result,
                "started": started.isoformat(),
                "finished": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

        except Exception as exc:
            record = {
                "name": name,
                "success": False,
                "error": str(exc),
                "started": started.isoformat(),
                "finished": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

        self._executions.append(record)
        return record

    def history(self):
        return tuple(self._executions)

    def clear(self):
        self._executions.clear()

    def __len__(self):
        return len(self._executions)
