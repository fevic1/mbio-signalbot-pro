from aios.providers.pool import provider_pool


class NeuralProxyRouter:


    def __init__(
        self,
        llm_router=None,
        provider_router=None,
        intelligence=None,
    ):

        self.llm_router = llm_router
        self.provider_router = provider_router
        self.intelligence = intelligence


    def select(
        self,
        capability,
        allowed_models=None,
    ):

        candidates = []


        if self.llm_router:

            candidates = self.llm_router.candidates(
                capability,
                allowed_models=allowed_models,
            )


        if not candidates:
            return None


        if self.intelligence:

            candidates = self.intelligence.rank(
                candidates,
                {
                    "quality": True,
                },
            )


        candidates.sort(
            key=self._score,
            reverse=True,
        )

        return candidates[0]



    def select_model(
        self,
        capability,
        allowed_models=None,
    ):

        return self.select(
            capability,
            allowed_models=allowed_models,
        )


    def _score(
        self,
        model,
    ):

        score = 0


        provider = provider_pool.best()


        if provider:

            if provider.name == model.provider:
                score += 50


            if provider.available():
                score += 20


            if provider.health():
                score += 10


        return score
