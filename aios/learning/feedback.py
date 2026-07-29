from dataclasses import dataclass, field
from typing import List


@dataclass
class ExecutionFeedback:

    execution_id: str

    success: bool

    score: float

    observations: List[str] = field(
        default_factory=list
    )

    asset: str = ""

    strategy: str = ""

    signal: str = ""

    pnl: float = 0.0

    confidence: float = 0.0


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
