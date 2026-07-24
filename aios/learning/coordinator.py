from .execution_memory import ExecutionMemory
from .feedback import FeedbackAnalyzer


class LearningCoordinator:


    def __init__(self):

        self.memory = ExecutionMemory()

        self.feedback = FeedbackAnalyzer()



    def process_execution(
        self,
        result,
    ):

        analysis = self.feedback.analyze(
            result
        )


        record = self.memory.store(
            {
                "result": result,
                "analysis": analysis,
            }
        )


        return record
