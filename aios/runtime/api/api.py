class RuntimeAPI:

    def __init__(self, kernel):
        self._kernel = kernel

    def service(self, name: str):
        return self._kernel.get(name)

    def services(self):
        return self._kernel.services()

    def status(self):
        return self._kernel.status.export()

    def metadata(self):
        return self._kernel.metadata.export()

    def info(self):
        return self._kernel.info.export()

    def platform(self):
        return self._kernel.platform.export()

    def capabilities(self):
        return self._kernel.capabilities.export()

    def features(self):
        return self._kernel.features.export()

    def profile(self):
        return self._kernel.profile.export()

    def identity(self):
        return self._kernel.identity.export()

    def resources(self):
        return self._kernel.resources.export()

    def diagnostics(self):
        return self._kernel.diagnostics.report()

    def snapshot(self):
        return self._kernel.introspection.snapshot()

    def registry(self):
        return self._kernel.registry

    def context(self):
        return self._kernel.context

    def config(self):
        return self._kernel.config
