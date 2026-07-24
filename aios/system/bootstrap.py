from .container import AIOSContainer

from aios.events import EventBus



class AIOSBootstrap:


    def __init__(self):

        self.container = AIOSContainer()



    def initialize(self):

        event_bus = EventBus()


        self.container.register(
            "event_bus",
            event_bus,
        )


        return self.container



    def describe(self):

        return self.container.describe()
