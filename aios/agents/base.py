from abc import ABC, abstractmethod
from datetime import datetime


class BaseAgent(ABC):

    def __init__(
        self,
        name,
        role,
        memory=None,
    ):

        self.name = name
        self.role = role
        self.memory = memory


    def observe(
        self,
        input_data,
    ):

        return input_data


    @abstractmethod
    def analyze(
        self,
        input_data,
    ):

        pass


    def execute(
        self,
        context,
    ):

        return self.analyze(
            context
        )


    def remember(
        self,
        title,
        content,
        metadata=None,
    ):

        if self.memory:

            return self.memory.remember(
                "agent",
                title,
                content,
                metadata,
            )

        return None


    def report(
        self,
        result,
    ):

        return {
            "agent": self.name,
            "role": self.role,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
        }


    def health(self):

        return {
            "agent": self.name,
            "status": "healthy",
        }
