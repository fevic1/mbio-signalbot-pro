from ..base import MemoryLayer


class KnowledgeMemory(MemoryLayer):


    def save(
        self,
        data,
    ):

        return self.repository.save(
            data
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
