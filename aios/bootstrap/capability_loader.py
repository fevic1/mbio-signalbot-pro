from aios.registry import CapabilityRegistry
from aios.capabilities.models import Capability


class CapabilityBootstrap:


    def __init__(
        self,
        registry,
    ):

        self.registry = registry


    def load_capabilities(
        self,
    ):

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
                name="market_analysis",
                permission="research",
            ),

            Capability(
                name="execution_approval",
                permission="trading",
            ),

        ]


        for capability in capabilities:

            self.registry.register(
                capability
            )


        return self.registry.list()
