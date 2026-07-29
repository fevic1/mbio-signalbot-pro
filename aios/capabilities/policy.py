
from aios.capabilities.errors import CapabilityExecutionError


class CapabilityPolicyEngine:


    def __init__(
        self,
        provider_pool=None,
    ):
        self.provider_pool = provider_pool


    def validate(
        self,
        capability,
    ):

        if not capability.enabled:
            raise CapabilityExecutionError(
                f"Capability disabled: {capability.name}"
            )


        metadata = capability.metadata or {}


        if metadata.get(
            "requires_provider",
            False,
        ):

            if self.provider_pool is None:
                raise CapabilityExecutionError(
                    "Provider pool unavailable"
                )


            if self.provider_pool.best() is None:
                raise CapabilityExecutionError(
                    f"{capability.name}: no usable provider"
                )


        if metadata.get(
            "risk_level"
        ) == "critical":

            if not metadata.get(
                "requires_approval",
                False,
            ):
                raise CapabilityExecutionError(
                    f"{capability.name}: critical capability requires approval"
                )


        return True
