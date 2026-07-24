from aios.memory import (
    MemoryType,
)

from aios.memory.intelligence import (
    MemoryQuery,
)



class AgentMemory:


    def __init__(
        self,
        intelligence,
        scope,
    ):

        self.intelligence = intelligence

        self.scope = scope



    def recall(
        self,
        agent_role,
        question,
        limit=5,
    ):

        layers = self.scope.layers_for(
            agent_role
        )


        query = MemoryQuery(
            text=question,
            layers=layers,
            limit=limit,
        )


        result = self.intelligence.query(
            query
        )


        return result



    def remember(
        self,
        memory,
    ):

        return self.intelligence.router.store(
            memory
        )
