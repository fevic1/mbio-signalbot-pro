from datetime import datetime, timezone


class RuntimeRateLimiter:

    def __init__(self):
        self._rules = {}
        self._hits = {}

    def configure(
        self,
        name: str,
        maximum: int,
        window_seconds: int,
    ):
        self._rules[name] = {
            "maximum": maximum,
            "window_seconds": window_seconds,
        }

        self._hits.setdefault(name, [])

    def allow(self, name: str):
        if name not in self._rules:
            return True

        now = datetime.now(timezone.utc)

        rule = self._rules[name]
        window = rule["window_seconds"]

        history = [
            timestamp
            for timestamp in self._hits[name]
            if (
                now - timestamp
            ).total_seconds() <= window
        ]

        self._hits[name] = history

        if len(history) >= rule["maximum"]:
            return False

        self._hits[name].append(now)
        return True

    def reset(self, name=None):
        if name:
            self._hits[name] = []
        else:
            self._hits.clear()

    def export(self):
        return {
            name: {
                "maximum": rule["maximum"],
                "window_seconds": rule["window_seconds"],
                "current": len(
                    self._hits.get(name, [])
                ),
            }
            for name, rule in self._rules.items()
        }

    def __contains__(self, name):
        return name in self._rules

    def __len__(self):
        return len(self._rules)
