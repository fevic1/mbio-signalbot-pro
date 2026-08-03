class ContextOptimizer:

    def optimize(self, context):

        keep = (
            "task_plan",
            "skill_route",
            "tool_results",
            "tool_evidence",
            "decision",
            "verification",
            "reflection",
            "workflow",
            "metrics",
            "memory_snapshot",
            "execution_policy",
        )

        return {
            k: context[k]
            for k in keep
            if k in context
        }
