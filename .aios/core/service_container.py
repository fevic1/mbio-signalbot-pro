#!/usr/bin/env python3

class ServiceContainer:
    def __init__(self):
        self._services = {}

    def register(self, name, service):
        if name in self._services:
            raise ValueError(f"Service '{name}' already registered")
        self._services[name] = service

    def get(self, name):
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found")
        return self._services[name]

    def has(self, name):
        return name in self._services

    def unregister(self, name):
        self._services.pop(name, None)

    def list(self):
        return sorted(self._services.keys())


services = ServiceContainer()


if __name__ == "__main__":
    services.register("config", {"env": "dev"})
    services.register("logger", "logger-instance")

    print(services.list())
    print(services.get("config"))
