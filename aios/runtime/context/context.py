class RuntimeContext:

    def __init__(self):
        self._values: dict[str, object] = {}

    def set(self, key: str, value):
        self._values[key] = value
        return value

    def get(self, key: str, default=None):
        return self._values.get(key, default)

    def remove(self, key: str):
        return self._values.pop(key, None)

    def update(self, values: dict):
        self._values.update(values)

    def clear(self):
        self._values.clear()

    def keys(self):
        return tuple(sorted(self._values))

    def values(self):
        return tuple(self._values.values())

    def items(self):
        return tuple(self._values.items())

    def __contains__(self, key):
        return key in self._values

    def __len__(self):
        return len(self._values)
