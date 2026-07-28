class RuntimePluginRegistry:

    def __init__(self):
        self._plugins: dict[str, object] = {}

    def register(self, name: str, plugin):
        self._plugins[name] = plugin

    def unregister(self, name: str):
        self._plugins.pop(name, None)

    def get(self, name: str, default=None):
        return self._plugins.get(name, default)

    def names(self):
        return tuple(sorted(self._plugins))

    def export(self):
        return {
            name: type(plugin).__name__
            for name, plugin in self._plugins.items()
        }

    def __contains__(self, name):
        return name in self._plugins

    def __len__(self):
        return len(self._plugins)
