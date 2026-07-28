from aios.core.events import EventBus


class EventPublisher:

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def publish(self, event):
        return self.event_bus.publish(event)
