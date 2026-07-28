class RuntimeDiscovery:

    def __init__(self, kernel):
        self._kernel = kernel

    def discover(self):
        return {
            "services": self._kernel.services.names()
            if hasattr(self._kernel.services, "names")
            else (),
            "plugins": self._kernel.plugins.list()
            if hasattr(self._kernel.plugins, "list")
            else (),
            "extensions": self._kernel.extensions.list()
            if hasattr(self._kernel.extensions, "list")
            else (),
            "providers": self._kernel.providers.names()
            if hasattr(self._kernel.providers, "names")
            else (),
            "drivers": self._kernel.drivers.names()
            if hasattr(self._kernel.drivers, "names")
            else (),
            "adapters": self._kernel.adapters.names()
            if hasattr(self._kernel.adapters, "names")
            else (),
            "connectors": self._kernel.connectors.names()
            if hasattr(self._kernel.connectors, "names")
            else (),
        }
