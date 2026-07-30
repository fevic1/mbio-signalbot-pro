from dataclasses import dataclass
from enum import Enum


class PolicySeverity(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"
    AUDIT = "AUDIT"


@dataclass(slots=True)
class PolicyResult:
    allowed: bool
    policy: str
    severity: PolicySeverity = PolicySeverity.ALLOW
    reason: str = ""
