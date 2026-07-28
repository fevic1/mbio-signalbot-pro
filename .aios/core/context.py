#!/usr/bin/env python3


class Context:

    def __init__(self, services, plugin=None):
        self.services = services
        self.plugin = plugin

    @property
    def config(self):
        return self.services.get("config")

    @property
    def logger(self):
        return self.services.get("logger")

    @property
    def event_bus(self):
        return self.services.get("event_bus")

    @property
    def memory(self):
        return self.services.get("memory")

    @property
    def knowledge(self):
        return self.services.get("knowledge")

    @property
    def permissions(self):
        return self.services.get("permissions")

    @property
    def scheduler(self):
        return self.services.get("scheduler")

    @property
    def llm(self):
        return self.services.get("llm")

    @property
    def runtime(self):
        return self.services.get("runtime")

    @property
    def lifecycle(self):
        return self.services.get("lifecycle")


    @property
    def hooks(self):
        return self.services.get("hooks")


    @property
    def pipeline(self):
        return self.services.get("pipeline")


    @property
    def router(self):
        return self.services.get("router")


    @property
    def command_bus(self):
        return self.services.get("command_bus")


    @property
    def query_bus(self):
        return self.services.get("query_bus")


    @property
    def event_store(self):
        return self.services.get("event_store")


    @property
    def state(self):
        return self.services.get("state")


    @property
    def registry(self):
        return self.services.get("registry")


    @property
    def health(self):
        return self.services.get("health")


    @property
    def resources(self):
        return self.services.get("resources")


    @property
    def metrics(self):
        return self.services.get("metrics")


    @property
    def manifest(self):
        return self.services.get("manifest")
