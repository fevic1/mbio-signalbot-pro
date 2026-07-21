class LLMRouter:


    def __init__(
        self,
        model_registry
    ):

        self.registry = model_registry
        self.history = []


    def select_model(
        self,
        capability
    ):

        models = (
            self.registry
            .find_by_capability(
                capability
            )
        )


        if not models:

            return None


        selected = models[0]


        self.history.append(
            {
                "capability": capability,
                "model": selected.name,
                "provider":
                    selected.provider
            }
        )


        return selected


    def history_log(
        self
    ):

        return self.history
