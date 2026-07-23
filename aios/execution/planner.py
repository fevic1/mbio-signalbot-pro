class ExecutionPlanner:

    def __init__(self):

        self.requirements = {

            "research": [
                "research",
                "reasoning",
                "verification",
                "risk_analysis",
            ],

            "trading": [
                "market_analysis",
                "risk_management",
                "verification",
            ],

            "engineering": [
                "architecture",
                "coding",
                "testing",
            ],

            "security": [
                "security_analysis",
                "risk_analysis",
                "verification",
            ],
        }


    def get_capabilities(
        self,
        category,
    ):

        return self.requirements.get(
            category,
            ["research"],
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
