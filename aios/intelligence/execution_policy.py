class ExecutionPolicy:

    def evaluate(
        self,
        context,
    ):

        verification = context.get(
            "verification",
            {},
        )

        return {
            "allowed": verification.get(
                "passed",
                True,
            ),
            "mode": (
                "automatic"
                if verification.get(
                    "passed",
                    True,
                )
                else "manual"
            ),
        }
