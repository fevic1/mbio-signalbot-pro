from datetime import datetime, timezone


class ExecutionDecisionMemoryHandler:

    def __init__(
        self,
        event_bus,
        memory_manager,
    ):

        self.memory_manager = memory_manager

        event_bus.subscribe(
            "execution.completed",
            self.handle,
        )


    def handle(
        self,
        event,
    ):

        payload = event.payload

        result = payload.get(
            "result",
            {},
        )

        if not result:
            return None

        memory = {
            "type": "execution_decision",
            "capability": result.get("capability"),
            "provider": result.get("provider"),
            "model": result.get("model"),
            "selected_model": result.get("selected_model"),
            "latency": result.get("latency"),
            "attempt": result.get("attempt"),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        return self.memory_manager.store(
            memory
        )
