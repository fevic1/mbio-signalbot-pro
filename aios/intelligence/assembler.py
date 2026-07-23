class ContextAssembler:

    def assemble(
        self,
        capability,
        request,
    ):

        execution = getattr(
            request,
            "context",
            None,
        )

        metadata = {}
        results = {}
        events = []

        if execution is not None:

            metadata = dict(
                getattr(
                    execution,
                    "metadata",
                    {},
                )
            )

            results = dict(
                getattr(
                    execution,
                    "results",
                    {},
                )
            )

            events = list(
                getattr(
                    execution,
                    "events",
                    [],
                )
            )

        blackboard = metadata.get(
            "blackboard",
            {},
        )

        memory = metadata.get(
            "memory",
            {},
        )

        architecture = metadata.get(
            "architecture",
            {},
        )

        project = metadata.get(
            "project",
            {},
        )

        return {
            "capability": capability,
            "permission": request.permission,
            "retry_limit": request.retry_limit,
            "project": project,
            "architecture": architecture,
            "memory": memory,
            "blackboard": blackboard,
            "previous_results": results,
            "events": events,
            "metadata": metadata,
        }
