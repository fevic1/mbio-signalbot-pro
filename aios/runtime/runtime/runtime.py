from aios.runtime.application import Application


class Runtime:

    def __init__(self, application: Application | None = None):
        self._application = application or Application()

    @property
    def application(self):
        return self._application

    @property
    def kernel(self):
        return self._application.kernel

    @property
    def started(self):
        return self._application.started

    def start(self):
        return self._application.start()

    def stop(self):
        return self._application.stop()

    def restart(self):
        return self._application.restart()

    def service(self, name):
        kernel = self.kernel
        if kernel is None:
            raise RuntimeError("Runtime has not been started.")
        return kernel.get(name)

    def services(self):
        kernel = self.kernel
        return {} if kernel is None else kernel.services()
