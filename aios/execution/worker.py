from datetime import datetime
from time import perf_counter



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


    def execute(
        self,
        task,
    ):

        started = datetime.utcnow()

        try:

            result = task.worker.run(
                context=None,
                blackboard=self.blackboard,
            )

            latency = perf_counter() - start

            result["latency"] = latency


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
