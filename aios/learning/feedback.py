class FeedbackAnalyzer:


    def analyze(
        self,
        result,
    ):

        confidence = result.get(
            "confidence",
            0,
        )


        issues = result.get(
            "issues",
            [],
        )


        recommendations = []


        quality = "acceptable"


        if confidence < 0.5:

            quality = "weak"

            recommendations.append(
                "Improve execution reliability"
            )


        if issues:

            quality = "needs_review"

            recommendations.append(
                "Investigate execution issues"
            )


        return {
            "agent": result.get(
                "agent"
            ),
            "quality": quality,
            "confidence": confidence,
            "issues": issues,
            "recommendations": recommendations,
        }
