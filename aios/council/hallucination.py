from .models import CouncilIssue


class HallucinationGuard:
    FORBIDDEN = [
        "guaranteed profit",
        "risk free",
        "cannot fail",
        "100% accurate",
    ]

    def inspect(self, text: str):
        text = (text or "").lower()
        issues = []

        for phrase in self.FORBIDDEN:
            if phrase in text:
                issues.append(CouncilIssue(
                    code="hallucination_claim",
                    severity="high",
                    message=f"Forbidden claim detected: {phrase}",
                ))

        return issues
