from ..models import ReviewResult


class SecurityReviewer:


    def review(
        self,
        objective_analysis,
    ):

        return ReviewResult(
            reviewer="Security Auditor",
            decision="approved",
            findings=[
                "Security assessment required"
            ],
            recommendations=[
                "Review permissions and attack surface"
            ],
        )
