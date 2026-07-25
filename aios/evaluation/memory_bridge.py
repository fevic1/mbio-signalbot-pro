from aios.memory.models import (
    MemoryRecord,
    MemoryType,
    MemoryImportance,
    MemoryMetadata,
)


class EvaluationMemoryBridge:


    def __init__(
        self,
        memory_router,
    ):

        self.memory_router = memory_router



    def store(
        self,
        outcome,
        evaluation,
    ):

        record = MemoryRecord(

            content={

                "change_id":
                    outcome.get(
                        "change_id"
                    ),

                "outcome":
                    outcome,

                "evaluation":
                    evaluation,

            },

            memory_type=MemoryType.FEEDBACK,

            importance=(
                MemoryImportance.HIGH
                if evaluation.get(
                    "improved",
                    False,
                )
                else MemoryImportance.NORMAL
            ),

            metadata=MemoryMetadata(

                source="aios_evaluation",

                tags=[
                    "evaluation",
                    "evolution",
                    "feedback",
                ],

                confidence=1.0,

            ),

        )


        return self.memory_router.store(
            record
        )
