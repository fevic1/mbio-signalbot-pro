class RuntimeSettingsManager:

    def __init__(self):
        self._settings = {}

    def set(self, name: str, value):
        self._settings[name] = value
        return value

    def get(self, name: str, default=None):
        return self._settings.get(
            name,
            default,
        )

    def remove(self, name: str):
        return self._settings.pop(
            name,
            None,
        )

    def exists(self, name: str):
        return name in self._settings

    def names(self):
        return tuple(
            sorted(self._settings)
        )

    def export(self):
        return dict(self._settings)

    def update(self, values: dict):
        self._settings.update(values)

    def clear(self):
        self._settings.clear()

    def __contains__(self, name):
        return self.exists(name)

    def __len__(self):
        return len(self._settings)
