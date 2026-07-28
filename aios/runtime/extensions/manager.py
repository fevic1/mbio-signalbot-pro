from .extension import RuntimeExtension


class ExtensionManager:

    def __init__(self):
        self._extensions: dict[str, RuntimeExtension] = {}

    def register(self, name_or_extension, extension=None):
        if extension is not None:
            self._extensions[name_or_extension] = extension
            return extension

        self._extensions[name_or_extension.name] = name_or_extension
        return name_or_extension

    def unregister(self, name: str):
        return self._extensions.pop(name, None)

    def initialize(self, kernel):
        for extension in self._extensions.values():
            if extension.enabled:
                extension.initialize(kernel)

    def shutdown(self, kernel):
        for extension in reversed(tuple(self._extensions.values())):
            if extension.enabled:
                extension.shutdown(kernel)

    def get(self, name: str):
        return self._extensions[name]

    def list(self):
        return tuple(self._extensions.values())

    def __contains__(self, name):
        return name in self._extensions

    def __len__(self):
        return len(self._extensions)
