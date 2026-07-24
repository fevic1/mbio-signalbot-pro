class PlannerLessonAnalyzer:


    def analyze(
        self,
        memories,
    ):

        lessons = []


        for memory in memories:

            if (
                memory.get("type")
                ==
                "knowledge"
            ):

                lessons.extend(
                    memory["content"]
                    .get(
                        "lessons",
                        []
                    )
                )


            if (
                memory.get("type")
                ==
                "operational"
            ):

                issues = (
                    memory["content"]
                    .get(
                        "issues",
                        []
                    )
                )

                lessons.extend(
                    [
                        f"Prevent recurrence of: {issue}"
                        for issue in issues
                    ]
                )


        return lessons
