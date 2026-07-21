class DecisionEvaluator:

    def __init__(self):

        self.minimum_score = 0.7


    def evaluate(
        self,
        proposal,
    ):

        issues = []

        score = 1.0


        opinions = proposal.opinions


        if not opinions:

            return {
                "valid": False,
                "score": 0,
                "issues": [
                    "No agent opinions"
                ]
            }


        # Check verification agent

        for opinion in opinions:

            agent = opinion.get(
                "agent",
                ""
            )

            result = opinion.get(
                "opinion",
                {}
            )


            if agent == "VerificationAgent":

                if isinstance(result, dict):

                    if result.get(
                        "verified"
                    ) is False:

                        score -= 0.4

                        issues.append(
                            "Evidence verification failed"
                        )


        # Check confidence inflation

        confidence_average = sum(
            opinion.get(
                "confidence",
                0
            )
            for opinion in opinions
        ) / len(opinions)


        if confidence_average > 0.9:

            score -= 0.2

            issues.append(
                "Possible confidence bias"
            )


        # Clamp score

        score = max(
            0,
            round(score, 2)
        )


        return {

            "valid":
                score >= self.minimum_score,

            "score":
                score,

            "issues":
                issues,

        }
