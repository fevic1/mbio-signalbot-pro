class RuntimeResources:

    def __init__(self):
        self._resources: dict[str, object] = {}

    def register(self, name: str, resource):
        self._resources[name] = resource

    def unregister(self, name: str):
        self._resources.pop(name, None)

    def get(self, name: str, default=None):
        return self._resources.get(name, default)

    def names(self):
        return tuple(sorted(self._resources))

    def export(self):
        return {
            name: type(resource).__name__
            for name, resource in self._resources.items()
        }

    def __contains__(self, name):
        return name in self._resources

    def __len__(self):
        return len(self._resources)
