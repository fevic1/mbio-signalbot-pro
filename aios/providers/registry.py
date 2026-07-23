from .groq import GroqProvider
from .cerebras import CerebrasProvider
from .openrouter import OpenRouterProvider
from .anthropic import AnthropicProvider


class ProviderRegistry:

    def __init__(self):
        self._factories = {
            "groq": GroqProvider,
            "cerebras": CerebrasProvider,
            "openrouter": OpenRouterProvider,
            "anthropic": AnthropicProvider,
        }

        self.providers = None

    def _ensure_loaded(self):
        if self.providers is None:
            self.providers = {
                name: factory()
                for name, factory in self._factories.items()
            }

    def all(self):
        self._ensure_loaded()
        return self.providers

    def available(self):
        self._ensure_loaded()

        return {
            name: provider
            for name, provider in self.providers.items()
            if provider.available()
        }

    def get(self, name):
        self._ensure_loaded()
        return self.providers.get(name)


registry = ProviderRegistry()
