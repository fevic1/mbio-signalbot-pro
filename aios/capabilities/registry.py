from .models import Capability


class CapabilityRegistry:


    def __init__(self):

        self._capabilities = {}


    def register(
        self,
        name,
        permission,
    ):

        capability = Capability(
            name=name,
            permission=permission,
        )

        self._capabilities[
            capability.name
        ] = capability


        return capability


    def get(
        self,
        name,
    ):

        return self._capabilities.get(
            name
        )


    def list_capabilities(self):

        return list(
            self._capabilities.values()
        )
