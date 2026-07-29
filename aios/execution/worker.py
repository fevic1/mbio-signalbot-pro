from aios.core.execution import ExecutionEngine

from datetime import datetime, timezone


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

    async def execute(
        self,
        task,
    ):

        if self.context is None:
            raise RuntimeError(
                "Worker is not bound to an execution context."
            )

        context = self.context

        started = datetime.now(timezone.utc)

        capability_definition = task.worker.capability

        capability = capability_definition.name

        context.emit(
            "capability_started",
            {
                "capability": capability,
                "permission": capability_definition.permission,
                "risk_level": (
                    capability_definition.metadata.get(
                        "risk_level"
                    )
                ),
                "requires_provider": (
                    capability_definition.metadata.get(
                        "requires_provider",
                        False,
                    )
                ),
                "memory_write": (
                    capability_definition.metadata.get(
                        "memory_write",
                        False,
                    )
                ),
                "task": task.id,
            },
        )

        try:

            result = await task.worker.run(
                context=context,
                blackboard=self.blackboard,
            )

            task.result = result

            context.add_result(
                capability,
                result,
            )

            task.started = started.isoformat()
            task.completed = datetime.now(timezone.utc).isoformat()
            task.status = "completed"

            self.queue.finish(task)

            context.emit(
                "capability_completed",
                {
                    "capability": capability,
                    "permission": capability_definition.permission,
                    "risk_level": (
                        capability_definition.metadata.get(
                            "risk_level"
                        )
                    ),
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "latency": result.get("latency"),
                    "success": True,
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
                    "permission": capability_definition.permission,
                    "risk_level": (
                        capability_definition.metadata.get(
                            "risk_level"
                        )
                    ),
                    "retry_limit": (
                        capability_definition.retry_limit
                    ),
                    "error": str(exc),
                },
            )

            if self.system.capability_health:

                self.system.capability_health.record_failure(
                    capability
                )

            raise
