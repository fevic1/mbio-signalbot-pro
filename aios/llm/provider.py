from abc import ABC, abstractmethod


class LLMProvider(ABC):


    def __init__(
        self,
        name
    ):
        self.name = name


    @abstractmethod
    def generate(
        self,
        prompt
    ):
        pass


    def health(self):

        return {
            "provider": self.name,
            "status": "unknown"
        }
