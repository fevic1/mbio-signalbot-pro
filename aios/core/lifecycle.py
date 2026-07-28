class Lifecycle:

    def initialize(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def shutdown(self):
        pass

    def restart(self):
        self.stop()
        self.start()
