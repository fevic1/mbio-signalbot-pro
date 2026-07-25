class ImpactAnalyzer:


    def __init__(
        self,
        lower_is_better=None,
    ):

        self.lower_is_better = (
            lower_is_better
            or set()
        )



    def analyze(
        self,
        metrics_before,
        metrics_after,
    ):

        improvements = {}
        regressions = {}


        for key, before in metrics_before.items():

            after = metrics_after.get(
                key,
                before,
            )


            if key in self.lower_is_better:

                if after < before:

                    improvements[key] = (
                        before,
                        after,
                    )

                elif after > before:

                    regressions[key] = (
                        before,
                        after,
                    )


            else:

                if after > before:

                    improvements[key] = (
                        before,
                        after,
                    )

                elif after < before:

                    regressions[key] = (
                        before,
                        after,
                    )


        return {

            "improvements":
                improvements,

            "regressions":
                regressions,

            "improved":
                bool(improvements)
                and not bool(regressions),

        }
