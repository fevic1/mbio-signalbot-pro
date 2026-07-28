from aios.runtime.bootstrap import Bootstrap


class Application:

    def __init__(self):
        self.bootstrap = Bootstrap()
        self.kernel = None
        self._started = False

    @property
    def started(self):
        return self._started

    def start(self):
        if self._started:
            return self.kernel

        self.kernel = self.bootstrap.initialize()
        self._started = True
        return self.kernel

    def stop(self):
        if not self._started:
            return

        self.bootstrap.shutdown()
        self._started = False
        self.kernel = None

    def restart(self):
        self.stop()
        return self.start()

    def services(self):
        if self.kernel is None:
            return {}
        return self.kernel.services()
