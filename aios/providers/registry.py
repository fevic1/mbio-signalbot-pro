import os

from .qwen import QwenProvider
from .groq import GroqProvider
from .cerebras import CerebrasProvider
from .openrouter import OpenRouterProvider
from .anthropic import AnthropicProvider
from .deepseek import DeepSeekProvider


class ProviderRegistry:

    def __init__(self):
        factories = {
            "qwen": QwenProvider,
            "deepseek": DeepSeekProvider,
            "groq": GroqProvider,
            "cerebras": CerebrasProvider,
            "openrouter": OpenRouterProvider,
            "anthropic": AnthropicProvider,
        }

        configured = os.getenv(
            "AIOS_PROVIDER_ORDER",
            "qwen,deepseek,groq,cerebras,openrouter",
        )

        order = [
            name.strip().lower()
            for name in configured.split(",")
            if name.strip().lower() in factories
        ]

        self._factories = {
            name: factories[name]
            for name in order
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
