class RuntimeFeatures:

    def __init__(self):
        self._features: dict[str, bool] = {}

    def enable(self, name: str):
        self._features[name] = True

    def disable(self, name: str):
        self._features[name] = False

    def enabled(self, name: str):
        return self._features.get(name, False)

    def toggle(self, name: str):
        self._features[name] = not self.enabled(name)
        return self._features[name]

    def list(self):
        return tuple(
            sorted(
                name
                for name, enabled in self._features.items()
                if enabled
            )
        )

    def export(self):
        return dict(self._features)

    def clear(self):
        self._features.clear()

    def __contains__(self, name):
        return self.enabled(name)

    def __len__(self):
        return len(self._features)
