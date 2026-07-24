from aios.events import AIOSDomainEvent


class LifecycleEventPublisher:


    def __init__(
        self,
        event_bus,
    ):

        self.event_bus = event_bus



    def publish_starting(self):

        return self.event_bus.publish(
            AIOSDomainEvent(
                event_type="system.starting",
                source="aios_lifecycle",
                payload={}
            )
        )



    def publish_ready(self):

        return self.event_bus.publish(
            AIOSDomainEvent(
                event_type="system.ready",
                source="aios_lifecycle",
                payload={}
            )
        )



    def publish_shutdown(self):

        return self.event_bus.publish(
            AIOSDomainEvent(
                event_type="system.shutdown",
                source="aios_lifecycle",
                payload={}
            )
        )
