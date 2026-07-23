from .manager import provider_manager
from .scoring import score


class ProviderPool:

    def ranked(self):
        providers = list(provider_manager.available().values())
        providers.sort(key=score, reverse=True)
        return providers

    def best(self):
        ranked = self.ranked()
        return ranked[0] if ranked else None

    def backup(self):
        ranked = self.ranked()
        return ranked[1:] if len(ranked) > 1 else []

    def next(self, current):
        for provider in self.backup():
            if provider.name != current:
                return provider
        return None


provider_pool = ProviderPool()
