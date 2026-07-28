class RuntimeFacade:

    def __init__(self, kernel):
        self._kernel = kernel

    def start(self):
        return self._kernel

    def stop(self):
        return self._kernel

    def service(self, name: str):
        return self._kernel.get(name)

    def services(self):
        return self._kernel.services()

    def status(self):
        return self._kernel.status.export()

    def diagnostics(self):
        return self._kernel.diagnostics.report()

    def snapshot(self):
        return self._kernel.introspection.snapshot()
