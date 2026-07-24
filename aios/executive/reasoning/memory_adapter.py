class ExecutiveMemoryAdapter:


    def __init__(
        self,
        memory_context,
    ):

        self.memory_context = memory_context



    def build_context(
        self,
        objective,
    ):

        context = self.memory_context.build()


        return {
            "objective": objective,

            "memory": context,

            "instructions": [
                "Use previous decisions when relevant",
                "Consider previous failures",
                "Avoid repeating known mistakes",
                "Prefer verified patterns",
            ],
        }
