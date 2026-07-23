from aios.registry import CapabilityRegistry
from .capability_loader import CapabilityBootstrap


class BootstrapLoader:

    def __init__(self):
        self.registry = CapabilityRegistry()
        self.bootstrap = CapabilityBootstrap(
            registry=self.registry,
        )

    def load(self):
        self.bootstrap.load_capabilities()
        return self.registry


    def boot(self):
        self.load()

        from aios.system.bootstrap import SystemBootstrap

        return SystemBootstrap().boot()
