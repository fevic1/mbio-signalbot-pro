from datetime import datetime
from time import perf_counter

from aios.capabilities.executor import CapabilityExecutor


class Worker:
    """
    Executes one capability task.
    """

    def __init__(
        self,
        system,
        blackboard,
        queue,
    ):
        self.system = system
        self.blackboard = blackboard
        self.queue = queue
        self.capability_executor = CapabilityExecutor()


    def execute(
        self,
        task,
    ):

        started = datetime.utcnow()

        try:

            response = self.capability_executor.execute(
                task.capability
            )

            latency = perf_counter() - start


            result = {
                "capability": task.capability,
                "provider": response.provider,
                "model": response.model,
                "content": response.content,
                "latency": latency,
            }


            self.blackboard.store(
                task.id,
                result,
            )


            task.result = result
            task.started = started.isoformat()
            task.completed = datetime.utcnow().isoformat()
            task.status = "completed"


            self.queue.finish(task)


            return result


        except Exception as exc:

            task.status = "failed"
            task.error = str(exc)

            self.queue.fail(task)

            raise
