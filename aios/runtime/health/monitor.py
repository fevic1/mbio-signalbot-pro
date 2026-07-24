from .models import RuntimeHealth


class RuntimeHealthMonitor:


    def __init__(
        self,
        worker,
        event_publisher=None,
    ):

        self.worker = worker

        self.event_publisher = (
            event_publisher
        )



    def check(self):

        status = (
            self.worker.status()
            if self.worker
            else {
                "running": False,
                "thread_alive": False,
            }
        )


        healthy = (
            status["running"]
            and status["thread_alive"]
        )


        health = RuntimeHealth(
            status=(
                "ok"
                if healthy
                else "warning"
            ),
            details=status,
        )


        if self.event_publisher:

            self.event_publisher.checked(
                health.describe()
            )


        return health
