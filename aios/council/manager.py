from .validator import Validator
from .critic import Critic
from .auditor import Auditor
from .policy import PolicyEngine
from .consensus import Consensus
from .memory import CouncilMemory


class CouncilManager:

    def __init__(self):
        self.validator = Validator()
        self.critic = Critic()
        self.auditor = Auditor()
        self.policy = PolicyEngine()
        self.consensus = Consensus()
        self.memory = CouncilMemory()

    def review(self, proposal):

        report = {
            "validator": self.validator.review(proposal),
            "critic": self.critic.review(proposal),
            "policy": self.policy.review(proposal),
        }

        report["consensus"] = self.consensus.vote(report)

        self.memory.store(report)

        return report

    def audit(self, execution):

        return self.auditor.audit(execution)
