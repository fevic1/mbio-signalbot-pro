class ContextAssembler:

    def assemble(
        self,
        system,
        capability,
        request,
    ):
        execution = getattr(
            request,
            "context",
            None,
        )

        if isinstance(execution, dict):
            metadata = dict(execution)
            results = dict(
                execution.get(
                    "results",
                    {},
                )
            )
        else:
            metadata = dict(
                getattr(
                    execution,
                    "metadata",
                    {},
                )
            ) if execution else {}

            results = dict(
                getattr(
                    execution,
                    "results",
                    {},
                )
            ) if execution else {}

        return {
            "capability": capability,
            "permission": request.permission,
            "retry_limit": request.retry_limit,
            "execution": execution,
            "results": results,
            "metadata": metadata,
            "memory": getattr(system, "memory", None),
            "project_manager": getattr(system, "project_manager", None),
            "event_bus": getattr(system, "event_bus", None),
            "decision_policy": getattr(system, "decision_policy", None),
            "skill_registry": getattr(system, "skill_registry", None),
            "capability_registry": getattr(system, "capability_registry", None),
        }
