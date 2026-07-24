from ..base import MemoryLayer
from ...models import (
    MemoryRecord,
    MemoryType,
)


class IdentityMemory(MemoryLayer):


    def save(
        self,
        data,
    ):

        memory = MemoryRecord(
            content=data,
            memory_type=MemoryType.KNOWLEDGE,
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
            if query.lower()
            in str(item.content).lower()
        ]
