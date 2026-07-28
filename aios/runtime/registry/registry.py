class RuntimeRegistryStore:

    def __init__(self):
        self._registries: dict[str, object] = {}

    def register(self, name: str, registry):
        self._registries[name] = registry

    def unregister(self, name: str):
        self._registries.pop(name, None)

    def get(self, name: str, default=None):
        return self._registries.get(name, default)

    def names(self):
        return tuple(sorted(self._registries))

    def export(self):
        return {
            name: type(registry).__name__
            for name, registry in self._registries.items()
        }

    def __contains__(self, name):
        return name in self._registries

    def __len__(self):
        return len(self._registries)
