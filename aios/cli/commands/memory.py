def memory(
    container,
):

    router = container.get(
        "memory_router"
    )

    if router is None:

        return {
            "status":
            "unavailable"
        }


    result = {
        "status":
        "available"
    }


    if hasattr(
        router,
        "describe",
    ):

        result["details"] = (
            router.describe()
        )


    return result
