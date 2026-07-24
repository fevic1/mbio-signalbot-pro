from .models import MemoryType

from .storage import (
    MemoryDatabase,
    MemoryRepository,
)


class PersistentMemoryRouter:


    def __init__(
        self,
        database_path="aios_memory.db",
    ):

        self.database = MemoryDatabase(
            database_path
        )

        self.repository = MemoryRepository(
            self.database
        )



    def store(
        self,
        memory,
    ):

        return self.repository.save(
            memory
        )



    def retrieve(
        self,
        memory_type: MemoryType,
    ):

        records = self.repository.all()

        return [
            record
            for record in records
            if record.memory_type == memory_type
        ]



    def summary(
        self,
    ):

        result = {
            memory_type.value: 0
            for memory_type in MemoryType
        }


        for record in self.repository.all():

            result[
                record.memory_type.value
            ] += 1


        return result
