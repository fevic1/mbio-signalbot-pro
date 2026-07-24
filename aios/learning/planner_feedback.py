class PlannerFeedbackEngine:


    def __init__(
        self,
        knowledge_store,
    ):

        self.knowledge = knowledge_store



    def improve_plan(
        self,
        plan,
    ):

        lessons = (
            self.knowledge.search()
        )


        improvements = []


        for lesson in lessons:

            for item in lesson.get(
                "lessons",
                []
            ):

                improvements.append(
                    item["lesson"]
                )


        return {
            "original_plan": plan,
            "improvements": improvements,
            "recommended_changes":
                self._apply_rules(
                    plan,
                    improvements
                ),
        }



    def _apply_rules(
        self,
        plan,
        improvements,
    ):

        updated = list(plan)


        for improvement in improvements:

            if (
                "verification"
                in improvement.lower()
            ):

                updated.append(
                    {
                        "name":
                            "additional verification",
                        "status":
                            "pending",
                    }
                )


        return updated
