from .feedback import ExecutionFeedback


class ExecutionEvaluator:

    def evaluate(
        self,
        execution,
    ):

        return ExecutionFeedback(
            execution_id=execution.id,
            success=execution.success,
            score=1.0 if execution.success else 0.0,
        )
