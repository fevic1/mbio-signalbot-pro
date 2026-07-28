from dataclasses import dataclass


@dataclass(slots=True)
class PolicyResult:
    allowed: bool
    policy: str
    reason: str = ""
