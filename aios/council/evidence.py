class EvidenceEvaluator:


    def evaluate(
        self,
        report,
    ):

        responses = report.get(
            "responses",
            []
        )

        artifacts = report.get(
            "artifacts",
            []
        )


        # Backward compatibility:
        # support older reports that only
        # stored artifacts inside responses.

        if not artifacts:

            for item in responses:

                response = item.get(
                    "response",
                    {}
                )

                if isinstance(response, dict):

                    artifact = response.get(
                        "artifact"
                    )

                    if artifact:

                        artifacts.append(
                            artifact
                        )


                if "artifact" in item:

                    artifacts.append(
                        item["artifact"]
                    )


        score = 0


        if responses:

            score += 0.5


        if artifacts:

            score += 0.5


        return {

            "score": score,

            "responses":
                len(responses),

            "artifacts":
                len(artifacts),

            "valid":
                score >= 1.0,

        }
