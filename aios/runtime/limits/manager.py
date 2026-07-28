from datetime import datetime, timezone


class RuntimeLimitManager:

    def __init__(self):
        self._limits = {}
        self._usage = {}

    def set(self, name: str, limit: int):
        self._limits[name] = limit
        self._usage.setdefault(name, 0)

    def consume(self, name: str, amount: int = 1):
        if name not in self._limits:
            return True

        current = self._usage.get(name, 0)
        allowed = current + amount <= self._limits[name]

        if allowed:
            self._usage[name] = current + amount

        return allowed

    def reset(self, name=None):
        if name:
            self._usage[name] = 0
        else:
            self._usage.clear()

    def usage(self, name: str):
        return {
            "limit": self._limits.get(name),
            "used": self._usage.get(name, 0),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    def export(self):
        return {
            name: {
                "limit": limit,
                "used": self._usage.get(name, 0),
            }
            for name, limit in self._limits.items()
        }

    def __contains__(self, name):
        return name in self._limits

    def __len__(self):
        return len(self._limits)
