#!/usr/bin/env python3

from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / file
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kernel = load("kernel", "kernel.py")
plugin_manager = load("plugin_manager", "plugin_manager.py")


class AIOS:

    def __init__(self):
        self.services = kernel.services
        self.lifecycle = kernel.lifecycle
        self.runtime = kernel.runtime
        self.registry = kernel.registry
        self.health_manager = kernel.health
        self.resources = kernel.resources
        self.metrics = kernel.metrics
        self.manifest = kernel.manifest

    def boot(self):

        self.runtime.set_state("starting")
        self.metrics.inc("application.boot")

        pm = plugin_manager.PluginManager()
        pm.discover()
        self.plugin_manager = pm

        for plugin in pm.plugins.values():

            instance = plugin.get("instance")

            if instance:
                self.lifecycle.register(
                    instance.NAME,
                    instance
                )

        self.health_manager.register(
            "runtime",
            self.runtime.health
        )

        self.health_manager.register(
            "registry",
            self.registry.health
        )

        self.health_manager.register(
            "resources",
            self.resources.stats
        )

        self.registry.register("kernel", self)

        for plugin in self.plugin_manager.plugins.values():
            if "instance" in plugin:
                self.registry.register(
                    plugin["instance"].NAME,
                    plugin["instance"]
                )

        self.metrics.gauge(
            "services",
            len(self.services.list())
        )

        self.metrics.gauge(
            "plugins",
            len(self.plugin_manager.plugins)
        )

        self.runtime.set_state("running")
        return self

    def health(self):

        return {
            "services": self.services.list(),
            "plugins": self.plugin_manager.plugins,
            "runtime": self.runtime.health(),
            "health": self.health_manager.run(),
        }

    def shutdown(self):
        self.runtime.set_state("stopping")
        self.lifecycle.shutdown()
        self.runtime.set_state("stopped")


if __name__ == "__main__":

    app = AIOS().boot()

    print()
    print("AIOS Boot Complete")
    print()

    health = app.health()

    print()
    print("Runtime")
    print(f"  {health['runtime']['state']}")
    print("-" * 40)


    print("Services")

    for service in health["services"]:
        print(" ", service)

    print()
    print("Plugins")

    for name, plugin in health["plugins"].items():
        if "instance" in plugin:
            h = plugin["instance"].health()
            print(f"  {name}: {h['status']} {h['version']}")

    print("-" * 40)
