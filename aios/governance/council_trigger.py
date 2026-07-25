class CouncilTrigger:


    def __init__(
        self,
        council,
    ):

        self.council = council



    def evaluate(
        self,
        issue,
    ):

        if not issue.requires_council():

            return {
                "action": "auto_fix",
                "issue": issue.describe(),
            }


        session = (
            self.council.create_session(
                issue.title
            )
        )


        self.council.assign_agents(
            session,
            [
                "architect",
                "risk",
                "skeptic",
                "verification",
            ]
        )


        return {
            "action": "council_review",
            "session": session,
        }
