class Module:

    def initialize(self):
        pass

    def configure(self, **kwargs):
        return self

    def start(self):
        pass

    def stop(self):
        pass

    def shutdown(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__
