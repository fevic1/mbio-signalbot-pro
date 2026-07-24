from datetime import datetime, timezone


class MemoryDecay:


    def apply(
        self,
        memory,
    ):

        if (
            memory.metadata.access_count
            == 0
        ):

            memory.metadata.confidence = max(
                0.1,
                memory.metadata.confidence
                -
                0.05
            )


        return memory
