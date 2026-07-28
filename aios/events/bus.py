from aios.core.observable import Observable

from .models import AIOSDomainEvent


class EventBus(Observable):


    def __init__(self):

        self.handlers = {}

        self.history = []



    def subscribe(
        self,
        event_type,
        handler,
    ):

        self.handlers.setdefault(
            event_type,
            []
        ).append(
            handler
        )



    def publish(
        self,
        event,
    ):

        self.history.append(
            event
        )


        for handler in (
            self.handlers
            .get(
                event.event_type,
                []
            )
        ):

            handler(
                event
            )


        return event



    def get_history(
        self,
    ):

        return [
            event.describe()
            for event in self.history
        ]
