from datetime import datetime, timezone


class RuntimeTelemetry:

    def __init__(self):
        self._events = []
        self._values = {}

    def record(self, name: str, value=None, metadata=None):
        event = {
            "name": name,
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._events.append(event)
        return event

    def set(self, name: str, value):
        self._values[name] = value

    def get(self, name: str, default=None):
        return self._values.get(name, default)

    def events(self):
        return tuple(self._events)

    def metrics(self):
        return dict(self._values)

    def export(self):
        return {
            "events": list(self._events),
            "metrics": dict(self._values),
        }

    def clear(self):
        self._events.clear()
        self._values.clear()

    def __len__(self):
        return len(self._events)
