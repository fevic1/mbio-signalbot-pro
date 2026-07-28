class RuntimeFeatureRegistry:

    def __init__(self):
        self._features = {}

    def register(self, name: str, feature):
        self._features[name] = feature
        return feature

    def unregister(self, name: str):
        return self._features.pop(
            name,
            None,
        )

    def get(self, name: str, default=None):
        return self._features.get(
            name,
            default,
        )

    def enabled(self, name: str):
        feature = self._features.get(name)

        if feature is None:
            return False

        status = getattr(
            feature,
            "enabled",
            True,
        )

        return bool(status)

    def names(self):
        return tuple(
            sorted(self._features)
        )

    def active(self):
        return tuple(
            name
            for name in self._features
            if self.enabled(name)
        )

    def export(self):
        return {
            name: self.enabled(name)
            for name in self._features
        }

    def clear(self):
        self._features.clear()

    def __contains__(self, name):
        return name in self._features

    def __len__(self):
        return len(self._features)
