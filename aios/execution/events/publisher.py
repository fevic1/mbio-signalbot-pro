from aios.core.events.publisher import EventPublisher
from aios.events import AIOSDomainEvent


class ExecutionEventPublisher:


    def __init__(
        self,
        event_bus,
    ):

        self.event_bus = event_bus



    def started(
        self,
        agent,
        task,
    ):

        event = AIOSDomainEvent(

            event_type=
            "execution.started",

            source=
            "aios_execution",

            payload={
                "agent":
                    getattr(
                        agent,
                        "name",
                        str(agent),
                    ),

                "task":
                    task,
            },
        )


        return self.event_bus.publish(
            event
        )



    def completed(
        self,
        agent,
        result,
    ):

        event = AIOSDomainEvent(

            event_type=
            "execution.completed",

            source=
            "aios_execution",

            payload={
                "agent":
                    getattr(
                        agent,
                        "name",
                        str(agent),
                    ),

                "result":
                    result,
            },
        )


        return self.event_bus.publish(
            event
        )
