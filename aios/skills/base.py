from abc import ABC, abstractmethod


class Skill(ABC):
    id: str
    name: str

    @abstractmethod
    def execute(self, context):
        raise NotImplementedError
