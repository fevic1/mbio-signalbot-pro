#!/usr/bin/env python3

from pathlib import Path
import yaml


class ManifestManager:

    def __init__(self):
        self.root = Path(".aios/plugins")

    def discover(self):

        manifests = {}

        for plugin in self.root.iterdir():

            if not plugin.is_dir():
                continue

            manifest = plugin / "manifest.yaml"

            if not manifest.exists():
                continue

            with manifest.open() as f:
                manifests[plugin.name] = yaml.safe_load(f)

        return manifests

    def get(self, plugin):
        return self.discover().get(plugin)

    def list(self):
        return sorted(self.discover())


manifest = ManifestManager()


if __name__ == "__main__":

    print(manifest.list())

    print(
        manifest.get(
            "superpowers"
        )
    )
