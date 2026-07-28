class RuntimePackageRegistry:

    def __init__(self):
        self._packages: dict[str, object] = {}

    def register(self, name: str, package):
        self._packages[name] = package

    def unregister(self, name: str):
        self._packages.pop(name, None)

    def get(self, name: str, default=None):
        return self._packages.get(name, default)

    def names(self):
        return tuple(sorted(self._packages))

    def export(self):
        return {
            name: type(package).__name__
            for name, package in self._packages.items()
        }

    def __contains__(self, name):
        return name in self._packages

    def __len__(self):
        return len(self._packages)
