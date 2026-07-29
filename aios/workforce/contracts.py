from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime, timezone


@dataclass
class AgentTask:

    objective: str

    task: Dict

    context: Dict = field(
        default_factory=dict
    )

    permissions: Dict = field(
        default_factory=dict
    )

    previous_results: List[Dict] = field(
        default_factory=list
    )



@dataclass
class AgentResult:

    agent: str

    status: str

    output: Dict = field(
        default_factory=dict
    )

    evidence: List[str] = field(
        default_factory=list
    )

    confidence: float = 0.0

    issues: List[str] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )

    timestamp: str = field(
        default_factory=lambda:
        datetime.now(timezone.utc).isoformat()
    )


    def describe(self):

        return {
            "agent": self.agent,
            "status": self.status,
            "output": self.output,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
