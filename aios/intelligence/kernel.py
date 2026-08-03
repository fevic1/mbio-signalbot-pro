class IntelligenceKernel:

    def run(self, context):

        return {
            "intent": context.get("task_plan"),
            "skills": context.get("skill_route"),
            "execution_policy": context.get("execution_policy"),
            "workflow": context.get("workflow"),
            "tool_results": context.get("tool_results"),
            "tool_evidence": context.get("tool_evidence"),
            "reasoning": context.get("reasoning"),
            "decision": context.get("decision"),
            "verification": context.get("verification"),
            "reflection": context.get("reflection"),
            "memory": context.get("memory_snapshot"),
            "metrics": context.get("metrics"),
            "optimizer": context.get("optimizer"),
        }
