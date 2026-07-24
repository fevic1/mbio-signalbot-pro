from aios.memory import (
    MemoryRecord,
    MemoryType,
)


class ExecutionMemoryWriter:


    TYPE_MAP = {

        "decision":
            MemoryType.DECISION,

        "knowledge":
            MemoryType.KNOWLEDGE,

        "operational":
            MemoryType.OPERATIONAL,

    }



    def __init__(
        self,
        router,
    ):

        self.router = router



    def write(
        self,
        memories,
    ):

        stored = []


        for item in memories:

            memory_type = (
                self.TYPE_MAP[
                    item["type"]
                ]
            )


            record = MemoryRecord(
                content=item["content"],
                memory_type=memory_type,
            )


            stored.append(
                self.router.store(
                    record
                )
            )


        return stored
