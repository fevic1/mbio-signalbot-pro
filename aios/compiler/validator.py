from .execution_plan import ExecutionPlan


class CompilerValidationError(ValueError):
    pass


class ExecutionPlanValidator:

    def validate(self, plan: ExecutionPlan) -> ExecutionPlan:

        if not isinstance(plan, ExecutionPlan):
            raise CompilerValidationError(
                "Expected ExecutionPlan."
            )

        if not plan.capability:
            raise CompilerValidationError(
                "Capability missing."
            )

        if not plan.messages:
            raise CompilerValidationError(
                "No messages supplied."
            )

        for i, message in enumerate(plan.messages):

            if not isinstance(message, dict):
                raise CompilerValidationError(
                    f"Message {i} must be dict."
                )

            if "role" not in message:
                raise CompilerValidationError(
                    f"Message {i} missing role."
                )

            if "content" not in message:
                raise CompilerValidationError(
                    f"Message {i} missing content."
                )

        return plan
