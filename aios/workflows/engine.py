from aios.execution import ExecutionExecutor


class WorkflowEngine:

    def __init__(
        self,
        system,
    ):

        self.system = system

        self.executor = ExecutionExecutor(
            system,
            system.execution_planner,
        )


    def execute(
        self,
        task,
    ):

        context = self.executor.execute(
            task
        )

        return context
