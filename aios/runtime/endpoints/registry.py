class RuntimeEndpointRegistry:

    def __init__(self):
        self._endpoints: dict[str, object] = {}

    def register(self, name: str, endpoint):
        self._endpoints[name] = endpoint

    def unregister(self, name: str):
        self._endpoints.pop(name, None)

    def get(self, name: str, default=None):
        return self._endpoints.get(name, default)

    def names(self):
        return tuple(sorted(self._endpoints))

    def export(self):
        return {
            name: type(endpoint).__name__
            for name, endpoint in self._endpoints.items()
        }

    def __contains__(self, name):
        return name in self._endpoints

    def __len__(self):
        return len(self._endpoints)
