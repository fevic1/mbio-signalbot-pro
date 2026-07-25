from aios.memory.models import MemoryType


class FeedbackRetriever:


    def __init__(
        self,
        memory_router,
    ):

        self.memory_router = memory_router



    def retrieve(
        self,
        limit=10,
    ):

        records = self.memory_router.retrieve(
            MemoryType.FEEDBACK
        )


        return records[-limit:]
