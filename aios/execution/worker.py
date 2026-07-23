from datetime import datetime
from time import perf_counter

from aios.providers.router import chat
from aios.providers.types import ProviderRequest


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

            request = ProviderRequest(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are executing capability: "
                            f"{task.capability}"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Execute capability {task.capability} "
                            "and provide a structured result."
                        ),
                    },
                ]
            )


            start = perf_counter()
            response = chat(request)
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
