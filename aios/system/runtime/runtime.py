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

        from aios.runtime.events import (
            RuntimeEventPublisher,
        )

        self.runtime_events = RuntimeEventPublisher(
            event_bus
        )

        from aios.runtime.worker import (
            RuntimeWorker,
        )

        runtime_daemon = container.get(
            "runtime_daemon"
        )

        self.worker = (
            RuntimeWorker(
                runtime_daemon
            )
            if runtime_daemon
            else None
        )



    def start(self):

        from aios.system.startup import (
            StartupValidator,
        )


        validation = StartupValidator().validate(
            self.container
        )


        if not validation["ready"]:

            raise RuntimeError(
                {
                    "startup_failed":
                    validation
                }
            )


        state = self.lifecycle.start()

        self.runtime_events.started(
            {
                "state":
                state.describe()
            }
        )

        if self.worker:

            self.worker.start()

        return state



    def shutdown(self):

        if self.worker:

            self.worker.stop()

        self.runtime_events.stopped(
            {
                "service":
                "aios_runtime"
            }
        )

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
