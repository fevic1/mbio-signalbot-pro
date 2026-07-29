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


from .providers import (
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    LocalAdapter,
)


def register_default_adapters():

    adapter_registry.register(
        "openai",
        OpenAIAdapter(),
    )

    adapter_registry.register(
        "anthropic",
        AnthropicAdapter(),
    )

    adapter_registry.register(
        "gemini",
        GeminiAdapter(),
    )

    adapter_registry.register(
        "local",
        LocalAdapter(),
    )


register_default_adapters()
