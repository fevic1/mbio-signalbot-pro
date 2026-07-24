class PlannerEventSubscriber:


    def __init__(
        self,
        feedback_engine,
    ):

        self.feedback_engine = feedback_engine



    def handle(
        self,
        event,
    ):

        memory = (
            event.payload
            .get(
                "memory",
                {}
            )
        )


        if isinstance(
            memory,
            str
        ):

            lesson = memory

        else:

            lesson = (
                memory.get(
                    "lesson",
                    ""
                )
            )


        if not lesson:

            return None


        return (
            self.feedback_engine
            .improve_plan(
                [],
                [
                    {
                        "type":
                        "knowledge",

                        "content":
                        {
                            "lessons":
                            [
                                lesson
                            ]
                        }
                    }
                ],
            )
        )
