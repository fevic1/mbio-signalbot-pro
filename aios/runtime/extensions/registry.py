class RuntimeExtensionRegistry:

    def __init__(self):
        self._extensions: dict[str, object] = {}

    def register(self, name: str, extension):
        self._extensions[name] = extension

    def unregister(self, name: str):
        self._extensions.pop(name, None)

    def get(self, name: str, default=None):
        return self._extensions.get(name, default)

    def names(self):
        return tuple(sorted(self._extensions))

    def export(self):
        return {
            name: type(extension).__name__
            for name, extension in self._extensions.items()
        }

    def __contains__(self, name):
        return name in self._extensions

    def __len__(self):
        return len(self._extensions)
