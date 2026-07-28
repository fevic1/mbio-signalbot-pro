class RuntimeDriverRegistry:

    def __init__(self):
        self._drivers: dict[str, object] = {}

    def register(self, name: str, driver):
        self._drivers[name] = driver

    def unregister(self, name: str):
        self._drivers.pop(name, None)

    def get(self, name: str, default=None):
        return self._drivers.get(name, default)

    def names(self):
        return tuple(sorted(self._drivers))

    def export(self):
        return {
            name: type(driver).__name__
            for name, driver in self._drivers.items()
        }

    def __contains__(self, name):
        return name in self._drivers

    def __len__(self):
        return len(self._drivers)
