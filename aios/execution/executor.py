from .context import ExecutionContext


class ExecutionExecutor:

    def __init__(
        self,
        system,
        planner,
    ):

        self.system = system
        self.planner = planner


    def execute(
        self,
        task,
    ):

        pipeline = self.planner.get_pipeline(
            task["category"]
        )


        context = ExecutionContext(
            task,
            event_bus=self.system.event_bus,
        )


        context.start()


        try:

            for agent_name in pipeline:

                record = self.system.registry.get(
                    agent_name
                )


                if record is None:

                    raise ValueError(
                        f"Unknown agent: {agent_name}"
                    )


                agent = record["agent"]


                output = agent.execute(
                    context
                )


                context.add_result(
                    agent_name,
                    output,
                )


            context.complete()


            if self.system.decision_workflow:

                decision = self.system.decision_workflow.run(
                    task,
                    context,
                )


                context.set_metadata(
                    "decision",
                    decision,
                )


        except Exception as error:

            context.fail(
                error
            )

            raise


        return context
