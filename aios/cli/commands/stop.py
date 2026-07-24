def stop(
    runtime,
):

    if runtime:

        runtime.shutdown()

        return {
            "status":
            "stopped"
        }


    return {
        "status":
        "not_running"
    }
