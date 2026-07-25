class SkillRouter:


    def __init__(
        self,
        registry,
    ):

        self.registry = registry



    def route(
        self,
        request,
    ):

        matches = (
            self.registry.find(
                request
            )
        )


        if not matches:

            raise ValueError(
                f"No skill matches request: {request}"
            )


        return self.rank(
            matches
        )



    def rank(
        self,
        skills,
    ):

        return sorted(
            skills,
            key=lambda skill:
                len(
                    skill.quality_gates
                ),
            reverse=True,
        )
