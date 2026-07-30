from .execution_memory import ExecutionMemory
from .feedback import FeedbackAnalyzer

from aios.memory.models import (
    MemoryRecord,
    MemoryType,
    MemoryImportance,
    MemoryMetadata,
)


class LearningCoordinator:


    def __init__(
        self,
        memory_manager=None,
    ):

        self.memory_manager = memory_manager

        self.memory = (
            memory_manager
            if memory_manager is not None
            else ExecutionMemory()
        )

        self.feedback = FeedbackAnalyzer()



    def process_execution(
        self,
        result,
    ):

        analysis = self.feedback.analyze(
            result
        )


        if self.memory_manager is not None:

            memory = MemoryRecord(
                content={
                    "result": result,
                    "analysis": analysis,
                },
                memory_type=MemoryType.FEEDBACK,
                importance=MemoryImportance.NORMAL,
                metadata=MemoryMetadata(
                    source="learning",
                    tags=[
                        "execution",
                        "model_feedback",
                    ],
                    confidence=result.get(
                        "confidence",
                        1.0,
                    ),
                ),
            )

            return self.memory.store(
                memory
            )


        return self.memory.store(
            {
                "result": result,
                "analysis": analysis,
            }
        )
