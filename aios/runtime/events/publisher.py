from aios.core.events.publisher import EventPublisher
from aios.events import AIOSDomainEvent


class RuntimeEventPublisher:

    def __init__(self, event_bus):
        self.event_bus = event_bus


    def started(self, details=None):

        return self.event_bus.publish(
            AIOSDomainEvent(
                event_type="runtime.started",
                source="aios_runtime",
                payload=details or {},
            )
        )


    def checked(self, details=None):

        return self.event_bus.publish(
            AIOSDomainEvent(
                event_type="runtime.checked",
                source="aios_runtime",
                payload=details or {},
            )
        )


    def stopped(self, details=None):

        return self.event_bus.publish(
            AIOSDomainEvent(
                event_type="runtime.stopped",
                source="aios_runtime",
                payload=details or {},
            )
        )
