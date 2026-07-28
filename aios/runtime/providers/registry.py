class RuntimeProviderRegistry:

    def __init__(self):
        self._providers: dict[str, object] = {}

    def register(self, name: str, provider):
        self._providers[name] = provider

    def unregister(self, name: str):
        self._providers.pop(name, None)

    def get(self, name: str, default=None):
        return self._providers.get(name, default)

    def names(self):
        return tuple(sorted(self._providers))

    def export(self):
        return {
            name: type(provider).__name__
            for name, provider in self._providers.items()
        }

    def __contains__(self, name):
        return name in self._providers

    def __len__(self):
        return len(self._providers)
