from aios.capabilities.executor import CapabilityExecutor


class CapabilityWorker:


    def __init__(
        self,
        capability,
    ):

        self.capability = capability
        self.executor = CapabilityExecutor()


    def run(
        self,
        context=None,
        blackboard=None,
    ):

        result = self.executor.execute(
            self.capability.name
        )

        output = {
            "capability": self.capability.name,
            "permission": self.capability.permission,
            "result": result,
        }


        if blackboard:

            blackboard.store(
                self.capability.name,
                output,
            )


        return output



class AgentFactory:


    def __init__(
        self,
        capability_registry,
    ):

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
                    capability
                )
            )


        return workers
