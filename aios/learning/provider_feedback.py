class ProviderFeedbackHandler:


    def __init__(
        self,
        event_bus,
        learning,
    ):

        self.learning = learning

        event_bus.subscribe(
            "provider_execution.completed",
            self.handle,
        )

        event_bus.subscribe(
            "provider_execution.failed",
            self.handle,
        )


    def handle(
        self,
        event,
    ):

        payload = dict(
            event.payload
        )

        payload[
            "type"
        ] = "provider_execution"

        return self.learning.process_execution(
            payload
        )
