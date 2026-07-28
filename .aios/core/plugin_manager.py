#!/usr/bin/env python3

from pathlib import Path
import importlib.util
from kernel import services

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"


class PluginManager:
    def __init__(self):
        self.plugins = {}

    def discover(self):
        for plugin in PLUGINS_DIR.iterdir():
            if not plugin.is_dir():
                continue

            bootstrap = plugin / "bootstrap.py"
            if not bootstrap.exists():
                continue

            spec = importlib.util.spec_from_file_location(
                plugin.name,
                bootstrap
            )

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.plugins[plugin.name] = {
                "registry": module.PLUGINS
            }

            plugin_file = plugin / "plugin.py"
            if plugin_file.exists():
                spec2 = importlib.util.spec_from_file_location(
                    f"{plugin.name}.plugin",
                    plugin_file
                )
                mod2 = importlib.util.module_from_spec(spec2)
                spec2.loader.exec_module(mod2)

                cls = None
                for obj in mod2.__dict__.values():
                    if (
                        isinstance(obj, type)
                        and obj.__module__ == mod2.__name__
                        and obj.__name__ != "BasePlugin"
                        and obj.__name__.endswith("Plugin")
                    ):
                        cls = obj
                        break

                if cls:
                    instance = cls()
                    instance.initialize(services)
                    instance.on_load()
                    self.plugins[plugin.name]["instance"] = instance

    def summary(self):
        for name, plugin in self.plugins.items():
            print(f"\n{name}")

            registry = plugin["registry"]

            for section, items in registry.items():
                print(f"  {section:10} {len(items)}")

            if "instance" in plugin:
                health = plugin["instance"].health()
                print(f"  status     {health['status']}")
                print(f"  version    {health['version']}")

if __name__ == "__main__":
    pm = PluginManager()
    pm.discover()
    pm.summary()
