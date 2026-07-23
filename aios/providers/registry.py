from dotenv import load_dotenv

load_dotenv()

from .groq import GroqProvider
from .cerebras import CerebrasProvider
from .openrouter import OpenRouterProvider
from .anthropic import AnthropicProvider


class ProviderRegistry:
    """
    Central registry for all LLM providers.
    """

    def __init__(self):
        self.providers = {
            "groq": GroqProvider(),
            "cerebras": CerebrasProvider(),
            "openrouter": OpenRouterProvider(),
            "anthropic": AnthropicProvider(),
        }

    def all(self):
        """
        Return every provider.
        """
        return self.providers

    def available(self):
        """
        Return only available providers.
        """
        return {
            name: provider
            for name, provider in self.providers.items()
            if provider.available()
        }

    def get(self, name):
        """
        Return a provider by name.
        """
        return self.providers.get(name)


# Singleton registry used by the provider router
registry = ProviderRegistry()
