import logging

from aios.core.observable import Observable


logger = logging.getLogger(__name__)


class EventBus(Observable):

    def __init__(self):
        self.handlers = {}
        self.history = []

    def subscribe(self, event_type, handler):
        self.handlers.setdefault(
            event_type,
            [],
        ).append(handler)

    def publish(self, event):
        if not hasattr(event, "event_type"):
            raise TypeError(
                "EventBus requires an AIOSDomainEvent-compatible object"
            )

        self.history.append(event)

        handlers = list(
            self.handlers.get(event.event_type, [])
        )

        handlers.extend(
            self.handlers.get("*", [])
        )

        for handler in handlers:
            try:
                handler(event)
            except Exception:
                # Observability and learning failures must never
                # break the user-facing execution.
                logger.exception(
                    "AIOS event handler failed: event=%s handler=%r",
                    event.event_type,
                    handler,
                )

        return event

    def get_history(self):
        return [
            event.describe()
            for event in self.history
        ]
