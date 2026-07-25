class SystemHealth:


    def __init__(
        self,
        checks,
    ):

        self.checks = checks



    def check(self):

        results = [

            check()

            for check in self.checks

        ]


        return {

            "healthy":
                all(
                    item.get(
                        "passed",
                        False
                    )
                    for item in results
                ),

            "checks":
                results,

        }
