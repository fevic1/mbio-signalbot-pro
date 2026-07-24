from ..base import MemoryLayer
from ...models import (
    MemoryRecord,
    MemoryType,
)


class ProjectMemory(MemoryLayer):


    def save(
        self,
        data,
    ):

        memory = MemoryRecord(
            content=data,
            memory_type=MemoryType.PROJECT,
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
            == MemoryType.PROJECT
            and query.lower()
            in str(item.content).lower()
        ]
