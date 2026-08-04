from .execution_plan import ExecutionPlan


class ContextCompiler:

    def compile(
        self,
        capability,
        messages,
        *,
        token_budget,
        provider_hints,
        evidence,
        metadata=None,
    ):

        return ExecutionPlan(
            capability=capability,
            messages=tuple(messages),
            token_budget=token_budget,
            provider_hints=provider_hints,
            evidence=evidence,
            metadata=metadata or {},
        )
