from aios.capabilities.models import Capability


class CapabilityBootstrap:


    def __init__(
        self,
        registry,
    ):

        self.registry = registry


    def load(self):

        capabilities = [

            Capability(
                name="research",
                permission="research",
            ),

            Capability(
                name="reasoning",
                permission="research",
            ),

            Capability(
                name="verification",
                permission="verification",
            ),

            Capability(
                name="risk_analysis",
                permission="research",
            ),

            Capability(
                name="coding",
                permission="engineering",
            ),

            Capability(
                name="testing",
                permission="engineering",
            ),

        ]


        for capability in capabilities:

            self.registry.register(
                capability
            )


        return self.registry.list()
