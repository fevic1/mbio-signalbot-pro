class RuntimeConfigurationRegistry:

    def __init__(self):
        self._configurations: dict[str, object] = {}

    def register(self, name: str, configuration):
        self._configurations[name] = configuration

    def unregister(self, name: str):
        self._configurations.pop(name, None)

    def get(self, name: str, default=None):
        return self._configurations.get(name, default)

    def names(self):
        return tuple(sorted(self._configurations))

    def export(self):
        return {
            name: type(configuration).__name__
            for name, configuration in self._configurations.items()
        }

    def __contains__(self, name):
        return name in self._configurations

    def __len__(self):
        return len(self._configurations)
