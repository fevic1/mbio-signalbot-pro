class QualityGate:


    def __init__(self):

        self.rules = []



    def register(
        self,
        rule,
    ):

        self.rules.append(
            rule
        )



    def evaluate(
        self,
        context,
    ):

        results = []


        for rule in self.rules:

            result = rule.check(
                context
            )

            results.append(
                result
            )


        return {
            "passed":
                all(
                    item.get(
                        "passed",
                        False
                    )
                    for item in results
                ),

            "results":
                results,
        }
