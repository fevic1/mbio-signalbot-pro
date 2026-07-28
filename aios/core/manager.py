class Manager:

    def start(self):
        pass

    def stop(self):
        pass

    def reload(self):
        return self.stop() or self.start()

    def status(self):
        return {"status": "running"}
