from aios.core.service import Service

from .versioning import StrategyVersionRegistry


class StrategyRegistry:

    def __init__(self):
        self.registry = StrategyVersionRegistry()

    def register(self, strategy):
        return self.registry.register(strategy)

    def get(self, name):
        return self.registry.get(name)

    def all(self):
        return list(self.registry.all())

    def metrics(self):
        return self.registry.metrics()
