from abc import ABC, abstractmethod


class BaseProvider(ABC):

    name = ""

    @abstractmethod
    def chat(self, request):
        ...

    @abstractmethod
    def health(self):
        ...
