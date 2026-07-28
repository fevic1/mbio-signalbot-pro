from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):

    @abstractmethod
    def chat(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    def complete(self, *args, **kwargs):
        return self.chat(*args, **kwargs)

    def generate(self, *args, **kwargs):
        return self.chat(*args, **kwargs)

    def embed(self, *args, **kwargs):
        raise NotImplementedError

    def health(self):
        return {"status": "healthy"}
