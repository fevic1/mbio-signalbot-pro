from .container import AIOSContainer

from aios.events import EventBus



class AIOSBootstrap:


    def __init__(self):

        self.container = AIOSContainer()



    def initialize(self):

        from .services.registry import (
            AIOSServiceRegistry
        )


        registry = AIOSServiceRegistry()


        services = registry.build_core()


        for name, service in services.items():

            self.container.register(
                name,
                service
            )


        return self.container



    def describe(self):

        return self.container.describe()
