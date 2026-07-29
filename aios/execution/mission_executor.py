from aios.core.execution.runner import ExecutionRunner

from aios.core.execution import ExecutionEngine

from aios.workforce import (
    AgentTask,
    AgentExecutor,
)

from .events import ExecutionEventPublisher



class MissionExecutor(ExecutionRunner):


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
        governance=None,
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

                if governance:
                    result.metadata = getattr(
                        result,
                        "metadata",
                        {}
                    )

                    result.metadata["governance"] = governance


                if governance:
                    result.metadata["governance"] = governance

                result_data = result.describe()

                self.events.publish_completed(
                    agent,
                    task.task,
                    result_data,
                )


                results.append(
                    result_data
                )


            except Exception as exc:

                self.events.publish_failed(
                    agent,
                    task.task,
                    exc,
                )


        return results
