from .identity.store import IdentityMemory
from .project.store import ProjectMemory
from .decisions.store import DecisionMemory
from .facts.store import FactsMemory
from .knowledge.store import KnowledgeMemory
from .operational.store import OperationalMemory
from .execution.store import ExecutionMemory


class MemoryLayerRegistry:


    def __init__(
        self,
        repository,
    ):

        self.repository = repository

        self.layers = {}

        self._register_defaults()



    def register(
        self,
        name,
        layer,
    ):

        if name in self.layers:

            raise ValueError(
                f"Memory layer already registered: {name}"
            )


        self.layers[name] = layer



    def get(
        self,
        name,
    ):

        layer = self.layers.get(
            name
        )


        if not layer:

            raise KeyError(
                f"Unknown memory layer: {name}"
            )


        return layer



    def available(self):

        return list(
            self.layers.keys()
        )



    def _register_defaults(
        self,
    ):

        self.register(
            "identity",
            IdentityMemory(
                self.repository
            )
        )


        self.register(
            "project",
            ProjectMemory(
                self.repository
            )
        )


        self.register(
            "decision",
            DecisionMemory(
                self.repository
            )
        )


        self.register(
            "facts",
            FactsMemory(
                self.repository
            )
        )


        self.register(
            "knowledge",
            KnowledgeMemory(
                self.repository
            )
        )


        self.register(
            "operational",
            OperationalMemory(
                self.repository
            )
        )


        self.register(
            "execution",
            ExecutionMemory(
                self.repository
            )
        )
