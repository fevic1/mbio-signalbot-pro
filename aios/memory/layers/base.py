from abc import ABC, abstractmethod


class MemoryLayer(ABC):


    def __init__(self, repository):

        self.repository = repository



    @abstractmethod
    def save(self, data):

        pass



    @abstractmethod
    def search(self, query):

        pass



    def all(self):

        return self.repository.all()
