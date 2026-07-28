from aios.core.execution.runner import ExecutionRunner

from aios.core.execution import ExecutionEngine

from aios.execution import ExecutionExecutor


class WorkflowEngine(ExecutionRunner):

    def __init__(
        self,
        system,
    ):

        self.system = system

        self.executor = ExecutionExecutor(
            system,
            system.execution_planner,
        )


    async def execute(
        self,
        task,
    ):

        context = await self.executor.execute(
            task
        )

        return context
