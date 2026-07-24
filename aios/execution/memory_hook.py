class ExecutionMemoryHook:


    def __init__(
        self,
        agent_memory,
    ):

        self.agent_memory = agent_memory



    def prepare(
        self,
        agent,
        task,
    ):

        role = (
            agent.role
            if hasattr(agent, "role")
            else str(agent)
        )


        question = (
            f"Previous experience for "
            f"task: {task}"
        )


        return self.agent_memory.recall(
            role,
            question,
        )
