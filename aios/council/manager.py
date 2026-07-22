from .validator import PlanValidator
from .critic import Critic
from .auditor import Auditor
from .policy import PolicyEngine
from .consensus import Consensus
from .memory import CouncilMemory


class CouncilManager:

    def __init__(self):

        self.validator = PlanValidator()
        self.critic = Critic()
        self.auditor = Auditor()
        self.policy = PolicyEngine()
        self.consensus = Consensus()
        self.memory = CouncilMemory()

    def review(self, plan):

        validation_issues = self.validator.validate(plan)

        validator = {
            "valid": len(validation_issues) == 0,
            "issues": validation_issues,
        }

        critic = self.critic.review(plan)

        policy = self.policy.review(plan)

        report = {
            "validator": validator,
            "critic": critic,
            "policy": policy,
        }

        report["consensus"] = self.consensus.vote(report)

        self.memory.store(report)

        return report

    def audit(self, execution):

        report = self.auditor.audit(execution)

        self.memory.store(report)

        return report
