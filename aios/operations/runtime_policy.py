class RuntimePolicy:


    def __init__(
        self,
        production=True,
    ):

        self.production = production



    def validate(
        self,
        context,
    ):

        issues = []


        if self.production:

            if not context.get(
                "governance_enabled",
                False,
            ):

                issues.append(
                    "governance disabled"
                )


        return {

            "allowed":
                len(issues) == 0,

            "issues":
                issues,

        }
