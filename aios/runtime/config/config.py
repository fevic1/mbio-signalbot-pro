class RuntimeConfig:

    def __init__(self):
        self._values: dict[str, object] = {}

    def set(self, key: str, value):
        self._values[key] = value
        return value

    def get(self, key: str, default=None):
        return self._values.get(key, default)

    def update(self, values: dict):
        self._values.update(values)

    def export(self):
        return dict(self._values)

    def clear(self):
        self._values.clear()

    def __contains__(self, key):
        return key in self._values

    def __len__(self):
        return len(self._values)
