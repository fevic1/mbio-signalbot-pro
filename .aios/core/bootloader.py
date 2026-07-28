#!/usr/bin/env python3

from pathlib import Path
import importlib.util
import time


ROOT = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / filename
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kernel = load("kernel", "kernel.py")
plugin_manager = load("plugin_manager", "plugin_manager.py")


class BootLoader:

    def __init__(self):
        self.services = kernel.services
        self.runtime = kernel.runtime
        self.logger = kernel.logger
        self.metrics = kernel.metrics
        self.registry = kernel.registry
        self.health = kernel.health
        self.event_store = kernel.event_store

    def boot(self):

        start = time.perf_counter()

        self.runtime.set_state("starting")

        self.event_store.append("kernel.boot.start")

        pm = plugin_manager.PluginManager()
        pm.discover()

        self.registry.register("plugin_manager", pm)

        self.metrics.gauge(
            "plugins",
            len(pm.plugins)
        )

        self.metrics.gauge(
            "services",
            len(self.services.list())
        )

        elapsed = time.perf_counter() - start

        self.metrics.timing(
            "boot",
            elapsed
        )

        self.event_store.append(
            "kernel.boot.complete",
            {
                "seconds": elapsed
            }
        )

        self.runtime.set_state("running")

        self.logger.info(
            f"Kernel booted in {elapsed:.3f}s",
            plugin="kernel"
        )

        return pm


bootloader = BootLoader()


if __name__ == "__main__":

    pm = bootloader.boot()

    print()
    print("Boot Summary")
    print("-" * 40)
    print("Runtime :", bootloader.runtime.state)
    print("Services:", len(bootloader.services.list()))
    print("Plugins :", len(pm.plugins))
    print("Metrics :", bootloader.metrics.snapshot())
    print("Events  :", bootloader.event_store.count())
