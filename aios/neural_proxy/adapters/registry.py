class AdapterRegistry:


    def __init__(self):

        self.adapters = {}


    def register(
        self,
        provider,
        adapter,
    ):

        self.adapters[provider] = adapter


    def get(
        self,
        provider,
    ):

        return self.adapters.get(
            provider
        )


adapter_registry = AdapterRegistry()
