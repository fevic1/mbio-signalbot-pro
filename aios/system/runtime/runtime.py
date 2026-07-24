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


        from aios.runtime.state import (
            RuntimeStateStore,
        )

        self.state_store = RuntimeStateStore()



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


        from aios.system.startup import (
            StartupHealthGate,
        )


        health = StartupHealthGate().check(
            self.container
        )


        if not health["ready"]:

            raise RuntimeError(
                {
                    "health_gate_failed":
                    health
                }
            )


        state = self.lifecycle.start()


        from aios.runtime.state import (
            RuntimeState,
        )

        self.state_store.save(
            RuntimeState(
                status="ready",
                pid=__import__(
                    "os"
                ).getpid(),
            )
        )


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


        from aios.runtime.state import (
            RuntimeState,
        )

        self.state_store.save(
            RuntimeState(
                status="stopped",
                pid=__import__(
                    "os"
                ).getpid(),
            )
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
