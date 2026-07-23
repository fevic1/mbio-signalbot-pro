from dataclasses import dataclass, field
from typing import List


@dataclass
class CouncilIssue:
    code: str
    severity: str
    message: str


@dataclass
class AgentOpinion:
    agent: str
    confidence: float
    summary: str


@dataclass
class CouncilDecision:
    approved: bool
    confidence: float
    issues: List[CouncilIssue] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    opinions: List[AgentOpinion] = field(default_factory=list)
    voting: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "approved": self.approved,
            "confidence": self.confidence,
            "issues": [issue.__dict__ for issue in self.issues],
            "actions": self.actions,
            "opinions": [op.__dict__ for op in self.opinions],
            "voting": self.voting,
        }
