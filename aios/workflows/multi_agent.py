from aios.core.execution import ExecutionEngine

class MultiAgentWorkflow:

    def __init__(
        self,
        system,
    ):
        self.system = system


    def execute_sync(
        self,
        *args,
        **kwargs,
    ):
        import asyncio

        return asyncio.run(
            self.execute(
                *args,
                **kwargs
            )
        )

    async def execute(
        self,
        task,
        agents=None,
    ):

        if self.system.workflow_engine is None:
            raise RuntimeError(
                "WorkflowEngine not initialized"
            )

        context = await self.system.workflow_engine.execute(
            task
        )

        return context.snapshot()
