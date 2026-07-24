class AlternativeGenerator:


    def generate(
        self,
        objective_analysis,
    ):

        objective = (
            objective_analysis.objective
        )


        return [
            {
                "approach":
                    "Incremental",

                "description":
                    f"Build the smallest validated version of {objective}",

                "risk":
                    "Lower",
            },

            {
                "approach":
                    "Full System",

                "description":
                    f"Implement complete architecture for {objective}",

                "risk":
                    "Higher",
            },

            {
                "approach":
                    "Research First",

                "description":
                    "Analyze requirements before implementation",

                "risk":
                    "Lower uncertainty",
            },
        ]
