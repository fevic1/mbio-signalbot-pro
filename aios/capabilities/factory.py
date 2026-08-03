from aios.core.factory import Factory

from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest


class CapabilityWorker:

    def __init__(
        self,
        system,
        capability,
    ):
        self.capability = capability
        self.executor = CapabilityExecutor(system)

    async def run(
        self,
        context=None,
        blackboard=None,
    ):

        print("=" * 80)
        print("CapabilityWorker.run()")
        print("context type:", type(context))
        print("context repr:", repr(context))
        if hasattr(context, "__dict__"):
            print("context __dict__:", context.__dict__)
        if isinstance(context, dict):
            print("context dict:", context)
        print("=" * 80)

        
        if isinstance(context, dict):
            ctx = dict(context)
        
        elif hasattr(context, "task"):
            task = getattr(context, "task", {}) or {}
            meta = getattr(context, "metadata", {}) or {}

            ctx = dict(meta)

            query = (
                task.get("context", {}).get("resolved_query")
                or task.get("context", {}).get("message")
                or task.get("context", {}).get("query")
                or task.get("name")
                or ""
            )

            if query:
                ctx["message"] = query
                ctx["query"] = query
                ctx["resolved_query"] = query

        elif hasattr(context, "snapshot"):
            snap = context.snapshot()
            ctx = snap if isinstance(snap, dict) else {}
        else:
            ctx = {}

        query = (
            ctx.get("resolved_query")
            or ctx.get("message")
            or ctx.get("query")
            or ctx.get("name")
            or ""
        )

        if query:
            ctx.setdefault("message", query)
            ctx.setdefault("query", query)
            ctx.setdefault("resolved_query", query)

        request = CapabilityRequest(
            capability=self.capability.name,
            permission=self.capability.permission,
            context=ctx,
        )


        output = await self.executor.execute(
            request
        )

        output["permission"] = self.capability.permission

        if blackboard:

            blackboard.store(
                self.capability.name,
                output,
            )

        return output


class CapabilityFactory:

    def __init__(
        self,
        system,
        capability_registry,
    ):
        self.system = system
        self.registry = capability_registry

    def create(
        self,
        capabilities,
    ):

        workers = []

        for name in capabilities:

            capability = self.registry.get(
                name
            )

            if capability is None:
                continue

            workers.append(
                CapabilityWorker(
                    self.system,
                    capability
                )
            )

        return workers
