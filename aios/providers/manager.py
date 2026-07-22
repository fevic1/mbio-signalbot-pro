from .retry import retry
from .registry import registry
from .router import chat


class ProviderManager:
    """
    Central interface for every AIOS component.
    """

    def __init__(self):
        self.registry = registry

    def providers(self):
        return self.registry.all()

    def provider(self, name):
        return self.registry.get(name)

    def chat(self, request, preferred="groq"):
        return retry(
            lambda: chat(request, preferred),
            retries=3,
            delay=1,
        )

    def health(self):
        return {
            name: provider.health()
            for name, provider in self.registry.all().items()
        }


provider_manager = ProviderManager()
