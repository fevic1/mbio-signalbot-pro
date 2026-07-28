from datetime import datetime, timezone


class RuntimeMetrics:

    def __init__(self):
        self._counters = {}
        self._started = datetime.now(timezone.utc)

    def increment(self, name: str, value: int = 1):
        self._counters[name] = (
            self._counters.get(name, 0) + value
        )

    def get(self, name: str, default=0):
        return self._counters.get(name, default)

    def set(self, name: str, value):
        self._counters[name] = value

    def export(self):
        return {
            "started": self._started.isoformat(),
            "counters": dict(self._counters),
        }

    def clear(self):
        self._counters.clear()

    def __contains__(self, name):
        return name in self._counters

    def __len__(self):
        return len(self._counters)
