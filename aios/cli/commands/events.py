def events(
    container,
):

    bus = container.get(
        "event_bus"
    )

    if bus is None:

        return {
            "status":
            "unavailable"
        }


    result = {
        "status":
        "available"
    }


    if hasattr(
        bus,
        "describe",
    ):

        result["details"] = (
            bus.describe()
        )


    return result
