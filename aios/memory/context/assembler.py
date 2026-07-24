from .priority import MemoryPriority
from .budget import ContextBudget



class MemoryContextAssembler:


    def __init__(
        self,
        registry,
        max_items=20,
    ):

        self.registry = registry

        self.priority = MemoryPriority()

        self.budget = ContextBudget(
            max_items
        )



    def collect(
        self,
        layers=None,
    ):

        memories = []


        if layers is None:

            layers = (
                self.registry.available()
            )


        for layer_name in layers:

            layer = self.registry.get(
                layer_name
            )


            memories.extend(
                layer.all()
            )


        return memories



    def build(
        self,
        layers=None,
    ):

        memories = self.collect(
            layers
        )


        ranked = self.priority.rank(
            memories
        )


        selected = self.budget.apply(
            ranked
        )


        return {
            "memory_count":
                len(selected),

            "memories":
                [
                    memory.describe()
                    for memory in selected
                ]
        }
