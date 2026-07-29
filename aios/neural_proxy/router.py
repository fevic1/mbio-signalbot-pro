class NeuralProxyRouter:


    def __init__(
        self,
        llm_router=None,
        provider_router=None,
    ):

        self.llm_router = llm_router
        self.provider_router = provider_router


    def select(
        self,
        capability,
        allowed_models=None,
    ):

        if self.llm_router:

            return self.llm_router.select_model(
                capability,
                allowed_models=allowed_models,
            )

        return None
