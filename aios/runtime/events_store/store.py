class RuntimeEventStore:

    def __init__(self):
        self._events = []

    def add(self, event):
        self._events.append(event)
        return event

    def latest(self, limit=10):
        return tuple(
            self._events[-limit:]
        )

    def all(self):
        return tuple(self._events)

    def count(self):
        return len(self._events)

    def clear(self):
        self._events.clear()

    def __len__(self):
        return len(self._events)
