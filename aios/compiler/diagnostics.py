from .execution_plan import ExecutionPlan


class CompilerDiagnostics:

    @staticmethod
    def report(plan: ExecutionPlan) -> dict:

        return {
            "capability": plan.capability,
            "messages": len(plan.messages),
            "estimated_prompt_tokens":
                plan.token_budget.estimated_prompt_tokens,
            "max_prompt_tokens":
                plan.token_budget.max_prompt_tokens,
            "max_completion_tokens":
                plan.token_budget.max_completion_tokens,
            "provider":
                plan.provider_hints.preferred_provider,
            "model":
                plan.provider_hints.preferred_model,
            "tool_count":
                len(plan.evidence.tools_called),
            "source_count":
                len(plan.evidence.sources),
            "metadata":
                dict(plan.metadata),
        }
