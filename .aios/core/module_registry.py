#!/usr/bin/env python3

from collections import OrderedDict


class ModuleRegistry:

    def __init__(self):
        self._modules = OrderedDict()

    def register(self, name, module):
        if name in self._modules:
            raise ValueError(f"Module '{name}' already registered")
        self._modules[name] = module

    def unregister(self, name):
        self._modules.pop(name, None)

    def get(self, name):
        return self._modules[name]

    def exists(self, name):
        return name in self._modules

    def list(self):
        return list(self._modules.keys())

    def health(self):
        result = {}

        for name, module in self._modules.items():
            if hasattr(module, "health"):
                result[name] = module.health()
            else:
                result[name] = {
                    "status": "loaded"
                }

        return result


registry = ModuleRegistry()


if __name__ == "__main__":

    class Demo:

        def health(self):
            return {
                "status": "healthy"
            }

    registry.register("demo", Demo())

    print(registry.list())
    print(registry.health())
