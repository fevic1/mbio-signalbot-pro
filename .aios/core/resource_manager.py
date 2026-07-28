#!/usr/bin/env python3

from threading import RLock


class ResourceManager:

    def __init__(self):
        self._resources = {}
        self._lock = RLock()

    def register(self, name, resource):

        with self._lock:

            if name in self._resources:
                raise ValueError(f"Resource '{name}' already exists")

            self._resources[name] = resource

    def unregister(self, name):

        with self._lock:
            self._resources.pop(name, None)

    def get(self, name):

        with self._lock:
            return self._resources[name]

    def exists(self, name):

        with self._lock:
            return name in self._resources

    def list(self):

        with self._lock:
            return sorted(self._resources.keys())

    def stats(self):

        with self._lock:
            return {
                "count": len(self._resources),
                "resources": sorted(self._resources.keys())
            }


resources = ResourceManager()


if __name__ == "__main__":

    resources.register("database", object())
    resources.register("redis", object())

    print(resources.list())
    print(resources.stats())
