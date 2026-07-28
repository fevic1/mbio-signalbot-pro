#!/usr/bin/env python3

import json
from pathlib import Path


class MemoryService:

    def __init__(self):
        self.root = Path(".aios/memory")
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, namespace):
        return self.root / f"{namespace}.json"

    def load(self, namespace):

        path = self._path(namespace)

        if not path.exists():
            return {}

        with path.open() as f:
            return json.load(f)

    def save(self, namespace, data):

        path = self._path(namespace)

        with path.open("w") as f:
            json.dump(data, f, indent=2)

    def get(self, namespace, key, default=None):
        data = self.load(namespace)
        return data.get(key, default)

    def set(self, namespace, key, value):
        data = self.load(namespace)
        data[key] = value
        self.save(namespace, data)

    def delete(self, namespace, key):
        data = self.load(namespace)

        if key in data:
            del data[key]
            self.save(namespace, data)

    def list(self):
        return sorted(
            p.stem
            for p in self.root.glob("*.json")
        )


memory = MemoryService()


if __name__ == "__main__":

    memory.set(
        "superpowers",
        "version",
        "1.0.0"
    )

    memory.set(
        "superpowers",
        "status",
        "healthy"
    )

    print(memory.get("superpowers", "version"))
    print(memory.load("superpowers"))
    print(memory.list())
