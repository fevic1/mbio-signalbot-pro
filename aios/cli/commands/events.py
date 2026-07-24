def events(container):

    bus = container.get(
        "event_bus"
    )

    return {
        "event_bus_available":
            bus is not None,
    }
