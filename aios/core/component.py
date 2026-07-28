class Component:

    def start(self):
        pass

    def stop(self):
        pass

    def health(self):
        return {"status": "healthy"}

    def metadata(self):
        return {
            "type": self.__class__.__name__
        }
