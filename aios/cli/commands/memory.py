def memory(container):

    router = container.get(
        "memory_router"
    )

    return {
        "memory_available":
            router is not None,
    }
