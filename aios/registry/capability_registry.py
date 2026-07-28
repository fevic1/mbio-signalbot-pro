from aios.core.registry import Registry


class CapabilityRegistry(Registry):

    def register(self, capability):
        capability.validate()
        return super().register(capability.name, capability)

    def list(self):
        return list(super().all())

    def exists(self, name):
        return name in self
