class ExecutionPlanner:


    def __init__(self):

        self.requirements = {

            "research": [
                "can_search",
                "can_reason",
                "can_verify",
            ],

            "trading": [
                "can_reason",
                "can_review",
                "can_verify",
            ],

            "engineering": [
                "can_plan",
                "can_execute",
                "can_verify",
            ],

            "security": [
                "can_review",
                "can_reason",
                "can_verify",
            ],
        }


    def get_capabilities(
        self,
        category,
    ):

        return self.requirements.get(
            category,
            [
                "can_reason"
            ],
        )


    def register_requirements(
        self,
        category,
        capabilities,
    ):

        self.requirements[
            category
        ] = capabilities


    def list_requirements(self):

        return self.requirements
