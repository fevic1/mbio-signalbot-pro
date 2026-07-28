class RuntimeCapabilities:

    def __init__(self):
        self._capabilities: dict[str, bool] = {}

    def enable(self, name: str):
        self._capabilities[name] = True

    def disable(self, name: str):
        self._capabilities[name] = False

    def supported(self, name: str):
        return self._capabilities.get(name, False)

    def list(self):
        return tuple(
            sorted(
                name
                for name, enabled in self._capabilities.items()
                if enabled
            )
        )

    def export(self):
        return dict(self._capabilities)

    def __contains__(self, name):
        return self.supported(name)

    def __len__(self):
        return len(self._capabilities)
