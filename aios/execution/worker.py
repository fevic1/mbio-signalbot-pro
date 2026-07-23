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


    def execute(
        self,
        task,
        context,
    ):

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


            self.queue.finish(
                task
            )


            context.emit(
                "capability_completed",
                {
                    "capability": capability,
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "latency": result.get("latency"),
                },
            )


            return result


        except Exception as exc:


            task.status = "failed"

            task.error = str(exc)


            self.queue.fail(
                task
            )


            context.emit(
                "capability_failed",
                {
                    "capability": capability,
                    "error": str(exc),
                },
            )


            raise
