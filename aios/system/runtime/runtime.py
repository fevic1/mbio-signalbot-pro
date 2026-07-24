from aios.system.lifecycle import (
    LifecycleManager,
)


class AIOSRuntime:


    def __init__(
        self,
        container,
    ):

        self.container = container

        event_bus = (
            container.get(
                "event_bus"
            )
        )


        from aios.system.lifecycle.events import (
            LifecycleEventPublisher,
        )


        publisher = LifecycleEventPublisher(
            event_bus
        )


        self.lifecycle = LifecycleManager(
            container,
            publisher,
        )



    def start(self):

        return self.lifecycle.start()



    def shutdown(self):

        return self.lifecycle.shutdown()



    def get(
        self,
        name,
    ):

        return self.container.get(
            name
        )



    def describe(self):

        return {
            "services":
                self.container.describe(),

            "state":
                self.lifecycle.status(),
        }
