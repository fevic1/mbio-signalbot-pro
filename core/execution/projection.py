from collections import deque
from threading import Lock


class ExecutionProjection:

    def __init__(self, max_events=500):
        self.events = deque(maxlen=max_events)
        self.lock = Lock()


    def subscribe(self, event):

        if event.event_type not in (
            "ORDER_SUBMITTED",
            "ORDER_FILLED",
        ):
            return

        with self.lock:
            self.events.append(
                event.describe()
            )


    def recent(self, limit=50):

        with self.lock:
            return list(self.events)[-limit:]
