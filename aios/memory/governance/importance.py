from ..models import MemoryImportance


class ImportanceManager:


    def evaluate(
        self,
        memory,
    ):

        access = (
            memory.metadata.access_count
        )


        if access >= 100:

            memory.importance = (
                MemoryImportance.CRITICAL
            )


        elif access >= 25:

            memory.importance = (
                MemoryImportance.HIGH
            )


        elif access >= 5:

            memory.importance = (
                MemoryImportance.NORMAL
            )


        return memory
