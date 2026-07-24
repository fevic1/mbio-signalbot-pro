from ..base import MemoryLayer
from ...models import (
    MemoryRecord,
    MemoryType,
)


class DecisionMemory(MemoryLayer):


    def save(
        self,
        data,
    ):

        memory = MemoryRecord(
            content=data,
            memory_type=MemoryType.DECISION,
        )

        return self.repository.save(
            memory
        )



    def search(
        self,
        query,
    ):

        return [
            item
            for item in self.repository.all()
            if item.memory_type
            == MemoryType.DECISION
        ]
