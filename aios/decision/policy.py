class DecisionPolicy:

    def __init__(self):

        self.minimum_evidence_score = 0.7
        self.minimum_agents = 3
        self.minimum_confidence = 0.5


    def validate(
        self,
        deliberation,
    ):

        issues = []

        confidence = deliberation.get(
            "confidence",
            0
        )

        if confidence < self.minimum_confidence:

            issues.append(
                "Low confidence"
            )


        agents = deliberation.get(
            "agents",
            []
        )

        if len(agents) < self.minimum_agents:

            issues.append(
                "Insufficient agent diversity"
            )


        evaluation = deliberation.get(
            "evaluation",
            {}
        )


        evidence_score = evaluation.get(
            "score",
            0
        )


        if evidence_score < self.minimum_evidence_score:

            issues.append(
                "Weak evidence quality"
            )


        evaluation_issues = evaluation.get(
            "issues",
            []
        )


        for issue in evaluation_issues:

            if "verification" in issue.lower():

                issues.append(
                    "Verification failure detected"
                )


        agreement = deliberation.get(
            "agreement",
            False
        )


        if not agreement:

            issues.append(
                "Agent disagreement detected"
            )


        return {

            "allowed":
                len(issues) == 0,

            "issues":
                list(set(issues)),

            "risk_level":
                self._risk_level(
                    issues
                ),

        }


    def _risk_level(
        self,
        issues,
    ):

        count = len(issues)


        if count == 0:

            return "low"


        if count <= 2:

            return "medium"


        return "high"
