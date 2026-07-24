from ..base import MemoryLayer


class OperationalMemory(MemoryLayer):


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

        return self.repository.all()
