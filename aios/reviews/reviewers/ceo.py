from ..models import ReviewResult


class CEOReviewer:


    def review(
        self,
        objective_analysis,
    ):

        findings = []


        if not objective_analysis.objective:

            findings.append(
                "Objective missing"
            )


        decision = (
            "rejected"
            if findings
            else "approved"
        )


        return ReviewResult(
            reviewer="CEO",
            decision=decision,
            findings=findings,
            recommendations=[
                "Confirm strategic alignment"
            ],
        )
