from ..base import MemoryLayer


class ExecutionMemory(MemoryLayer):


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
