from aios.workflows.engine import (
    WorkflowEngine as CanonicalWorkflowEngine,
)


class WorkflowEngineAdapter:

    def __init__(self, system=None):
        self.system = system
        self.engine = CanonicalWorkflowEngine()
        self.workflows = {}

    def submit(self, workflow):

        return self.engine.submit(
            workflow
        )


    def ready(self):

        return self.engine.ready()


    def register(self, name, steps):

        self.workflows[name] = steps


    async def execute(
        self,
        task_or_name,
        context=None,
    ):

        if isinstance(task_or_name, str):

            context = context or {}

            for step in self.workflows[task_or_name]:
                context = step(context)

            return {
                "workflow": task_or_name,
                "result": context,
            }

        if self.system:

            from aios.execution import ExecutionExecutor

            executor = ExecutionExecutor(
                self.system,
                self.system.execution_planner,
            )

            return await executor.execute(
                task_or_name
            )

        return await self.engine.execute(
            task_or_name
        )


    def list(self):

        return tuple(
            self.workflows
        )
