class LLMRouter:


    def __init__(
        self,
        model_registry
    ):

        self.registry = model_registry
        self.history = []


    def candidates(
        self,
        capability,
        allowed_models=None,
    ):

        models = (
            self.registry
            .find_by_capability(
                capability
            )
        )

        if allowed_models:

            models = [
                model
                for model in models
                if model.name in allowed_models
            ]

        return models


    def select_model(
        self,
        capability,
        allowed_models=None,
    ):

        models = (
            self.registry
            .find_by_capability(
                capability
            )
        )

        if allowed_models:

            models = [
                model
                for model in models
                if model.name in allowed_models
            ]


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
