class RuntimeAdapterRegistry:

    def __init__(self):
        self._adapters: dict[str, object] = {}

    def register(self, name: str, adapter):
        self._adapters[name] = adapter

    def unregister(self, name: str):
        self._adapters.pop(name, None)

    def get(self, name: str, default=None):
        return self._adapters.get(name, default)

    def names(self):
        return tuple(sorted(self._adapters))

    def export(self):
        return {
            name: type(adapter).__name__
            for name, adapter in self._adapters.items()
        }

    def __contains__(self, name):
        return name in self._adapters

    def __len__(self):
        return len(self._adapters)
