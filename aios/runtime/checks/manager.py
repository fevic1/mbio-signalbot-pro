from datetime import datetime, timezone


class RuntimeCheckManager:

    def __init__(self):
        self._checks = {}

    def register(self, name: str, check):
        self._checks[name] = check
        return check

    def remove(self, name: str):
        return self._checks.pop(name, None)

    def run(self):
        results = {}

        for name, check in self._checks.items():
            started = datetime.now(timezone.utc)

            try:
                result = check()

                results[name] = {
                    "passed": bool(result),
                    "error": None,
                    "timestamp": started.isoformat(),
                }

            except Exception as exc:
                results[name] = {
                    "passed": False,
                    "error": str(exc),
                    "timestamp": started.isoformat(),
                }

        return results

    def passed(self):
        return all(
            item["passed"]
            for item in self.run().values()
        )

    def names(self):
        return tuple(sorted(self._checks))

    def clear(self):
        self._checks.clear()

    def __contains__(self, name):
        return name in self._checks

    def __len__(self):
        return len(self._checks)
