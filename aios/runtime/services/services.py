class RuntimeServices:

    def __init__(self):
        self._services: dict[str, object] = {}

    def register(self, name: str, service):
        self._services[name] = service

    def unregister(self, name: str):
        self._services.pop(name, None)

    def get(self, name: str, default=None):
        return self._services.get(name, default)

    def names(self):
        return tuple(sorted(self._services))

    def export(self):
        return {
            name: type(service).__name__
            for name, service in self._services.items()
        }

    def __contains__(self, name):
        return name in self._services

    def __len__(self):
        return len(self._services)
