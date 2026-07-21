from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class EvidenceRecord:
    source: str
    evidence: str
    confidence: float = 0.0

    # backward compatibility
    claim: str = ""
    verified: bool = False

    timestamp: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )


@dataclass
class RiskFlag:
    category: str
    description: str
    severity: str = "medium"


@dataclass
class BiasReport:
    # new structure
    bias_type: str = ""
    description: str = ""
    severity: str = "medium"

    # backward compatibility
    detected: bool = False
    indicators: list = field(default_factory=list)
    score: float = 0.0


@dataclass
class PolicyResult:
    allowed: bool
    issues: List[str] = field(default_factory=list)


@dataclass
class DecisionResult:
    proposal_id: str
    decision: str
    confidence: float

    # new policy validation
    policy: Optional[PolicyResult] = None

    # backward-compatible audit fields
    risk_level: str = "unknown"
    issues: list = field(default_factory=list)
    bias_report: Optional[BiasReport] = None

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )

    timestamp: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    # preserve old naming
    created_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    approval_required: bool = False
    approval_id: Optional[str] = None
    approval_status: Optional[str] = None


    def to_dict(self):
        return {
            "id": self.id,

            "proposal_id": self.proposal_id,
            "decision": self.decision,
            "confidence": self.confidence,

            "risk_level": self.risk_level,
            "issues": self.issues,

            "bias_report":
                self.bias_report.__dict__
                if self.bias_report
                else None,

            "policy": {
                "allowed": self.policy.allowed,
                "issues": self.policy.issues,
            } if self.policy else None,

            "timestamp": self.timestamp,
            "created_at": self.created_at,

            "approval_required":
                self.approval_required,

            "approval_id":
                self.approval_id,

            "approval_status":
                self.approval_status,
        }
