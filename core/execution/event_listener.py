from core.execution.event_store import execution_event_store


EXECUTION_EVENTS = {
    "ORDER_SUBMITTED",
    "ORDER_FILLED",
}


def register_execution_listener(event_bus):

    for event_name in EXECUTION_EVENTS:

        event_bus.subscribe(
            event_name,
            lambda payload, name=event_name:
                execution_event_store.record(
                    name,
                    payload
                )
        )
