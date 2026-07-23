from dataclasses import dataclass


@dataclass
class VoteResult:

    approved: bool
    confidence: float
    quorum: bool
    votes: dict


class VotingEngine:

    def __init__(
        self,
        quorum=0.66,
    ):
        self.quorum = quorum

    def decide(
        self,
        opinions,
        issues,
    ):

        if not opinions:
            return VoteResult(
                approved=not issues,
                confidence=1.0 if not issues else 0.0,
                quorum=False,
                votes={},
            )

        total_weight = 0.0
        approval_weight = 0.0
        votes = {}

        for opinion in opinions:

            weight = getattr(
                opinion,
                "weight",
                1.0,
            )

            confidence = getattr(
                opinion,
                "confidence",
                0.0,
            )

            approved = getattr(
                opinion,
                "approved",
                False,
            )

            vote_weight = weight * confidence

            total_weight += weight

            if approved:
                approval_weight += vote_weight

            votes[opinion.agent] = {
                "approved": approved,
                "confidence": confidence,
                "weight": weight,
            }

        confidence = (
            approval_weight / total_weight
            if total_weight
            else 0.0
        )

        quorum_reached = (
            len(opinions) /
            max(len(opinions), 1)
            >= self.quorum
        )

        return VoteResult(
            approved=(
                quorum_reached
                and confidence >= self.quorum
                and not issues
            ),
            confidence=confidence,
            quorum=quorum_reached,
            votes=votes,
        )
