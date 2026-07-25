from abc import ABC, abstractmethod


class StorageBackend(ABC):


    @abstractmethod
    def append(
        self,
        category,
        data,
    ):
        pass



    @abstractmethod
    def read(
        self,
        category,
    ):
        pass
