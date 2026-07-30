from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class GovernanceContext:
    version: str
    constitution: str
    security_rules: str
    reliability_rules: str

    constraints: List[str] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )
