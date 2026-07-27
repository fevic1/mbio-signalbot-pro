from collections import deque
from datetime import datetime, timezone
from threading import Lock


class ExecutionEventStore:
    """
    MBIO SignalPro execution telemetry read model.

    Stores execution lifecycle events for dashboard consumption.
    Does not control execution.
    """

    def __init__(self, max_events: int = 500):
        self.events = deque(maxlen=max_events)
        self.lock = Lock()


    def record(self, event_type: str, payload: dict):
        event = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }

        with self.lock:
            self.events.append(event)


    def latest(self):
        with self.lock:
            return list(self.events)


execution_event_store = ExecutionEventStore()
