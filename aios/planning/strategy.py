class StrategyGenerator:


    def generate(
        self,
        objective,
    ):

        text = objective.lower()


        if any(
            word in text
            for word in [
                "build",
                "create",
                "develop",
            ]
        ):

            return (
                "Research, design, implement, "
                "validate, deploy, and improve."
            )


        return (
            "Analyze objective, execute plan, "
            "verify outcome, and improve."
        )
