from .models import CouncilDecision
from .validator import PlanValidator
from .hallucination import HallucinationGuard
from .debate import DebateEngine
from .voting import VotingEngine


class Council:
    def __init__(self):
        self.validator = PlanValidator()
        self.guard = HallucinationGuard()
        self.debate = DebateEngine()
        self.voting = VotingEngine()

    def review(self, plan, text: str = ""):
        issues = []

        issues.extend(self.validator.validate(plan))
        issues.extend(self.guard.inspect(text))

        opinions = self.debate.collect(plan)

        approved, confidence = self.voting.decide(opinions, issues)

        actions = []
        if not approved:
            actions.append("revise_plan")
            actions.append("request_additional_evidence")

        return CouncilDecision(
            approved=approved,
            confidence=confidence,
            issues=issues,
            actions=actions,
            opinions=opinions,
        )

