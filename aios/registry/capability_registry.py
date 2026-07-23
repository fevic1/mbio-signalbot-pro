class CapabilityRegistry:

    def __init__(self):
        self._capabilities = {}


    def register(
        self,
        capability,
    ):

        capability.validate()

        self._capabilities[
            capability.name
        ] = capability
            capability.name
        ] = capability


    def get(
        self,
        name,
    ):

        return self._capabilities.get(
            name
        )


    def list(
        self,
    ):

        return list(
            self._capabilities.values()
        )


    def exists(
        self,
        name,
    ):

        return name in self._capabilities
