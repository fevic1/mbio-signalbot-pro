class DeploymentGuard:


    name = "deployment"



    def check(
        self,
        context,
    ):

        failures = []


        if not context.get(
            "rollback_available",
            False,
        ):

            failures.append(
                "rollback unavailable"
            )


        if not context.get(
            "approved",
            False,
        ):

            failures.append(
                "deployment not approved"
            )


        return {

            "guard":
                self.name,

            "passed":
                len(failures) == 0,

            "failures":
                failures,

        }
