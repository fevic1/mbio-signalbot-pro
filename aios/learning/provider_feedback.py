class ProviderFeedbackHandler:


    def __init__(
        self,
        event_bus,
        learning,
        model_intelligence=None,
    ):

        self.learning = learning
        self.model_intelligence = model_intelligence

        event_bus.subscribe(
            "provider_execution.completed",
            self.handle,
        )

        event_bus.subscribe(
            "provider_execution.failed",
            self.handle,
        )

        event_bus.subscribe(
            "model_execution.completed",
            self.handle_model,
        )

        event_bus.subscribe(
            "model_execution.failed",
            self.handle_model,
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


    def handle_model(
        self,
        event,
    ):

        payload = dict(
            event.payload
        )

        model = payload.get(
            "model"
        )

        if self.model_intelligence and model:

            self.model_intelligence.register(
                model,
                {
                    "provider": payload.get(
                        "provider"
                    ),
                    "quality":
                        "high"
                        if payload.get(
                            "success",
                            False,
                        )
                        else "low",
                    "score":
                        10
                        if payload.get(
                            "success",
                            False,
                        )
                        else -10,
                },
            )

        payload[
            "type"
        ] = "model_execution"

        return self.learning.process_execution(
            payload
        )
