import os


class RuntimeEnvironmentManager:

    def __init__(self):
        self._values = {}

    def set(self, name: str, value: str):
        self._values[name] = value

    def get(self, name: str, default=None):
        return self._values.get(
            name,
            os.getenv(name, default),
        )

    def remove(self, name: str):
        self._values.pop(name, None)

    def exists(self, name: str):
        return (
            name in self._values
            or name in os.environ
        )

    def names(self):
        return tuple(
            sorted(
                set(self._values)
                | set(os.environ)
            )
        )

    def export(self):
        return {
            name: "***"
            for name in self._values
        }

    def clear(self):
        self._values.clear()

    def __contains__(self, name):
        return self.exists(name)

    def __len__(self):
        return len(self._values)
