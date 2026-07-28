class Controller:

    def initialize(self):
        pass

    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def shutdown(self):
        pass

    def health(self):
        return {"status": "healthy"}
