from abc import ABC


class MemoryLayer(ABC):

    def initialize(self):
        pass

    def load(self):
        pass

    def save(self):
        pass

    def clear(self):
        pass

    def search(self, *args, **kwargs):
        return []

    def health(self):
        return {"status": "healthy"}
