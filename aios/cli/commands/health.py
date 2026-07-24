def health(container):

    runtime = container.get(
        "runtime_daemon"
    )

    return {
        "runtime_available":
            runtime is not None,

        "status":
            "ok" if runtime else "warning",
    }
