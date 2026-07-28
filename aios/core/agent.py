class Agent:

    def initialize(self):
        pass

    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def shutdown(self):
        pass

    def capabilities(self):
        return []

    def metadata(self):
        return {
            "type": self.__class__.__name__,
        }
