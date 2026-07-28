class RuntimeModules:

    def __init__(self):
        self._modules: dict[str, object] = {}

    def register(self, name: str, module):
        self._modules[name] = module

    def unregister(self, name: str):
        self._modules.pop(name, None)

    def get(self, name: str, default=None):
        return self._modules.get(name, default)

    def names(self):
        return tuple(sorted(self._modules))

    def export(self):
        return {
            name: type(module).__name__
            for name, module in self._modules.items()
        }

    def __contains__(self, name):
        return name in self._modules

    def __len__(self):
        return len(self._modules)
