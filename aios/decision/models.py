from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class EvidenceRecord:
    source: str
    evidence: str
    confidence: float = 0.0


@dataclass
class RiskFlag:
    category: str
    severity: str
    description: str


@dataclass
class BiasReport:
    bias_type: str
    description: str
    severity: str = "medium"


@dataclass
class PolicyResult:
    allowed: bool
    issues: List[str] = field(default_factory=list)


@dataclass
class DecisionResult:

    proposal_id: str

    decision: str

    confidence: float

    policy: PolicyResult

    timestamp: str = field(
        default_factory=lambda:
            datetime.utcnow().isoformat()
    )

    approval_required: bool = False

    approval_id: Optional[str] = None

    approval_status: Optional[str] = None


    def to_dict(self):

        return {
            "proposal_id": self.proposal_id,
            "decision": self.decision,
            "confidence": self.confidence,

            "policy": {
                "allowed": self.policy.allowed,
                "issues": self.policy.issues,
            },

            "timestamp": self.timestamp,

            "approval_required":
                self.approval_required,

            "approval_id":
                self.approval_id,

            "approval_status":
                self.approval_status,
        }
