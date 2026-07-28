class ServiceContainer:

    def __init__(self):
        self._services = {}

    def register(self, name, service):
        self._services[name] = service
        return service

    def unregister(self, name):
        return self._services.pop(name, None)

    def get(self, name):
        return self._services[name]

    def has(self, name):
        return name in self._services

    def resolve(self, name):
        return self.get(name)

    def services(self):
        return dict(self._services)

    def __call__(self):
        return dict(self._services)

    def clear(self):
        self._services.clear()

    def __contains__(self, name):
        return name in self._services

    def __len__(self):
        return len(self._services)
