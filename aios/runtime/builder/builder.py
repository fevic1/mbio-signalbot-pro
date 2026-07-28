from aios.runtime.application import Application


class ApplicationBuilder:

    def __init__(self):
        self._application = Application()

    def application(self):
        return self._application

    def start(self):
        self._application.start()
        return self

    def stop(self):
        self._application.stop()
        return self

    def restart(self):
        self._application.restart()
        return self

    def kernel(self):
        return self._application.kernel

    def service(self, name):
        kernel = self.kernel()
        if kernel is None:
            raise RuntimeError("Application has not been started.")
        return kernel.get(name)

    def build(self):
        return self._application
