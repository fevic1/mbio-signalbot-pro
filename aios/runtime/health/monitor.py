from datetime import datetime, timezone


class RuntimeHealthMonitor:

    def __init__(self, kernel):
        self._kernel = kernel
        self._checks = {}

    def register(self, name, check):
        self._checks[name] = check

    def check(self):
        results = {}

        for name, check in self._checks.items():
            try:
                results[name] = {
                    "healthy": bool(check()),
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat(),
                }
            except Exception as exc:
                results[name] = {
                    "healthy": False,
                    "error": str(exc),
                }

        return results

    def healthy(self):
        return all(
            result["healthy"]
            for result in self.check().values()
        )
