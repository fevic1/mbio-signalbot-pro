class AgentCoordinator:


    def __init__(
        self,
        registry,
    ):

        self.registry = registry



    def assign(
        self,
        agent_name,
        task,
    ):

        agent = self.registry.get(
            agent_name
        )


        if not agent:

            raise ValueError(
                "Agent unavailable"
            )


        return {
            "agent": agent_name,
            "task": task,
            "status": "assigned",
        }

