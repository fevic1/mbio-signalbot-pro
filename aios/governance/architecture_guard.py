class ArchitectureGuard:


    def __init__(self):

        self.violations = []



    def validate(
        self,
        architecture,
    ):

        checks = [

            (
                "dependencies",
                architecture.get(
                    "dependencies"
                )
            ),

            (
                "documentation",
                architecture.get(
                    "documented"
                )
            ),

            (
                "validation",
                architecture.get(
                    "validated"
                )
            ),

        ]


        results = []


        for name, value in checks:

            passed = bool(value)

            result = {
                "check": name,
                "passed": passed,
            }


            results.append(
                result
            )


            if not passed:

                self.violations.append(
                    result
                )


        return {
            "passed":
                all(
                    r["passed"]
                    for r in results
                ),

            "results":
                results,
        }



    def report(
        self,
    ):

        return self.violations
