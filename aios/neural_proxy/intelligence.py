from aios.providers.metrics import metrics


class ModelIntelligence:


    def __init__(self):

        self.profiles = {}


    def register(
        self,
        model,
        profile,
    ):

        self.profiles[model] = profile


    def profile(
        self,
        model,
    ):

        return self.profiles.get(
            model,
            {}
        )


    def rank(
        self,
        models,
        requirement=None,
    ):

        requirement = requirement or {}

        def score(model):

            profile = self.profile(
                model.name
            )

            value = 0


            if requirement.get(
                "fast"
            ):

                if profile.get(
                    "speed"
                ) == "fast":

                    value += 20


            if requirement.get(
                "cheap"
            ):

                if profile.get(
                    "cost"
                ) == "low":

                    value += 20


            if requirement.get(
                "quality"
            ):

                if profile.get(
                    "quality"
                ) == "high":

                    value += 20


            provider_name = getattr(
                model,
                "provider",
                None,
            )

            if provider_name:

                telemetry = metrics.get(
                    provider_name
                )

                if telemetry.successes:

                    value += (
                        telemetry.successes
                        * 2
                    )

                if telemetry.failures:

                    value -= (
                        telemetry.failures
                        * 5
                    )

                if telemetry.latency():

                    value -= min(
                        telemetry.latency(),
                        10,
                    )


            value += profile.get(
                "score",
                0,
            )

            return value


        return sorted(
            models,
            key=score,
            reverse=True,
        )
