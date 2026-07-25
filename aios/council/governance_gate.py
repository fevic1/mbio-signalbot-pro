from abc import ABC, abstractmethod


class GovernanceGate(ABC):


    name = "base"


    @abstractmethod
    def check(
        self,
        context,
    ):
        pass
