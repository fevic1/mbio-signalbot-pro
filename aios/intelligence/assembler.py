class ContextAssembler:

    def assemble(
        self,
        capability,
        request,
    ):

        context = getattr(
            request,
            "context",
            {},
        ) or {}

        metadata = {}

        if hasattr(context, "metadata"):
            metadata = dict(
                context.metadata
            )

        results = {}

        if hasattr(context, "results"):
            results = dict(
                context.results
            )

        events = []

        if hasattr(context, "events"):
            events = list(
                context.events
            )

        return {
            "capability": capability,
            "permission": request.permission,
            "attempt": request.retry_limit,
            "metadata": metadata,
            "results": results,
            "events": events,
            "context": context,
        }
