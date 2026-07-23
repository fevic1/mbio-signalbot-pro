class CapabilityRegistry:

    def __init__(self):
        self._capabilities = {}


    def register(self, capability):

        self._capabilities[
            capability.name
        ] = capability


    def get(self, name):

        return self._capabilities.get(name)


    def list(self):

        return list(
            self._capabilities.values()
        )
