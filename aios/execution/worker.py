from datetime import datetime


class Worker:

    def __init__(
        self,
        system,
        blackboard,
        queue,
    ):
        self.system = system
        self.blackboard = blackboard
        self.queue = queue
        self.context = None

    def bind(
        self,
        context,
    ):
        self.context = context

    def execute(
        self,
        task,
    ):

        if self.context is None:
            raise RuntimeError(
                "Worker is not bound to an execution context."
            )

        context = self.context

        started = datetime.utcnow()

        capability = task.worker.capability.name

        context.emit(
            "capability_started",
            {
                "capability": capability,
                "task": task.id,
            },
        )

        try:

            result = task.worker.run(
                context=context,
                blackboard=self.blackboard,
            )

            task.result = result
            task.started = started.isoformat()
            task.completed = datetime.utcnow().isoformat()
            task.status = "completed"

            self.queue.finish(task)

            context.emit(
                "capability_completed",
                {
                    "capability": capability,
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "latency": result.get("latency"),
                },
            )

            if self.system.capability_health:

                self.system.capability_health.record_success(
                    capability,
                    latency=result.get("latency", 0),
                    cost=result.get("cost", 0),
                )

            return result

        except Exception as exc:

            task.status = "failed"
            task.error = str(exc)

            self.queue.fail(task)

            context.emit(
                "capability_failed",
                {
                    "capability": capability,
                    "error": str(exc),
                },
            )

            if self.system.capability_health:

                self.system.capability_health.record_failure(
                    capability
                )

            raise
