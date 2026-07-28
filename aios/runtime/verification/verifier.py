from datetime import datetime, timezone


class RuntimeVerifier:

    def __init__(self):
        self._checks = {}
        self._history = []

    def register(self, name: str, check):
        self._checks[name] = check
        return check

    def remove(self, name: str):
        return self._checks.pop(name, None)

    def verify(self, target=None):
        results = {}

        for name, check in self._checks.items():
            try:
                results[name] = {
                    "passed": bool(check(target)),
                    "error": None,
                }

            except Exception as exc:
                results[name] = {
                    "passed": False,
                    "error": str(exc),
                }

        record = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "results": results,
        }

        self._history.append(record)

        return record

    def history(self):
        return tuple(self._history)

    def checks(self):
        return tuple(sorted(self._checks))

    def clear(self):
        self._checks.clear()
        self._history.clear()

    def __contains__(self, name):
        return name in self._checks

    def __len__(self):
        return len(self._checks)
