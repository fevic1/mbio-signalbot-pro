from dataclasses import dataclass


@dataclass(slots=True)
class VerificationResult:
    passed: bool
    score: float
    report: dict


class VerificationEngine:

    def verify(self, response):

        score = 1.0 if response.content else 0.0

        return VerificationResult(
            passed=score >= 0.5,
            score=score,
            report={
                "content_present": bool(response.content),
            },
        )
