from datetime import datetime


class Worker:
    """
    Executes exactly one task.
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

    def execute(self, task):

        started = datetime.utcnow()

        try:

            result = task.agent.run(
                task=task,
                context=task.context,
                blackboard=self.blackboard,
            )

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
