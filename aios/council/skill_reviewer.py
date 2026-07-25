class SkillReviewer:


    def __init__(
        self,
        council_manager,
    ):

        self.council = council_manager



    def review(
        self,
        skill,
    ):

        question = (
            f"Review AIOS skill proposal: "
            f"{skill.name}"
        )


        session = (
            self.council
            .create_session(
                question
            )
        )


        return session
