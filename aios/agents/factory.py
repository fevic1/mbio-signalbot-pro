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

        response = self.executor.execute(
            self.capability
        )

        result = {
            "capability": self.capability,
            "provider": response.provider,
            "model": response.model,
            "content": response.content,
        }

        if blackboard:

            blackboard.store(
                self.capability,
                result,
            )

        return result



class AgentFactory:

    def create(
        self,
        capabilities,
    ):

        workers = []

        for capability in capabilities:

            workers.append(
                CapabilityWorker(
                    capability
                )
            )

        return workers
