class Resource:

    def initialize(self):
        pass

    def acquire(self):
        pass

    def release(self):
        pass

    def shutdown(self):
        pass

    def health(self):
        return {"status": "healthy"}
