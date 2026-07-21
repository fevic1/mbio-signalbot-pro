class ExecutionPlanner:

    def __init__(self):

        self.pipelines = {

            "research": [
                "ResearchAgent",
                "FundamentalAgent",
                "RiskAgent",
                "SkepticAgent",
                "VerificationAgent",
            ],

            "trading": [
                "ResearchAgent",
                "FundamentalAgent",
                "RiskAgent",
                "VerificationAgent",
            ],

            "engineering": [
                "ResearchAgent",
                "VerificationAgent",
            ],

            "security": [
                "ResearchAgent",
                "RiskAgent",
                "VerificationAgent",
            ],
        }

    def get_pipeline(
        self,
        category,
    ):

        return self.pipelines.get(
            category,
            ["ResearchAgent"],
        )

    def register_pipeline(
        self,
        category,
        pipeline,
    ):

        self.pipelines[category] = pipeline

        return True

    def list_pipelines(self):

        return self.pipelines
