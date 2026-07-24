from aios.learning.memory_writer import (
    MemoryClassifier,
    ExecutionMemoryWriter,
)


class MemoryEventSubscriber:


    def __init__(
        self,
        memory_router,
    ):

        self.classifier = MemoryClassifier()

        self.writer = ExecutionMemoryWriter(
            memory_router
        )



    def handle(
        self,
        event,
    ):

        result = (
            event.payload
            .get(
                "result",
                {}
            )
        )


        memories = (
            self.classifier.classify(
                result
            )
        )


        stored = (
            self.writer.write(
                memories
            )
        )


        return stored
