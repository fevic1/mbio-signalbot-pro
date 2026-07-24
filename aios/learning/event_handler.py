class LearningEventHandler:


    def __init__(
        self,
        event_bus,
        learning,
    ):

        self.learning = learning


        event_bus.subscribe(
            "execution.completed",
            self.handle,
        )



    def handle(
        self,
        event,
    ):

        payload = event.payload


        result = payload.get(
            "result"
        )


        if not result:

            return None


        return self.learning.process_execution(
            result
        )
