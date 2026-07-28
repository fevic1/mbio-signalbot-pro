class RuntimeFeatureFlagManager:

    def __init__(self):
        self._flags = {}

    def enable(self, name: str):
        self._flags[name] = True
        return True

    def disable(self, name: str):
        self._flags[name] = False
        return False

    def enabled(self, name: str):
        return self._flags.get(
            name,
            False,
        )

    def toggle(self, name: str):
        value = not self.enabled(name)
        self._flags[name] = value
        return value

    def names(self):
        return tuple(
            sorted(self._flags)
        )

    def active(self):
        return tuple(
            name
            for name, enabled in self._flags.items()
            if enabled
        )

    def export(self):
        return dict(self._flags)

    def clear(self):
        self._flags.clear()

    def __contains__(self, name):
        return name in self._flags

    def __len__(self):
        return len(self._flags)
