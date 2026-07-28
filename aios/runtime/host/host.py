from aios.runtime.application import Application


class RuntimeHost:

    def __init__(self, application: Application | None = None):
        self._application = application or Application()

    @property
    def application(self):
        return self._application

    @property
    def kernel(self):
        return self._application.kernel

    def start(self):
        return self._application.start()

    def stop(self):
        return self._application.stop()

    def restart(self):
        return self._application.restart()

    def service(self, name: str):
        kernel = self.kernel
        if kernel is None:
            raise RuntimeError("Runtime has not been started.")
        return kernel.get(name)

    def register_extension(self, extension):
        kernel = self.kernel
        if kernel is None:
            raise RuntimeError("Runtime has not been started.")
        kernel.extensions.register(extension)
        return extension

    def register_plugin(self, plugin):
        kernel = self.kernel
        if kernel is None:
            raise RuntimeError("Runtime has not been started.")
        kernel.plugins.register(plugin)
        return plugin

    def register_tool(self, tool):
        kernel = self.kernel
        if kernel is None:
            raise RuntimeError("Runtime has not been started.")
        return kernel.tool_registry.register(tool)

    def services(self):
        kernel = self.kernel
        return {} if kernel is None else kernel.services()
