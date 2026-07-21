class MultiAgentWorkflow:

    def __init__(
        self,
        system,
    ):

        self.system = system


    def execute(
        self,
        task,
    ):

        if self.system.workflow_engine is None:

            raise RuntimeError(
                "WorkflowEngine not initialized"
            )


        context = self.system.workflow_engine.execute(
            task
        )


        return context.snapshot()
