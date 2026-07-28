#!/usr/bin/env python3

from collections import OrderedDict


class LifecycleManager:

    def __init__(self):
        self.components = OrderedDict()

    def register(self, name, component):
        self.components[name] = component

    def startup(self):
        for name, component in self.components.items():
            if hasattr(component, "on_load"):
                component.on_load()

    def shutdown(self):
        for name, component in reversed(self.components.items()):
            if hasattr(component, "on_unload"):
                component.on_unload()

    def health(self):
        result = {}

        for name, component in self.components.items():
            if hasattr(component, "health"):
                result[name] = component.health()
            else:
                result[name] = {"status": "unknown"}

        return result


lifecycle = LifecycleManager()


if __name__ == "__main__":

    class Demo:

        def on_load(self):
            print("loaded")

        def on_unload(self):
            print("unloaded")

        def health(self):
            return {"status": "healthy"}

    lifecycle.register("demo", Demo())

    lifecycle.startup()
    print(lifecycle.health())
    lifecycle.shutdown()
