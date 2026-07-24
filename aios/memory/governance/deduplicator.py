class MemoryDeduplicator:


    def find_duplicate(
        self,
        memory,
        existing_records,
    ):

        for record in existing_records:

            if (
                record.memory_type
                ==
                memory.memory_type
                and
                record.content
                ==
                memory.content
            ):

                return record


        return None



    def merge(
        self,
        existing,
        incoming,
    ):

        existing.metadata.access_count += 1

        existing.metadata.confidence = min(
            1.0,
            existing.metadata.confidence
            +
            0.05
        )

        return existing
