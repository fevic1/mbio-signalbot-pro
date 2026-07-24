from aios.workforce import (
    AgentTask,
    AgentExecutor,
)

from .events import ExecutionEventPublisher



class MissionExecutor:


    def __init__(
        self,
        event_bus=None,
    ):

        self.executor = AgentExecutor()

        self.events = ExecutionEventPublisher(
            event_bus
        )



    def execute(
        self,
        assignments,
    ):

        results = []


        for assignment in assignments:

            agent = assignment["agent"]

            task = AgentTask(
                objective=assignment["milestone"],
                task=assignment["task"],
                permissions={},
            )


            self.events.publish_started(
                agent,
                task.task,
            )


            try:

                result = self.executor.execute(
                    agent,
                    task,
                )


                self.events.publish_completed(
                    agent,
                    task.task,
                    result.describe(),
                )


                results.append(
                    result.describe()
                )


            except Exception as exc:

                self.events.publish_failed(
                    agent,
                    task.task,
                    exc,
                )


        return results
