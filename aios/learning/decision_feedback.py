from dataclasses import dataclass


@dataclass
class DecisionFeedback:

    decision_id: str

    approved: bool

    governance_passed: bool

    failed_gates: list[str]

    agents: list[str]



    def describe(self):

        return {

            "decision_id":
                self.decision_id,

            "approved":
                self.approved,

            "governance_passed":
                self.governance_passed,

            "failed_gates":
                self.failed_gates,

            "agents":
                self.agents,

        }
