def check_kernel(kernel):
    return {
        "state": str(kernel.state),
        "services": len(kernel.services),
    }


def check_supervisor(kernel):
    return {
        "supervised": len(kernel.supervisor),
        "healthy": len(kernel.supervisor.healthy()),
        "failed": len(kernel.supervisor.failed()),
    }


def check_lifecycle(kernel):
    return {
        "events": len(kernel.lifecycle.history()),
        "latest": (
            kernel.lifecycle.latest().phase.value
            if kernel.lifecycle.latest()
            else None
        ),
    }


def check_events(kernel):
    return {
        "event_bus": type(kernel.event_bus).__name__,
    }
