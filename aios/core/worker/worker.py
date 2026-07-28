class Worker:

    def initialize(self):
        pass

    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def shutdown(self):
        pass

    def busy(self):
        return False

    def idle(self):
        return not self.busy()

    def health(self):
        return {"status": "healthy"}
