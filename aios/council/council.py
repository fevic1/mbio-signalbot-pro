from .models import CouncilDecision
from .validator import PlanValidator
from .hallucination import HallucinationGuard
from .debate import DebateEngine
from .voting import VotingEngine
from aios.events import Event


class Council:
    def __init__(
        self,
        event_bus=None,
    ):
        self.event_bus = event_bus
        self.validator = PlanValidator()
        self.guard = HallucinationGuard()
        self.debate = DebateEngine()
        self.voting = VotingEngine()

    def review(self, plan, text: str = ""):

        if self.event_bus:
            self.event_bus.publish(
                Event(
                    "council_started",
                    source="council",
                    payload={
                        "plan": plan,
                    },
                )
            )

        issues = []

        issues.extend(self.validator.validate(plan))
        issues.extend(self.guard.inspect(text))

        opinions = self.debate.collect(plan)

        vote = self.voting.decide(
            opinions,
            issues,
        )

        approved = vote.approved
        confidence = vote.confidence

        actions = []
        if not approved:
            actions.append("revise_plan")
            actions.append("request_additional_evidence")

        decision = CouncilDecision(
            approved=approved,
            confidence=confidence,
            issues=issues,
            actions=actions,
            opinions=opinions,
            voting={
                "quorum": vote.quorum,
                "votes": vote.votes,
            },
        )

        if self.event_bus:
            self.event_bus.publish(
                Event(
                    "council_decision",
                    source="council",
                    payload=decision.to_dict(),
                )
            )

        return decision

