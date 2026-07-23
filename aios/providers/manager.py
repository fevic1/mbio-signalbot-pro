from .metrics import metrics
from .registry import registry
from .scoring import score


class ProviderManager:

    def providers(self):
        return registry.all()

    def provider(self, name):
        return registry.get(name)

    def health(self):
        return {
            name: provider.health()
            for name, provider in registry.all().items()
        }

    def available(self):
        return {
            name: provider
            for name, provider in registry.all().items()
            if provider.available()
        }

    def scores(self):
        return {
            name: score(provider)
            for name, provider in registry.all().items()
        }

    def best(self):
        available = self.available()

        if not available:
            return None

        return max(available.values(), key=score)

    def metrics(self):
        return metrics.providers


provider_manager = ProviderManager()
