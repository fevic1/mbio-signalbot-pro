from ..models import MemoryImportance


class RetentionManager:


    def should_keep(
        self,
        memory,
    ):

        if (
            memory.importance
            ==
            MemoryImportance.CRITICAL
        ):

            return True


        if (
            memory.memory_type.value
            ==
            "decision"
        ):

            return True


        return (
            memory.metadata.access_count
            > 0
        )
