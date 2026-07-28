from aios.core.registry import Registry


class MemoryLayerRegistry(Registry):

    def register(self, layer):
        return super().register(layer.name, layer)

    def remove(self, name):
        return self.unregister(name)

    def layers(self):
        return list(self.all())
