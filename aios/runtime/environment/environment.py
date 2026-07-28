import os


class RuntimeEnvironment:

    def __init__(self):
        self._values = dict(os.environ)

    def get(self, key: str, default=None):
        return self._values.get(key, default)

    def set(self, key: str, value):
        self._values[key] = str(value)
        return value

    def remove(self, key: str):
        return self._values.pop(key, None)

    def export(self):
        return dict(self._values)

    def reload(self):
        self._values = dict(os.environ)

    def __contains__(self, key):
        return key in self._values

    def __len__(self):
        return len(self._values)
