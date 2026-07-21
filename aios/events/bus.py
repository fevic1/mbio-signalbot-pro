class EventBus:

    def __init__(self):

        self.subscribers = {}

        self.history = []


    def subscribe(
        self,
        event_type,
        callback,
    ):

        if event_type not in self.subscribers:

            self.subscribers[event_type] = []


        self.subscribers[event_type].append(
            callback
        )

        return True


    def publish(
        self,
        event,
    ):

        record = {
            "event": event.to_dict()
        }


        self.history.append(
            record
        )


        listeners = self.subscribers.get(
            event.type,
            []
        )


        for callback in listeners:

            callback(event)


        return record


    def get_history(self):

        return self.history


    def clear_history(self):

        self.history.clear()

        return True
