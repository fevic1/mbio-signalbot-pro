from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class EvidenceRecord:

    source: str

    claim: str

    verified: bool = False

    confidence: float = 0.0

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

    detected: bool = False

    indicators: list = field(
        default_factory=list
    )

    score: float = 0.0


@dataclass
class DecisionResult:

    decision: str

    confidence: float

    proposal_id: str

    risk_level: str = "unknown"

    issues: list = field(
        default_factory=list
    )

    bias_report: BiasReport | None = None

    id: str = field(
        default_factory=lambda:
            str(uuid.uuid4())
    )

    created_at: str = field(
        default_factory=lambda:
            datetime.utcnow().isoformat()
    )


    def to_dict(self):

        return {

            "id": self.id,

            "decision": self.decision,

            "confidence": self.confidence,

            "proposal_id": self.proposal_id,

            "risk_level": self.risk_level,

            "issues": self.issues,

            "bias_report":
                self.bias_report.__dict__
                if self.bias_report
                else None,

            "created_at": self.created_at,

        }
