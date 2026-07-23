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

        request = CapabilityRequest(
            capability=self.capability.name,
            permission=self.capability.permission,
            context=context,
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
