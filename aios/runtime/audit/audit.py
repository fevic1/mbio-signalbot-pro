from datetime import datetime, timezone


class RuntimeAudit:

    def __init__(self):
        self._records = []

    def record(self, action: str, actor="runtime", metadata=None):
        event = {
            "action": action,
            "actor": actor,
            "metadata": metadata or {},
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        self._records.append(event)
        return event

    def all(self):
        return tuple(self._records)

    def filter(self, action: str):
        return [
            event
            for event in self._records
            if event["action"] == action
        ]

    def clear(self):
        self._records.clear()

    def __len__(self):
        return len(self._records)
