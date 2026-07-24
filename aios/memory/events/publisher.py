from aios.events import AIOSDomainEvent


class MemoryEventPublisher:


    def __init__(
        self,
        event_bus,
    ):

        self.event_bus = event_bus



    def created(
        self,
        memory,
    ):

        return self.event_bus.publish(
            AIOSDomainEvent(

                event_type=
                "memory.created",

                source=
                "aios_memory",

                payload={
                    "memory":
                    memory.describe()
                    if hasattr(
                        memory,
                        "describe"
                    )
                    else str(memory)
                },
            )
        )



    def updated(
        self,
        memory,
    ):

        return self.event_bus.publish(
            AIOSDomainEvent(

                event_type=
                "memory.updated",

                source=
                "aios_memory",

                payload={
                    "memory":
                    memory.describe()
                    if hasattr(
                        memory,
                        "describe"
                    )
                    else str(memory)
                },
            )
        )
