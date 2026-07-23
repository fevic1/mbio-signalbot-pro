from .feedback import ExecutionFeedback


class ExecutionEvaluator:

    def evaluate(
        self,
        execution,
    ):

        return ExecutionFeedback(
            execution_id=execution.id,
            success=execution.status == "completed",
            score=1.0 if execution.status == "completed" else 0.0,
        )
