from ..models import ReviewResult


class ArchitectureReviewer:


    def review(
        self,
        objective_analysis,
    ):

        return ReviewResult(
            reviewer="Architect",
            decision="approved",
            findings=[
                "Architecture review required before implementation"
            ],
            recommendations=[
                "Define components and dependencies"
            ],
        )
