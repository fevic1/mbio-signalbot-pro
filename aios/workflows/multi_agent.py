class MultiAgentWorkflow:

    def __init__(
        self,
        system,
    ):
        self.system = system

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
