class RuntimeIntrospection:

    def __init__(self, kernel):
        self._kernel = kernel

    def snapshot(self):
        return {
            "state": self._kernel.state.value,
            "version": self._kernel.version.string,
            "metadata": self._kernel.metadata.export(),
            "status": self._kernel.status.export(),
            "services": sorted(self._kernel.services()),
            "registry_categories": self._kernel.registry.categories(),
            "context_keys": self._kernel.context.keys(),
            "config": self._kernel.config.export(),
            "environment_size": len(self._kernel.environment),
        }

    def service(self, name):
        return self._kernel.get(name)

    def exists(self, name):
        return name in self._kernel.services()
