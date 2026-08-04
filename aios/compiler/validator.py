class CompilerValidator:

    def validate(
        self,
        original_messages,
        execution_plan,
    ) -> bool:

        return (
            len(original_messages)
            == len(execution_plan.context.messages)
        )
