def status(
    runtime=None,
):

    if not runtime:

        return {
            "status": "unavailable"
        }


    result = {
        "status": "running",
    }


    if hasattr(
        runtime,
        "worker",
    ) and runtime.worker:

        result["worker"] = (
            runtime.worker.status()
        )


    return result
