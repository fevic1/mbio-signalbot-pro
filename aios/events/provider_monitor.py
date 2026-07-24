class ProviderExecutionMonitor:

    def __init__(self, event_bus):

        self.events = []

        event_bus.subscribe(
            "provider_execution.completed",
            self.on_completed,
        )

        event_bus.subscribe(
            "provider_execution.failed",
            self.on_failed,
        )


    def on_completed(self, event):

        self.events.append(
            {
                "type": event.type,
                **event.payload,
                "timestamp": event.time,
            }
        )


    def on_failed(self, event):

        self.events.append(
            {
                "type": event.type,
                **event.payload,
                "timestamp": event.time,
            }
        )


    def recent(self, limit=50):

        return self.events[-limit:]
