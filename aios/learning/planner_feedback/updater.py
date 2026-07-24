class PlannerFeedbackUpdater:


    def improve(
        self,
        plan,
        lessons,
    ):

        improved = list(
            plan
        )


        for lesson in lessons:

            improved.append(
                {
                    "name":
                    "Additional verification",

                    "description":
                    lesson,

                    "status":
                    "pending",
                }
            )


        return improved
