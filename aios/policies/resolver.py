class PolicyResolver:


    def __init__(
        self,
        registry,
    ):

        self.registry = registry



    def resolve(
        self,
        name,
    ):

        history = self.registry.history(
            name
        )


        if not history:

            return None


        return history[-1]
