from .models import (
    MemoryRecord,
    MemoryType,
)

from .stores import (
    ProjectMemoryStore,
    AgentMemoryStore,
    DecisionMemoryStore,
    KnowledgeMemoryStore,
    OperationalMemoryStore,
    FeedbackMemoryStore,
)


class MemoryRouter:


    def __init__(self):

        self.stores = {

            MemoryType.PROJECT:
                ProjectMemoryStore(),

            MemoryType.AGENT:
                AgentMemoryStore(),

            MemoryType.DECISION:
                DecisionMemoryStore(),

            MemoryType.KNOWLEDGE:
                KnowledgeMemoryStore(),

            MemoryType.OPERATIONAL:
                OperationalMemoryStore(),

            MemoryType.FEEDBACK:
                FeedbackMemoryStore(),
        }



    def store(
        self,
        memory: MemoryRecord,
    ):

        store = self.stores.get(
            memory.memory_type
        )


        if not store:

            raise ValueError(
                f"Unsupported memory type: {memory.memory_type}"
            )


        return store.save(
            memory
        )



    def retrieve(
        self,
        memory_type: MemoryType,
    ):

        store = self.stores.get(
            memory_type
        )


        if not store:

            raise ValueError(
                f"Unsupported memory type: {memory_type}"
            )


        return store.all()



    def search_tag(
        self,
        memory_type: MemoryType,
        tag: str,
    ):

        store = self.stores.get(
            memory_type
        )


        return store.search_tag(
            tag
        )



    def summary(
        self,
    ):

        return {
            memory_type.value:
                len(store.all())

            for memory_type, store
            in self.stores.items()
        }
