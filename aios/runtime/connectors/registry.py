class RuntimeConnectorRegistry:

    def __init__(self):
        self._connectors: dict[str, object] = {}

    def register(self, name: str, connector):
        self._connectors[name] = connector

    def unregister(self, name: str):
        self._connectors.pop(name, None)

    def get(self, name: str, default=None):
        return self._connectors.get(name, default)

    def names(self):
        return tuple(sorted(self._connectors))

    def export(self):
        return {
            name: type(connector).__name__
            for name, connector in self._connectors.items()
        }

    def __contains__(self, name):
        return name in self._connectors

    def __len__(self):
        return len(self._connectors)
